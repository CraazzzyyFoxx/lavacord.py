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

import abc
from datetime import timedelta, datetime, timezone
from typing import (
    List,
    Literal,
    Optional,
    TYPE_CHECKING,
    Type,
    TypeVar,
    Union,
    overload,
    ClassVar,
)

import hikari
from pydantic import BaseModel, Field, validator

from .enums import Icons

if TYPE_CHECKING:
    from .pool import Node

__all__ = (
    "Searchable",
    "Playlist",
    "Track",
    "PlayerUpdate",
    "PlayerState",
)

ST = TypeVar("ST", bound="Searchable")


class Track(BaseModel, abc.ABC):
    """A Lavalink track object."""

    id: str = Field(alias="track")

    title: str
    identifier: Optional[str] = Field(repr=False)
    uri: Optional[str] = Field(repr=False)
    is_seekable: bool = Field(alias="isSeekable", repr=False)
    author: Optional[str]
    is_stream: bool = Field(alias="isStream", repr=False)
    length: timedelta = Field(repr=False)
    source_mame: str = Field(alias="sourceName", repr=False)
    position: int = Field(repr=False)

    requester: hikari.Snowflake = Field(repr=False)

    @validator("position", pre=True)
    def parse_position(cls, value):
        return int(value)

    @validator("length", pre=True)
    def parse_length(cls, value):
        return timedelta(microseconds=value)

    def __str__(self):
        return f"[{self.title} - {self.author}]({self.uri}) \n" \
               f"({self.length if not self.is_stream else 'Infinity'}) " \
               f"Requester: <@{self.requester}>"

    @property
    @abc.abstractmethod
    def thumbnail(self):
        """Track thumbnail"""

    @property
    def duration(self) -> timedelta:
        return self.length


class Searchable(metaclass=abc.ABCMeta):
    @overload
    @classmethod
    @abc.abstractmethod
    async def search(
            cls: Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
            *,
            return_first: Literal[True] = ...
    ) -> Optional[ST]:
        ...

    @overload
    @classmethod
    @abc.abstractmethod
    async def search(
            cls: Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
            *,
            return_first: Literal[False] = ...
    ) -> List[ST]:
        ...

    @overload
    @classmethod
    @abc.abstractmethod
    async def search(
            cls: Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
            *,
            return_first: Literal[True] = ...
    ) -> Optional[ST]:
        ...

    @overload
    @classmethod
    @abc.abstractmethod
    async def search(
            cls: Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
            *,
            return_first: Literal[False] = ...
    ) -> List[ST]:
        ...

    @classmethod
    @abc.abstractmethod
    async def search(
            cls: Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
            *,
            return_first: bool = False
    ) -> Union[Optional[ST], List[ST]]:
        raise NotImplementedError


class Playlist(BaseModel):
    """An ABC that defines the basic structure of a lavalink playlist resource"""

    _icon: ClassVar[Icons]
    _color: ClassVar[hikari.Color]

    name: str
    track_count: int = Field(alias="selectedTrack")
    tracks: List[Track]
    requester: hikari.Snowflake

    @overload
    @classmethod
    async def search(
            cls: Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node = ...,
    ) -> Playlist:
        ...

    @classmethod
    async def search(
            cls: Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node = None,
    ) -> Playlist:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def thumbnail(self):
        """Playlist thumbnail"""

    @property
    def embed(self) -> hikari.Embed:
        emb = hikari.Embed(color=self._color, timestamp=datetime.now(timezone.utc))
        emb.description = self.name
        if self.thumbnail:
            emb.set_thumbnail(self.thumbnail)
        emb.add_field(name='Duration', value=str(sum([track.length for track in self.tracks])))
        emb.set_author(icon=self._icon, name='Playlist Added to Queue')
        return emb


class PlayerState(BaseModel):
    time: datetime
    position: timedelta
    connected: bool

    @validator("time", pre=True)
    def parse_time(cls, value):
        return datetime.fromtimestamp(value, tz=timezone.utc)

    @validator("position", pre=True)
    def parse_position(cls, value):
        return timedelta(microseconds=value)


class PlayerUpdate(BaseModel):
    guild_id: hikari.Snowflake = Field(alias="guildId")
    state: PlayerState
