from __future__ import annotations

import typing as t

import attr
from hikari import Event

from .abc import Track
from .player import BasePlayer


if t.TYPE_CHECKING:
    from .pool import Node


__all__ = ("NodeReady",
           "TrackStartEvent",
           "TrackEndEvent",
           "ErrorEvent",
           "TrackExceptionEvent",
           "TrackStuckEvent",
           "PlayerUpdateEvent",
           "WebSocketClosedEvent")


@attr.define(kw_only=True)
class NodeReady(Event):
    app = attr.field(default=None)
    node: Node = attr.field()


@attr.define(kw_only=True)
class TrackStartEvent(Event):
    """
    Event on track start.
    """
    app = attr.field(default=None)
    track: Track = attr.field()
    guild_id: int = attr.field()
    player: BasePlayer = attr.field()


@attr.define(kw_only=True)
class TrackEndEvent(Event):
    """
    Event on track end.
    """
    app = attr.field(default=None)
    track: Track = attr.field()
    guild_id: int = attr.field()
    reason: str = attr.field()
    player: BasePlayer = attr.field()


@attr.define(kw_only=True)
class TrackExceptionEvent(Event):
    """
    Event on track exception.
    """
    app = attr.field(default=None)
    track: Track = attr.field()
    guild_id: int = attr.field()
    exception: str = attr.field()
    message: str = attr.field()
    severity: str = attr.field()
    cause: str = attr.field()
    player: BasePlayer = attr.field()


@attr.define(kw_only=True)
class TrackStuckEvent(Event):
    """
    Event on track stuck.
    """
    app = attr.field(default=None)
    track: Track = attr.field()
    guild_id: int = attr.field()
    thresholdMs: str = attr.field()
    player: BasePlayer = attr.field()


@attr.define(kw_only=True)
class WebSocketClosedEvent(Event):
    """
    Event on websocket closed.
    """
    app = attr.field(default=None)
    track: Track = attr.field()
    guild_id: int = attr.field()
    code: int = attr.field()
    reason: str = attr.field()
    byRemote: bool = attr.field()


@attr.define(kw_only=True)
class PlayerUpdateEvent(Event):
    """
    Event on player update.
    """
    app = attr.field(default=None)
    guild_id: int = attr.field()
    time: int = attr.field()
    position: t.Union[int, None] = attr.field()
    connected: bool = attr.field()


@attr.define(kw_only=True)
class ErrorEvent(Event):
    """
    Event on error.
    """
    app = attr.field(default=None)
    guild_id: int = attr.field()
    exception: Exception = attr.field()
