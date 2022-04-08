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

from __future__ import annotations

import typing as t

import attrs
import hikari
from hikari.events.base_events import Event

from .abc import Track
from .enums import ErrorSeverity
from .player import BasePlayer

if t.TYPE_CHECKING:
    from .pool import Node

__all__ = ("NodeReady",
           "TrackStartEvent",
           "TrackEndEvent",
           "TrackExceptionEvent",
           "TrackStuckEvent",
           "WebSocketClosedEvent")

BP = t.TypeVar("BP", bound=BasePlayer)


@attrs.define(kw_only=True, weakref_slot=False)
class NodeReady(Event):
    node: Node = attrs.field()

    @property
    def app(self) -> hikari.traits.RESTAware:
        return self.node.bot


@attrs.define(kw_only=True, weakref_slot=False)
class BaseTrackEvent(Event):
    track: str = attrs.field()
    """The base64 track identifier"""

    player: BP = attrs.field()
    """The player in which the track is located"""

    @property
    def app(self) -> hikari.traits.RESTAware:
        return self.player.node.bot

    async def build_track(self) -> Track:
        return await self.player.node.build_track(Track, self.track)


@attrs.define(kw_only=True, weakref_slot=False)
class TrackStartEvent(BaseTrackEvent):
    """
    Event on track start.
    """


@attrs.define(kw_only=True, weakref_slot=False)
class TrackEndEvent(BaseTrackEvent):
    """
    Event on track end.
    """
    reason: str = attrs.field()


@attrs.define(kw_only=True, weakref_slot=False)
class TrackExceptionEvent(BaseTrackEvent):
    """
    Event on track exception.
    """

    exception: Exception = attrs.field()
    severity: ErrorSeverity = attrs.field(converter=ErrorSeverity)
    message: str = attrs.field()


@attrs.define(kw_only=True, weakref_slot=False)
class TrackStuckEvent(BaseTrackEvent):
    """
    Event on track stuck.
    """
    thresholdMs: str = attrs.field()

    @property
    def threshold(self):
        return self.thresholdMs


@attrs.define(kw_only=True, weakref_slot=False)
class WebSocketClosedEvent(hikari.Event):
    """
    Event on websocket closed.
    """
    guildId: hikari.Snowflake = attrs.field(converter=hikari.Snowflake)
    app: hikari.RESTAware = attrs.field()
    code: int = attrs.field()
    reason: str = attrs.field()
    byRemote: bool = attrs.field()

    @property
    def guild_id(self):
        return self.guildId

    @property
    def by_remote(self):
        return self.byRemote
