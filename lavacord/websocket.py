"""
MIT License

Copyright (c) 2019-2021 PythonistaGuild
Copyright (c) 2022-present CrazzzyyFoxx

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, TYPE_CHECKING, Optional

import aiohttp
import hikari

from .backoff import Backoff
from .events import *
from .stats import Stats, PlayerState
from .utils import _from_json, _to_json

if TYPE_CHECKING:
    from .pool import Node
    from .player import BasePlayer

__all__ = ("Websocket",)

logger: logging.Logger = logging.getLogger(__name__)


class Websocket:
    def __init__(self, *, node: Node):
        self.node: Node = node

        self.websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        self.listener: Optional[asyncio.Task] = None
        self.session: Optional[aiohttp.ClientSession] = None

    def is_connected(self) -> bool:
        return self.websocket is not None and not self.websocket.closed

    async def connect(self) -> None:
        credentials = self.node.credentials

        headers = {
            "Authorization": credentials.password,
            "User-Id": str(self.node.bot.get_me().id),
            "Client-Name": "Lavacord",
            'Resume-Key': credentials.resume_key
        }

        self.session = aiohttp.ClientSession(headers=headers)
        if self.is_connected():
            assert isinstance(self.websocket, aiohttp.ClientWebSocketResponse)
            await self.websocket.close(
                code=1006, message=b"Lavacord: Attempting reconnection."
            )

        try:
            self.websocket = await self.session.ws_connect(
                self.node.credentials.websocket_host,
                headers=headers,
                heartbeat=self.node.heartbeat
            )
        except Exception as error:
            if (
                    isinstance(error, aiohttp.WSServerHandshakeError)
                    and error.status == 401
            ):
                logger.error(f"\nAuthorization Failed for Node: {self.node}\n")
            else:
                logger.error(f"Connection Failure: {error}")

            return

        if self.listener is None:
            self.listener = asyncio.create_task(self.listen())

        if self.is_connected():
            await self.node.bot.dispatch(NodeReady(node=self.node))
            logger.info(f"Connection established...{self.node.__repr__()}")

            resume = {
                "op": "configureResuming",
                "key": f"{self.node.credentials.resume_key}",
                "timeout": 60
            }
            await self.send(resume)

    async def listen(self) -> None:
        backoff = Backoff(base=1, maximum_time=60, maximum_tries=None)

        while True:
            assert isinstance(self.websocket, aiohttp.ClientWebSocketResponse)
            msg = await self.websocket.receive()
            if msg.type is aiohttp.WSMsgType.CLOSED:
                logger.info(f"Websocket Closed: {msg.extra}")

                retry = backoff.calculate()

                logger.warning(f"\nRetrying connection in <{retry}> seconds...\n")

                await asyncio.sleep(retry)
                if not self.is_connected():
                    await self.connect()
            else:
                logger.debug(f"Received Payload:: <{msg.data}>")

                if msg.data == 1011:
                    logger.error('Internal Lavalink Error encountered. Terminating Lavacord without retries.'
                                 'Consider updating your Lavalink Server.')

                    self.listener.cancel()
                    return

                asyncio.create_task(self.process_data(msg.json(loads=_from_json)))

    async def process_data(self, data: Dict[str, Any]) -> None:
        op = data.pop("op")
        if not op:
            return

        if op == "stats":
            self.node.stats = Stats(data)
            return

        player = self.node.get_player(hikari.Snowflake(data.pop("guildId")))
        assert player is not None

        if op == 'event':
            event = self._get_event_payload(data, player)
            logger.debug(f'op: event:: {event}')

            await self.node.bot.dispatch(event)

        elif op == "playerUpdate":
            logger.debug(f"op: playerUpdate:: {data}")
            player.last_state = PlayerState(data.get("state"))

    def _get_event_payload(self, data: Dict[str, Any], player: BasePlayer) -> hikari.Event:
        name = data.pop('type')
        if name == "WebSocketClosedEvent":
            event = WebSocketClosedEvent(self.node.bot, data)
        else:
            if name == "TrackEndEvent":
                player._source = None
                event = TrackEndEvent(player=player,
                                      **data)

            elif name == "TrackStartEvent":
                event = TrackStartEvent(player=player,
                                        **data)

            elif name == "TrackExceptionEvent":
                event = TrackExceptionEvent(player=player,
                                            **data)
            else:
                event = TrackStuckEvent(player=player,
                                        **data)

        return event

    async def send(self, data: dict) -> None:
        if self.is_connected():
            assert isinstance(self.websocket, aiohttp.ClientWebSocketResponse)
            logger.debug(f"Sending Payload:: {data}")
            await self.websocket.send_str(_to_json(data))
