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

from .abc import Track, PlayerUpdate
from .backoff import Backoff
from .events import *
from .stats import Stats

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

        self.host: str = f'{"https://" if self.node._https else "http://"}{self.node.host}:{self.node.port}'
        self.ws_host: str = f"ws://{self.node.host}:{self.node.port}"

    @property
    def headers(self) -> Dict[str, Any]:
        return {
            "Authorization": self.node.password,
            "User-Id": str(self.node.bot.get_me().id),
            "Client-Name": "Lavacord",
            'Resume-Key': self.node.resume_key
        }

    def is_connected(self) -> bool:
        return self.websocket is not None and not self.websocket.closed

    async def connect(self) -> None:
        self.session = aiohttp.ClientSession(headers=self.headers)
        if self.is_connected():
            assert isinstance(self.websocket, aiohttp.ClientWebSocketResponse)
            await self.websocket.close(
                code=1006, message=b"Lavacord: Attempting reconnection."
            )

        host = self.host if self.node._https else self.ws_host
        try:
            self.websocket = await self.session.ws_connect(
                host, headers=self.headers, heartbeat=self.node._heartbeat
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
            self.dispatch(NodeReady(node=self.node))
            logger.info(f"Connection established...{self.node.__repr__()}")

            resume = {
                "op": "configureResuming",
                "key": f"{self.node.resume_key}",
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

                asyncio.create_task(self.process_data(msg.json()))

    async def process_data(self, data: Dict[str, Any]) -> None:
        op = data.pop("op")
        if not op:
            return

        if op == "stats":
            self.node.stats = Stats(self.node, data)
            return

        player = self.node.get_player(hikari.Snowflake(self.node.bot.cache.get_guild(data["guildId"])))

        if player is None:
            return

        if op == 'event':
            event = await self._get_event_payload(data, player)
            logger.debug(f'op: event:: {event}')

            self.dispatch(event)

        elif op == "playerUpdate":
            logger.debug(f"op: playerUpdate:: {data}")

            await player.update_state(PlayerUpdate(**data))

    async def _get_event_payload(self, data: Dict[str, Any], player: BasePlayer) -> hikari.Event:
        name = data.pop('type')
        if name == "WebSocketClosedEvent":
            event = WebSocketClosedEvent(**data)

        elif name == "TrackEndEvent":
            track = await self.node.build_track(cls=Track, identifier=data.pop('track'))
            player._source = None
            event = TrackEndEvent(track=track,
                                  player=player,
                                  **data)

        elif name == "TrackStartEvent":
            track = await self.node.build_track(cls=Track, identifier=data.pop('track'))
            event = TrackStartEvent(track=track,
                                    player=player,
                                    **data)

        elif name == "TrackExceptionEvent":
            track = await self.node.build_track(cls=Track, identifier=data.pop('track'))
            event = TrackExceptionEvent(track=track,
                                        player=player,
                                        **data)

        else:
            track = await self.node.build_track(cls=Track, identifier=data.pop('track'))
            event = TrackStuckEvent(track=track,
                                    player=player,
                                    **data)

        return event

    def dispatch(self, event) -> None:
        self.node.bot.dispatch(event)

    async def send(self, data: dict) -> None:
        if self.is_connected():
            assert isinstance(self.websocket, aiohttp.ClientWebSocketResponse)
            logger.debug(f"Sending Payload:: {data}")

            data_str = self.node._dumps(data)
            if isinstance(data_str, bytes):
                data_str = data_str.decode("utf-8")

            await self.websocket.send_str(data_str)
