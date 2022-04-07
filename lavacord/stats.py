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

import typing as t
from datetime import datetime, timezone, timedelta

import hikari

__all__ = (
    "Penalty",
    "Stats",
    "ConnectionInfo",
    "PlayerState",
    "PlayerUpdate"
)


class ConnectionInfo:
    """
    A Connection info just use to save the connection information.
    """

    __slots__ = ("guild_id", "session_id", "channel_id")

    def __init__(self,
                 guild_id: hikari.Snowflake,
                 channel_id: hikari.Snowflake,
                 *,
                 session_id: t.Optional[str] = None
                 ):
        self.guild_id = guild_id
        self.session_id = session_id
        self.channel_id = channel_id


class PlayerState:
    __slots__ = ("time", "position", "connected")

    def __init__(self, data: dict):
        self.time: datetime = datetime.fromtimestamp(data.get("time"), tz=timezone.utc)
        self.position: timedelta = timedelta(milliseconds=data.get("position"))
        self.connected: bool = data.get("connected")

    @classmethod
    def null(cls):
        self = cls.__new__(cls)
        self.time = datetime.fromtimestamp(0, tz=timezone.utc)
        self.position = timedelta(seconds=0)
        self.connected = False
        return self


class PlayerUpdate:
    __slots__ = ("guild_id", "state")

    def __init__(self, data: dict):
        self.guild_id: hikari.Snowflake = data.get("guildId")
        self.state = PlayerState(data)


class Penalty:
    __slots__ = ("player_penalty", "cpu_penalty", "null_frame_penalty", "deficit_frame_penalty", "total")

    def __init__(self, stats: Stats):
        self.player_penalty: int = stats.playing_players
        self.cpu_penalty: float = 1.05 ** (100 * stats.system_load) * 10 - 10
        self.null_frame_penalty: float = 0
        self.deficit_frame_penalty: float = 0

        if stats.frames_nulled != -1:
            self.null_frame_penalty = (
                                              1.03 ** (500 * (stats.frames_nulled / 3000))
            ) * 300 - 300
            self.null_frame_penalty *= 2

        if stats.frames_deficit != -1:
            self.deficit_frame_penalty = (
                1.03 ** (500 * (stats.frames_deficit / 3000))
            ) * 600 - 600

        self.total: float = (
            self.player_penalty
            + self.cpu_penalty
            + self.null_frame_penalty
            + self.deficit_frame_penalty
        )


class Stats:
    __slots__ = ("uptime",
                 "players",
                 "playing_players",
                 "memory_free",
                 "memory_used",
                 "memory_allocated",
                 "memory_reservable",
                 "cpu_cores",
                 "system_load",
                 "lavalink_load",
                 "frames_sent",
                 "frames_nulled",
                 "frames_deficit",
                 "penalty",
                 )

    def __init__(self, data: t.Dict[str, t.Any]):
        self.uptime: int = data["uptime"]

        self.players: int = data["players"]
        self.playing_players: int = data["playingPlayers"]

        memory: t.Dict[str, t.Any] = data["memory"]
        self.memory_free: int = memory["free"]
        self.memory_used: int = memory["used"]
        self.memory_allocated: int = memory["allocated"]
        self.memory_reservable: int = memory["reservable"]

        cpu: t.Dict[str, t.Any] = data["cpu"]
        self.cpu_cores: int = cpu["cores"]
        self.system_load: float = cpu["systemLoad"]
        self.lavalink_load: float = cpu["lavalinkLoad"]

        frame_stats: t.Dict[str, t.Any] = data.get("frameStats", {})
        self.frames_sent: int = frame_stats.get("sent", -1)
        self.frames_nulled: int = frame_stats.get("nulled", -1)
        self.frames_deficit: int = frame_stats.get("deficit", -1)
        self.penalty = Penalty(self)
