class AppError(Exception):
    """Base exception for backend application errors."""


class ConfigurationError(AppError):
    """Raised when the backend configuration is invalid."""

