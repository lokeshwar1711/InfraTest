"""Domain exceptions for InfraTest."""


class InfraTestError(Exception):
    """Base error for controlled InfraTest failures."""


class ConfigLoadError(InfraTestError):
    """Raised when configuration cannot be loaded or validated."""


class ExecutionError(InfraTestError):
    """Raised when verification cannot proceed due to runtime issues."""


class ReportWriteError(InfraTestError):
    """Raised when InfraTest cannot write a requested report."""
