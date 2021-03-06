"""
The MIT License (MIT)

Copyright (c) 2022 CrazzzyyFoxx

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

import asyncio
import typing as t

import hikari

from .exceptions import NoMatchingNode
from .player import BasePlayer
from .pool import Node, NodePool

__all__ = (
    "LavalinkClient",
)

BP = t.TypeVar("BP", bound=BasePlayer)


class LavalinkClient:
    """
    Represents a Lavalink client used to manage nodes and connections.
    """

    def __init__(self, bot: hikari.GatewayBot):
        self.bot = bot
        self.bot.subscribe(hikari.VoiceStateUpdateEvent, self._raw_voice_state_update)
        self.bot.subscribe(hikari.VoiceServerUpdateEvent, self._raw_voice_server_update)

    @staticmethod
    async def create_player(voice_state: hikari.VoiceState, cls=BasePlayer) -> BP:
        node = NodePool.get_node()
        player = await node.create_player(voice_state, cls)
        return player

    @staticmethod
    async def get_player(guild_id: hikari.Snowflake) -> t.Optional[BP]:
        for node in NodePool._nodes.values():
            player = node.get_player(guild_id)
            if player is not None:
                return player

        return None

    async def _raw_voice_state_update(self, event: hikari.VoiceStateUpdateEvent) -> None:
        """
        A voice state update has been received from Discord.
        """
        if event.state.user_id != self.bot.get_me().id:
            return

        guild_id = event.guild_id
        player = await self.get_player(guild_id)

        if player:
            player.voice_channel_id = event.state.channel_id
            player.session_id = event.state.session_id

    async def _raw_voice_server_update(self, event: hikari.VoiceServerUpdateEvent) -> None:
        """
        A voice server update has been received from Discord.
        """
        guild_id = event.guild_id

        player = await self.get_player(guild_id)
        if not player:
            return
        await player.node._websocket.send({
            "op": "voiceUpdate",
            "guildId": str(guild_id),
            "sessionId": player.session_id,
            "event": {
                "token": event.token,
                "guild_id": str(guild_id),
                "endpoint": event.raw_endpoint
            }
        })

    async def wait_for_connection(self, guild_id: hikari.Snowflake) -> t.Optional[Node]:
        """
        Wait for the voice connection to be established.

        Parameters
        ---------
        guild_id: :class:`hikari.Snowflake`
            guild id for server
        """
        while not (await self.get_player(guild_id)):
            await asyncio.sleep(0.1)
        return await self.get_player(guild_id)

    async def wait_for_remove_connection(self, guild_id: hikari.Snowflake) -> None:
        """
        Wait for the voice connection to be removed.

        Parameters
        ---------
        guild_id: :class:`hikari.Snowflake`
            guild id for server

        Raises
        --------
        :exc:`.NoMatchingNode`
            If guild not found in nodes cache.
        """
        player = await self.get_player(guild_id)
        if not player:
            raise NoMatchingNode("Node not found", guild_id)
        while await self.get_player(guild_id):
            await asyncio.sleep(0.1)
