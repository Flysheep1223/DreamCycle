"""Judge-specific errors that preserve the raw model response for debugging."""


class JudgeValidationError(ValueError):
    def __init__(self, message: str, raw: dict):
        super().__init__(message)
        self.raw = raw
