class WeheatControlException(Exception):
    """Base class for this library."""


class ApiException(WeheatControlException):
    def __init__(self, status: int, body: str = "") -> None:
        super().__init__(f"HTTP {status}: {body[:300]}")
        self.status = status
        self.body = body


class ProtectedSettingError(WeheatControlException, ValueError):
    """Raised when a write touches installer- or hardware-level configuration."""
