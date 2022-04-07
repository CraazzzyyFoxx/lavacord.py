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

import asyncio
import typing as t
from datetime import datetime, timezone

import hikari
import tekore
from tekore.model import FullAlbum, FullPlaylist, SimpleTrack, PlaylistTrack

from .abc import Playlist, Track
from .enums import Icons
from .utils import _from_json

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
PT = t.TypeVar("PT", bound="Playlist")


class SearchableTrack(Track):
    _search_type: t.ClassVar[str]
    _icon: t.ClassVar[Icons]
    _color: t.ClassVar[hikari.Color]

    @classmethod
    async def search(
            cls: t.Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
            *,
            return_first: bool = True
    ) -> t.List[Track]:
        tracks = await node.get_tracks(cls,
                                       query=query,
                                       requester=requester,
                                       return_first=return_first
                                       )

        if tracks is not None:
            return tracks

    @property
    def embed(self) -> hikari.Embed:
        emb = hikari.Embed(color=self._color, timestamp=datetime.now(timezone.utc))
        emb.set_thumbnail(self.thumbnail)
        emb.description = self.title
        emb.add_field(name='Duration', value=str(self.length) if not self.is_stream else 'Infinity')
        emb.set_author(icon=self._icon, name='Track Added to Queue')
        return emb


class YouTubeTrack(SearchableTrack):
    """A track created using a search to YouTube."""

    _search_type = "ytsearch"
    _color = hikari.Color.from_hex_code("#ff0101")
    _icon = Icons.youtube

    @property
    def thumbnail(self) -> str:
        """The URL to the thumbnail of this video."""
        return f"https://img.youtube.com/vi/{self.identifier}/maxresdefault.jpg"


class YouTubeMusicTrack(SearchableTrack):
    """A track created using a search to YouTube Music."""

    _search_type = "ytmsearch"
    _color = hikari.Color.from_hex_code("#ff0101")
    _icon = Icons.youtubemusic

    @property
    def thumbnail(self) -> str:
        """The URL to the thumbnail of this video."""
        return f"https://i.ytimg.com/vi/{self.identifier}/maxresdefault.jpg"


class TwitchTrack(SearchableTrack):
    """A track created using a search to Twitch."""
    _search_type = ""
    _color = hikari.Color.from_hex_code("#9448ff")
    _icon = Icons.twitch


class SoundCloudTrack(SearchableTrack):
    """A track created using a search to SoundCloud."""

    _search_type = "scsearch"
    _color = hikari.Color.from_hex_code("#f08f16")
    _icon = Icons.soundcloud


class SpotifyTrack(YouTubeMusicTrack):
    """A track retrieved via YouTubeMusic with a Spotify URL/ID."""
    _color = hikari.Color.from_hex_code("#1ed760")
    _icon = Icons.spotify

    thumbnail_: str

    @property
    def thumbnail(self) -> str:
        return self.thumbnail_

    @property
    def uri(self):
        return f'https://open.spotify.com/track/{self.identifier}'

    @classmethod
    async def search(
            cls: t.Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
            *,
            return_first: bool = True
    ) -> t.List[Track]:
        track_: tekore.model.FullTrack = await node.spotify.track(query)
        artists = [artist.name for artist in track_.artists]
        return await node.get_tracks(cls,
                                     query=f'{track_.name} {", ".join(artists)}',
                                     requester=requester,
                                     payload={"identifier": track_.id, "thumbnail_": track_.album.images[0].url},
                                     return_first=return_first)


class YandexMusicTrack(YouTubeMusicTrack):
    _color = hikari.Color.from_hex_code("#f3d92f")
    _icon = Icons.yandexmusic

    thumbnail_: str

    @property
    def thumbnail(self) -> str:
        return self.thumbnail_

    @classmethod
    async def search(
            cls: t.Type[ST],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
            *,
            return_first: bool = True
    ) -> t.List[Track]:
        async with node._websocket.session.get(f"https://music.yandex.ru/handlers/track.jsx?track={query}") as resp:
            data = await resp.json(loads=_from_json)
        track_data = data["track"]
        version = track_data.get("version")
        query = f"{track_data['title']}"
        if version:
            query += f"({version})"

        artists = track_data.get("artists")
        artists = [artist.get("name") for artist in artists]
        query += f' {", ".join(artists)}'
        thumb: str = track_data.get("coverUri")
        thumb.replace()
        return await node.get_tracks(cls,
                                     query=query,
                                     requester=requester,
                                     payload={"thumbnail_": thumb},
                                     return_first=return_first)


class YouTubePlaylist(Playlist):
    _icon = Icons.youtube
    _color = hikari.Color.from_hex_code("#ff0101")

    @classmethod
    async def search(
            cls: t.Type[PT],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
    ) -> YouTubePlaylist:
        return await node.get_playlist(cls, YouTubeTrack, query, requester)


class YouTubeMusicPlaylist(Playlist):
    _icon = Icons.youtubemusic
    _color = hikari.Color.from_hex_code("#ff0101")

    @classmethod
    async def search(
            cls: t.Type[PT],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
    ) -> YouTubeMusicPlaylist:
        return await node.get_playlist(cls, YouTubeMusicTrack, query, requester)


class SpotifyAlbum(Playlist):
    _icon = Icons.spotify
    _color = hikari.Color.from_hex_code("#1ed760")

    uri: str

    @classmethod
    async def search(
            cls: t.Type[PT],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
    ) -> SpotifyAlbum:
        playlist: FullAlbum = await node.spotify.album(query)
        tracks = []

        async def func(spotify_track: SimpleTrack):
            artists = [artist.name for artist in spotify_track.artists]
            lavalink_track = await node.get_tracks(SpotifyTrack,
                                                   query=f'{spotify_track.name} {", ".join(artists)}',
                                                   requester=requester,
                                                   return_first=True,
                                                   payload={"identifier": spotify_track.id,
                                                            "thumbnail": spotify_track.preview_url}
                                                   )
            if lavalink_track is None:
                return

            tracks.append(lavalink_track)

        tasks = []

        for track in playlist.tracks.items:
            tasks.append(asyncio.create_task(func(track)))
        await asyncio.wait(tasks)

        return cls(tracks=tracks,
                   name=playlist.name,
                   selectedTrack=len(tracks),
                   uri=playlist.uri,
                   thumbnail=playlist.images[0].url,
                   requester=requester)


class SpotifyPlaylist(Playlist):
    _icon = Icons.spotify
    _color = hikari.Color.from_hex_code("#1ed760")

    uri: str

    @classmethod
    async def search(
            cls: t.Type[PT],
            query: str,
            requester: hikari.Snowflake,
            node: Node,
    ) -> SpotifyPlaylist:
        playlist: FullPlaylist = await node.spotify.playlist(query)
        tracks = []

        async def func(spotify_track: PlaylistTrack):
            artists = [artist.name for artist in spotify_track.track.artists]
            lavalink_track = await node.get_tracks(SpotifyTrack,
                                                   query=f'{spotify_track.track.name} {", ".join(artists)}',
                                                   requester=requester,
                                                   return_first=True,
                                                   payload={"identifier": spotify_track.track.id,
                                                            "thumbnail": spotify_track.track.album.images[0].url}
                                                   )
            if lavalink_track is None:
                return

            tracks.append(lavalink_track)

        tasks = []

        for track in playlist.tracks.items:
            tasks.append(asyncio.create_task(func(track)))
        await asyncio.wait(tasks)

        return cls(tracks=tracks,
                   name=playlist.name,
                   selectedTrack=len(tracks),
                   uri=playlist.uri,
                   thumbnail=playlist.images[0].url,
                   requester=requester)
