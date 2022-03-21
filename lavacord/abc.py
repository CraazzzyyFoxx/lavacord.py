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
    overload, ClassVar,
)

import hikari
import attr

from .enums import Icons

if TYPE_CHECKING:
    from .pool import Node

__all__ = (
    "Searchable",
    "Playlist",
    "Track",
)

ST = TypeVar("ST", bound="Searchable")


@attr.define(kw_only=True)
class Track:
    """A Lavalink track object.
    Attributes
    ------------
    id: str
        The Base64 Track ID, can be used to rebuild track objects.
    title: str
        The track title.
    identifier: Optional[str]
        The tracks' identifier. could be None depending on track type.
    length:
        The duration of the track in seconds.
    uri: Optional[str]
        The tracks URI. Could be None.
    author: Optional[str]
        The author of the track. Could be None
    requester: Union[hikari.Snowflake, None]
        The requester of the track. Could be None
    """

    track: str = attr.field(default=None)
    title: str = attr.field()
    identifier: Optional[str] = attr.field(default=None)
    uri: Optional[str] = attr.field()
    isSeekable: bool = attr.field()
    author: Optional[str] = attr.field()
    isStream: bool = attr.field()
    length: float = attr.field()
    sourceName: str = attr.field()
    position: str = attr.field()
    requester: Optional[hikari.Snowflake] = attr.field(default=None)

    def __repr__(self):
        return f"[{self.title} - {self.author}]({self.uri}) \n > " \
               f"({timedelta(milliseconds=self.length)}) Requester: <@{self.requester}>"


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


@attr.define(kw_only=True)
class Playlist(metaclass=abc.ABCMeta):
    """An ABC that defines the basic structure of a lavalink playlist resource"""

    _icon: ClassVar[Icons]
    _color: ClassVar[hikari.Color]

    name: str = attr.field()
    selected_tracks: int = attr.field()
    tracks: List[Track] = attr.field()

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
        return await node.get_playlist(cls, query, requester)

    @property
    def thumbnail(self):
        return NotImplemented

    @property
    def embed(self) -> hikari.Embed:
        emb = hikari.Embed(color=self._color, timestamp=datetime.now(timezone.utc))
        emb.description = self.name
        # emb.thumbnail = self.thumbnail
        emb.add_field(name='Duration',
                      value=str(timedelta(milliseconds=sum([track.length for track in self.tracks]))))
        emb.set_author(icon=self._icon, name='Playlist Added to Queue')
        return emb
