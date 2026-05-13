class StationNotFoundError(Exception):
    """Raised when a station cannot be found for the requested identifier."""


class ServiceNotFoundError(Exception):
    """Raised when a service cannot be found for the requested identifier."""
