from __future__ import annotations

import asyncio
import typing as t

from datetime import timedelta

import attr
import hikari
import tekore

from tekore._model import FullTrack, FullAlbum, FullPlaylist, SimpleTrack, PlaylistTrack

from airy.utils import utcnow

from .abc import Playlist, Track
from .enums import Icons

if t.TYPE_CHECKING:
    from .pool import Node

__all__ = (
    "SearchableTrack",
    "YouTubeTrack",
    "YouTubeMusicTrack",
    "SoundCloudTrack",
    "YouTubePlaylist",
    "SpotifyTrack",
    "YouTubeMusicPlaylist",
    "SpotifyPlaylist",
    "TwitchTrack",
    "SpotifyAlbum",
)

ST = t.TypeVar("ST", bound="SearchableTrack")


@attr.define(kw_only=True, repr=False)
class SearchableTrack(Track):
    _search_type: t.ClassVar[str]
    _icon: t.ClassVar[Icons]
    _color: t.ClassVar[hikari.Color]
    _spotify = False

    @property
    def thumbnail(self):
        raise NotImplemented

    @classmethod
    async def search(
            cls: t.Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node = None,
            *,
            return_first: bool = True
    ) -> t.List[Track]:
        tracks = await node.get_tracks(cls, query=query, requester=requester, return_first=return_first)

        if tracks is not None:
            return tracks



    @property
    def embed(self) -> hikari.Embed:
        emb = hikari.Embed(color=self._color, timestamp=utcnow())
        emb.set_thumbnail(self.thumbnail)
        emb.description = self.title
        emb.add_field(name='Duration', value=str(timedelta(milliseconds=self.length)))
        emb.set_author(icon=self._icon, name='Track Added to Queue')
        return emb


class YouTubeTrack(SearchableTrack):
    """A track created using a search to YouTube."""

    _search_type = "ytsearch"
    _color = hikari.Color.from_hex_code("#ff0101")
    _icon = Icons.youtube
    _spotify = False

    @property
    def thumbnail(self) -> str:
        """The URL to the thumbnail of this video."""
        return f"https://img.youtube.com/vi/{self.identifier}/maxresdefault.jpg"


class YouTubeMusicTrack(SearchableTrack):
    """A track created using a search to YouTube Music."""

    _search_type = "ytmsearch"
    _color = hikari.Color.from_hex_code("#ff0101")
    _icon = Icons.youtubemusic
    _spotify = False

    @property
    def thumbnail(self) -> str:
        """The URL to the thumbnail of this video."""
        return f"https://i.ytimg.com/vi/{self.identifier}/maxresdefault.jpg"


class TwitchTrack(SearchableTrack):
    """A track created using a search to Twitch."""
    _color = hikari.Color.from_hex_code("#9448ff")
    _icon = Icons.twitch
    _spotify = False


class SoundCloudTrack(SearchableTrack):
    """A track created using a search to SoundCloud."""

    _search_type = "scsearch"
    _color = hikari.Color.from_hex_code("#f08f16")
    _icon = Icons.soundcloud
    _spotify = False


@attr.define(kw_only=True, repr=False)
class SpotifyTrack(YouTubeMusicTrack):
    """A track retrieved via YouTubeMusic with a Spotify URL/ID."""
    _color = hikari.Color.from_hex_code("#1ed760")
    _icon = Icons.spotify
    _spotify = True

    spotify_info: FullTrack = attr.field()

    @property
    def uri(self):
        return f'https://open.spotify.com/track/{self.spotify_info.id}'

    @property
    def thumbnail(self) -> str:
        return self.spotify_info.album.images[0].url

    @classmethod
    async def search(
            cls: t.Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node = None,
            *,
            return_first: bool = True
    ) -> t.List[Track]:
        track_: tekore.model.FullTrack = await node.spotify.track(query)
        artists = [artist.name for artist in track_.artists]
        query = f'{track_.name} {", ".join(artists)}'
        return await node.get_tracks(cls, query, requester, payload=dict(spotify_info=track_),
                                     return_first=return_first)


@attr.define(kw_only=True, repr=False)
class YouTubePlaylist(Playlist):
    _icon = Icons.youtube
    _color = hikari.Color.from_hex_code("#ff0101")
    _spotify = False

    @property
    def thumbnail(self):
        return NotImplemented


@attr.define(kw_only=True, repr=False)
class YouTubeMusicPlaylist(Playlist):
    _icon = Icons.youtubemusic
    _color = hikari.Color.from_hex_code("#ff0101")
    _spotify = False


class SpotifyAlbum(Playlist):
    _icon = Icons.spotify
    _color = hikari.Color.from_hex_code("#1ed760")
    _spotify = True

    name: str = attr.field()
    uri: str = attr.field()
    thumbnail: str = attr.field()

    @classmethod
    async def search(
            cls: t.Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node = None,
    ) -> SpotifyAlbum:
        playlist: FullAlbum = await node.spotify.album(query)
        tracks = []

        async def func(track: SimpleTrack):
            artists = [artist.name for artist in track.artists]
            query = f'{track.name} {", ".join(artists)}'
            track_ = await node.get_tracks(SpotifyTrack,
                                           query=query,
                                           requester=requester,
                                           return_first=True,
                                           payload=dict(spotify_info=track))
            if track_ is None:
                return

            tracks.append(track_)

        tasks = []

        for track in playlist.tracks.items:
            tasks.append(asyncio.create_task(func(track)))
        await asyncio.wait(tasks)

        return cls(tracks=tracks,
                   name=playlist.name,
                   selected_tracks=len(tracks),
                   uri=playlist.uri,
                   thumbnail=playlist.images[0].url)


@attr.define(kw_only=True, repr=False)
class SpotifyPlaylist(Playlist):
    _icon = Icons.spotify
    _color = hikari.Color.from_hex_code("#1ed760")
    _spotify = False

    name: str = attr.field()
    uri: str = attr.field()
    thumbnail: str = attr.field()

    @classmethod
    async def search(
            cls: t.Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node = None,
    ) -> SpotifyAlbum:
        playlist: FullPlaylist = await node.spotify.playlist(query)
        tracks = []

        async def func(track: PlaylistTrack):
            artists = [artist.name for artist in track.track.artists]
            query = f'{track.track.name} {", ".join(artists)}'
            track_ = await node.get_tracks(SpotifyTrack,
                                           query=query,
                                           requester=requester,
                                           return_first=True,
                                           payload=dict(spotify_info=track))
            if track_ is None:
                return

            tracks.append(track_)

        tasks = []

        for track in playlist.tracks.items:
            tasks.append(asyncio.create_task(func(track)))
        await asyncio.wait(tasks)

        return cls(tracks=tracks,
                   name=playlist.name,
                   selected_tracks=len(tracks),
                   uri=playlist.uri,
                   thumbnail=playlist.images[0].url)
