"""Centralised error definitions for the niche_analysis package."""


class NicheAnalysisError(Exception):
    """Base class for all custom errors in niche_analysis."""


class InvalidInputError(NicheAnalysisError):
    """Raised when a user passes invalid data or types to an analysis function."""


class DataNotFoundError(NicheAnalysisError):
    """Raised when requested data cannot be found in internal knowledge bases."""


class ScoringError(NicheAnalysisError):
    """Raised when an error occurs during opportunity scoring."""
