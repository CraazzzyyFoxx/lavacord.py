from __future__ import annotations

from hikari.internal.enums import Enum

__all__ = (
    "RepeatMode",
    "ShuffleMode",
    "Icons",
    "ButtonEmojis",
    "SpotifySearchType",
    "LoadType",
    "ErrorSeverity"
)


class RepeatMode(str, Enum):
    OFF = "OFF"
    ONE = "ONE"
    ALL = "ALL"


class ShuffleMode(int, Enum):
    OFF = 0
    ON = 1


class SpotifySearchType(int, Enum):
    track = 0
    album = 1
    playlist = 2
    unusable = 3


class ErrorSeverity(str, Enum):
    common = "COMMON"
    suspicious = "SUSPICIOUS"
    fault = "FAULT"


class LoadType(str, Enum):
    track_loaded = "TRACK_LOADED"
    playlist_loaded = "PLAYLIST_LOADED"
    search_result = "SEARCH_RESULT"
    no_matches = "NO_MATCHES"
    load_failed = "LOAD_FAILED"


class Icons(str, Enum):
    spotify = "https://cdn.discordapp.com/emojis/908292227657240578.png"
    twitch = "https://cdn.discordapp.com/emojis/908292214067691573.png"
    youtube = "https://cdn.discordapp.com/emojis/908292349170446336.png"
    youtubemusic = "https://cdn.discordapp.com/emojis/908292237786497034.png"
    soundcloud = "https://cdn.discordapp.com/emojis/954864037596917850.png"


class ButtonEmojis(str, Enum):
    play = "<:play:910871207841251328>"
    pause = "<:pause:910871198433415208>"
    next = "<:next:910871169811492865>"
    previous = "<:previous:910871233422295080>"
    repeat = "<:repeat:910871225583149066>"
    audio = "<:audio:910871158814048316>"
    skipto = "<:skipto:911150565969518592>"
