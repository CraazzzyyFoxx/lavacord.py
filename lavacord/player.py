"""
MIT License

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

from __future__ import annotations

import datetime
import logging
import typing as t

import hikari
import yarl

from . import abc, Playlist
from .queue import Queue
from .stats import PlayerState
from .tracks import *

if t.TYPE_CHECKING:
    from .pool import Node, NodePool

__all__ = ("BasePlayer",
           "Player",
           )

logger: logging.Logger = logging.getLogger(__name__)


class BasePlayer:
    """Lavaplayer object."""

    def __init__(self,
                 guild_id: hikari.Snowflake,
                 channel_id: hikari.Snowflake,
                 *,
                 node: Node):
        self.last_state: PlayerState = PlayerState.null()

        self.voice_channel_id: hikari.Snowflake = channel_id
        self.guild_id: hikari.Snowflake = guild_id
        self.session_id: t.Optional[str] = None

        if not node:
            node = NodePool.get_node()
        self.node: Node = node

        self._connected: bool = False
        self.volume: float = 100
        self._paused: bool = False
        self._source: t.Optional[abc.Track] = None
        self.queue = Queue()

    @property
    def source(self) -> t.Optional[abc.Track]:
        """The currently playing audio source."""
        return self._source

    @property
    def position(self) -> datetime.timedelta:
        """The current seek position of the playing source in seconds. If nothing is playing this defaults to ``0``."""
        if not self.is_playing():
            return datetime.timedelta(seconds=0)

        if self.is_paused():
            return self.last_state.position

        return self.last_state.position

    def is_connected(self) -> bool:
        """Indicates whether the player is connected to voice."""
        return self._connected

    def is_playing(self) -> bool:
        """Indicates wether a track is currently being played."""
        return self.is_connected() and self._source is not None

    def is_paused(self) -> bool:
        """Indicates wether the currently playing track is paused."""
        return self._paused

    async def connect(self, *, self_deaf: bool = True) -> None:
        await self.node.bot.update_voice_state(self.guild_id,
                                               self.voice_channel_id,
                                               self_deaf=self_deaf)
        self._connected = True

        logger.info(f"Connected to voice channel:: {self.voice_channel_id}")

    async def disconnect(self) -> None:
        logger.info(f"Disconnected from voice channel:: {self.voice_channel_id}")

        await self.node.bot.update_voice_state(guild=self.guild_id, channel=None)
        self._connected = False

    async def move_to(self, channel: hikari.GuildVoiceChannel) -> None:
        """|coro|
        Moves the player to a different voice channel.
        Parameters
        -----------
        channel: :class:`hikari.GuildVoiceChannel`
            The channel to move to. Must be a voice channel.
        """
        await self.node.bot.update_voice_state(self.guild_id, channel.id)
        logger.info(f"Moving to voice channel:: {channel.id}")

    async def play(
            self, source: abc.Track, replace: bool = True, start: int = 0, end: int = 0
    ):
        """|coro|
        Play a Lavacord Track.
        Parameters
        ----------
        source: :class:`abc.Playable`
            The :class:`abc.Playable` to initiate playing.
        replace: bool
            Whether or not the current track, if there is one, should be replaced or not. Defaults to ``True``.
        start: int
            The position to start the player from in milliseconds. Defaults to ``0``.
        end: int
            The position to end the track on in milliseconds.
            By default this always allows the current song to finish playing.
        Returns
        -------
        :class:`lavacord.abc.Playable`
            The track that is now playing.
        """
        if replace or not self.is_playing():
            self._paused = False
        else:
            return

        payload = {
            "op": "play",
            "guildId": str(self.guild_id),
            "track": source.id,
            "noReplace": not replace,
            "startTime": str(start),
        }
        if end > 0:
            payload["endTime"] = str(end)

        await self.node._websocket.send(payload)

        logger.info(f"Started playing track:: {source.__repr__()} ({self.voice_channel_id})")

        self._source = source
        return source

    async def stop(self) -> None:
        """|coro|
        Stop the Player's currently playing song.
        """
        await self.node._websocket.send({
            "op": "stop", "guildId": str(self.guild_id)}
        )
        logger.info(f"Current track stopped:: {str(self.source)} ({self.voice_channel_id})")
        self._source = None

    async def set_pause(self, pause: bool) -> None:
        """|coro|
        Set the players paused state.
        Parameters
        ----------
        pause: bool
            A bool indicating if the player's paused state should be set to True or False.
        """
        await self.node._websocket.send(
            {"op": "pause", "guildId": str(self.guild_id), "pause": pause}
        )
        self._paused = pause
        logger.info(f"Set pause:: {self._paused} ({self.voice_channel_id})")

    async def pause(self) -> None:
        """|coro|
        Pauses the player if it was playing.
        """
        if not self._paused:
            await self.set_pause(True)

    async def resume(self) -> None:
        """|coro|
        Resumes the player if it was paused.
        """
        if self._paused:
            await self.set_pause(False)

    async def set_volume(self, volume: int) -> None:
        """|coro|
        Set the player's volume, between 0 and 1000.
        Parameters
        ----------
        volume: int
            The volume to set the player to.
        """
        self.volume = max(min(volume, 1000), 0)
        await self.node._websocket.send(
            {"op": "volume", "guildId": str(self.guild_id), "volume": self.volume}
        )
        logger.info(f"Set volume:: {self.volume} ({self.voice_channel_id})")

    async def seek(self, position: int = 0) -> None:
        """|coro|
        Seek to the given position in the song.
        Parameters
        ----------
        position: int
            The position as an int in milliseconds to seek to. Could be None to seek to beginning.
        """
        await self.node._websocket.send(
            dict(op="seek", guildId=str(self.guild_id), position=position)
        )

    async def destroy(self):
        """|coro|
               Destroy the player..
                """
        await self.node._websocket.send(
            {"op": "destroy", "guildId": str(self.guild_id)}
        )
        logger.info(f'Player destroyed:: {self.voice_channel_id}')
        self.node._players.pop(self.guild_id)
        await self.disconnect()


class Player(BasePlayer):
    async def search_tracks(self,
                            query: str,
                            member: hikari.Snowflake,
                            ) -> t.Optional[t.Union[SearchableTrack, Playlist]]:
        result = yarl.URL(query)
        if not result.host:
            data = await YouTubeTrack.search(query, member, self.node, return_first=True)
        else:
            query = str(result)
            if result.host in ("www.youtube.com", "youtube.com"):
                if result.query.get('list'):
                    data = await YouTubePlaylist.search(query, member, self.node)
                else:
                    data = await YouTubeTrack.search(query, member, self.node, return_first=True)
            elif result.host in ("www.music.youtube.com", "music.youtube.com"):
                if result.query.get('list'):
                    data = await YouTubeMusicPlaylist.search(query, member, self.node)
                else:
                    data = await YouTubeMusicTrack.search(query, member, self.node, return_first=True)
            elif result.host in ("open.spotify.com",):
                type_ = result.parts[-2]
                if type_ == "playlist":
                    data = await SpotifyPlaylist.search(result.parts[-1], member, self.node)
                elif type_ == "track":
                    data = await SpotifyTrack.search(result.parts[-1], member, self.node)
                elif type_ == "album":
                    data = await SpotifyAlbum.search(result.parts[-1], member, self.node)
                else:
                    return None

            elif result.host in ("www.twitch.tv",):
                data = await TwitchTrack.search(query, member, self.node)
            else:
                return

        return data
