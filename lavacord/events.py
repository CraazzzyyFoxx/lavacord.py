"""
The MIT License (MIT)

Copyright (c) 2022 CraazzzyyFoxx

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
import typing as t

import hikari
from pydantic import BaseModel, Field, validator

from .abc import Track
from .enums import ErrorSeverity
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

BP = t.TypeVar("BP", bound=BasePlayer)


class NodeReady(BaseModel, hikari.Event):
    node: Node

    @property
    def app(self) -> hikari.traits.RESTAware:
        return self.node.bot


class TrackStartEvent(BaseModel, hikari.Event):
    """
    Event on track start.
    """
    track: Track
    guild_id: hikari.Snowflake = Field(alias="guildId")
    player: BP

    @property
    def app(self) -> hikari.traits.RESTAware:
        return self.player.node.bot


class TrackEndEvent(BaseModel, hikari.Event):
    """
    Event on track end.
    """
    track: Track
    guild_id: hikari.Snowflake = Field(alias="guildId")
    reason: str
    player: BP

    @property
    def app(self) -> hikari.traits.RESTAware:
        return self.player.node.bot


class TrackExceptionEvent(BaseModel, hikari.Event):
    """
    Event on track exception.
    """
    track: Track
    guild_id: hikari.Snowflake = Field(alias="guildId")
    exception: str
    message: str
    severity: ErrorSeverity
    cause: str
    player: BP

    @property
    def app(self) -> hikari.traits.RESTAware:
        return self.player.node.bot


class TrackStuckEvent(BaseModel, hikari.Event):
    """
    Event on track stuck.
    """
    track: Track
    guild_id: hikari.Snowflake = Field(alias="guildId")
    thresholdMs: str
    player: BP

    @property
    def app(self) -> hikari.traits.RESTAware:
        return self.player.node.bot


class WebSocketClosedEvent(BaseModel, hikari.Event):
    """
    Event on websocket closed.
    """
    app: hikari.RESTAware
    track: Track
    guild_id: hikari.Snowflake
    code: int
    reason: str
    by_remote: bool = Field(alias="byRemote")


class PlayerUpdateEvent(BaseModel, hikari.Event):
    """
    Event on player update.
    """
    app: hikari.RESTAware
    track: Track
    guild_id: hikari.Snowflake
    time: datetime.datetime
    position: t.Optional[int]
    connected: bool

    @validator("time", pre=True)
    def parse_position(cls, value):
        return datetime.datetime.fromtimestamp(value)


class ErrorEvent(BaseModel, hikari.Event):
    """
    Event on error.
    """
    app: hikari.RESTAware
    guild_id: hikari.Snowflake
    exception: Exception
