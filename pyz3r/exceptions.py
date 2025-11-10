"""Custom exceptions for pyz3r library."""


class Pyz3rException(Exception):
    """Base exception for all pyz3r errors."""
    pass


class AlttprFailedToRetrieve(Pyz3rException):
    """Raised when unable to retrieve an ALTTPR game from the API."""
    pass


class AlttprFailedToGenerate(Pyz3rException):
    """Raised when unable to generate an ALTTPR game via the API."""
    pass


class UnableToRetrieve(Pyz3rException):
    """Raised when unable to retrieve data from a randomizer API."""
    pass


class UnableToGenerate(Pyz3rException):
    """Raised when unable to generate a game via a randomizer API."""
    pass