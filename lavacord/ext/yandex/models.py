from datetime import datetime
from typing import (
    Optional,
    List,
    Any,
)

from pydantic import BaseModel, Field


class Cover(BaseModel):
    type: str
    uri: str
    prefix: str


class Counts(BaseModel):
    tracks: int
    direct_albums: int = Field(alias="directAlbums")
    also_albums: int = Field(alias="alsoAlbums")
    also_tracks: int = Field(alias="alsoTracks")


class Ratings(BaseModel):
    week: int
    month: int
    day: int


class Link(BaseModel):
    title: str
    href: str
    type: str


class Label(BaseModel):
    id: int
    name: str


class R128(BaseModel):
    i: float
    tp: float


class TrackPosition(BaseModel):
    volume: int
    index: int


class LyricsInfo(BaseModel):
    has_sync: bool = Field(alias="hasAvailableSyncLyrics")
    has_text: bool = Field(alias="hasAvailableTextLyrics")


class Lyric(BaseModel):
    id: int
    lyrics: str
    full: str = Field(alias="fullLyrics")
    has_rights: bool = Field(alias="hasRights")
    show_translation: bool = Field(alias="showTranslation")


class Video(BaseModel):
    cover: str
    title: str
    embed_url: str = Field(alias="embedUrl")


class Pager(BaseModel):
    total: int
    page: int
    per_page: int = Field(alias="perPage")


class Artist(BaseModel):
    id: int
    error: Optional[str]
    reason: Optional[str]
    name: str
    cover: Optional[Cover]
    various: Optional[bool]
    composer: Optional[bool]
    genres: Optional[List[str]]
    og_image: Optional[str] = Field(alias="ogImage")
    counts: Optional[Counts]
    available: Optional[bool]
    ratings: Optional[Ratings]
    links: Optional[List[Link]]
    tickets_available: Optional[bool] = Field(alias="ticketsAvailable")


class Album(BaseModel):
    id: int
    title: str
    type: str  # TODO: Make enum
    meta_type: str = Field(alias="metaType")
    year: int
    release_date: datetime = Field(alias="releaseDate")
    cover_uri: str = Field(alias="coverUri")
    og_image: str = Field(alias="ogImage")
    genre: str
    buy: List[Any]
    track_count: int = Field(alias="trackCount")
    likes_count: int = Field(alias="likesCount")
    recent: bool
    very_important: bool = Field(alias="veryImportant")
    artists: List[Artist]
    labels: List[Label]
    available: bool
    available_for_premium_users: bool = Field(alias="availableForPremiumUsers")
    available_for_mobile: bool = Field(alias="availableForMobile")
    available_partially: bool = Field(alias="availablePartially")

    bests: List[int]

    track_position: Optional[TrackPosition]
    volumes: Optional[List['Track']]
    pager: Optional[Pager]

    redirected: Optional[bool]


class Track(BaseModel):
    id: int
    real_id: int = Field(alias="realId")
    title: str
    version: str
    major: Label
    available: bool
    available_for_premium_users: bool = Field(alias="availableForPremiumUsers")
    available_full_without_permissions: bool = Field(alias="availableFullWithoutPermissions")
    store_dir: str = Field(alias="storeDir")
    duration: int = Field(alias="DurationMs")
    file_size: int = Field(alias='fileSize')
    r128: R128
    preview_duration: int = Field(alias="previewDurationMs")
    artists: List[Artist]
    albums: List[Album]
    cover_uri: str = Field(alias="coverUri")
    og_image: str = Field(alias="ogImage")
    lyrics_available: bool = Field(alias="lyricsAvailable")
    type: str  # TODO: Make enum
    remember_position: bool = Field(alias="rememberPosition")
    track_sharing_flag: str = Field(alias="trackSharingFlag")  # TODO: Make enum
    lyrics_info: LyricsInfo

    best: Optional[bool]


class OtherVersions(BaseModel):
    another: List[Track]


class TrackAPI(BaseModel):
    counter: int
    artists: List[Artist]
    aliases: List[str]
    other_versions: OtherVersions = Field(alias="otherVersions")
    also_in_albums: List[Album] = Field(alias="alsoInAlbums")
    similar_tracks: List[Track] = Field(alias="similarTracks")
    track: Track
    lyric: Lyric
    episode_description: Optional[str] = Field(alias="episodeDescription")
    video: Video
    is_ugs_track: bool = Field(alias="isUgsTrack")
