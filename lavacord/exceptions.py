from .enums import ErrorSeverity


class WavelinkError(Exception):
    """Base WaveLink Exception"""


class AuthorizationFailure(WavelinkError):
    """Exception raised when an invalid password is provided toa node."""


class LavalinkException(WavelinkError):
    """Exception raised when an error occurs talking to Lavalink."""


class LoadTrackError(LavalinkException):
    """Exception raised when an error occurred when loading a track."""

    def __init__(self, data):
        exception = data["exception"]
        self.severity: ErrorSeverity = ErrorSeverity[exception["severity"]]
        super().__init__(exception["message"])


class BuildTrackError(LavalinkException):
    """Exception raised when a track is failed to be decoded and re-built."""

    def __init__(self, data):
        super().__init__(data["error"])


class NodeOccupied(WavelinkError):
    """Exception raised when node identifiers conflict."""


class InvalidIDProvided(WavelinkError):
    """Exception raised when an invalid ID is passed somewhere in Wavelink."""


class ZeroConnectedNodes(WavelinkError):
    """Exception raised when an operation is attempted with nodes, when there are None connected."""


class NoMatchingNode(WavelinkError):
    """Exception raised when a Node is attempted to be retrieved with a incorrect identifier."""


class QueueException(WavelinkError):
    """Base WaveLink Queue exception."""

    pass


class QueueFull(QueueException):
    """Exception raised when attempting to add to a full Queue."""

    pass


class QueueEmpty(QueueException):
    """Exception raised when attempting to retrieve from an empty Queue."""

    pass


class QueueHistoryEmpty(QueueEmpty):
    pass


class FiltersError(Exception):
    """
    A error for all filters.
    Parameters
    ----------
    message: :class:`str`
        the error message
    """

    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self):
        """
        A error message.
        """
        return self._message


class PlayerException(Exception):
    """Base Player Exception"""
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class PlayerNotFound(PlayerException):
    def __init__(self):
        message = 'Player not found.'
        super().__init__(message)


class AlreadyConnected(PlayerException):
    def __init__(self, ctx):
        message = f'The bot is already in the voice channel. ({ctx.voice_client.channel.path}).'
        super().__init__(message)


class NoVoiceChannel(PlayerException):
    def __init__(self):
        message = 'You must be in a voice channel.'
        super().__init__(message)
