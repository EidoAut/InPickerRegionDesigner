
class InPickerError(Exception):
    """Base domain/application error."""

class ValidationError(InPickerError):
    """Raised when user input is invalid."""

class MissingDependencyError(InPickerError):
    """Raised when an optional dependency is required but unavailable."""
