from __future__ import annotations

import typing as t

import attr
import hikari

if t.TYPE_CHECKING:
    from .pool import Node


__all__ = (
    "Penalty",
    "Stats",
    "ConnectionInfo"
)


@attr.define(kw_only=True)
class ConnectionInfo:
    """
    A info for Connection just use to save the connection information.
    """
    guild_id: hikari.Snowflake = attr.field()
    session_id: hikari.Snowflake = attr.field()
    channel_id: t.Optional[hikari.Snowflake] = attr.field(default=None)


class Penalty:
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
    def __init__(self, node: Node, data: t.Dict[str, t.Any]):
        self._node: Node = node

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
