class AppError(Exception):
    """Base exception for backend application errors."""


class ConfigurationError(AppError):
    """Raised when the backend configuration is invalid."""


class ProviderError(AppError):
    """Base exception for provider integration errors."""

    code: str = "PROVIDER_ERROR"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ProviderUnavailableError(ProviderError):
    """Raised when a configured provider cannot be reached."""

    code = "PROVIDER_UNAVAILABLE"


class ModelNotFoundError(ProviderError):
    """Raised when the configured model is unavailable on the provider."""

    code = "MODEL_NOT_FOUND"


class RequestTimeoutError(ProviderError):
    """Raised when the provider request exceeds the configured timeout."""

    code = "REQUEST_TIMEOUT"

