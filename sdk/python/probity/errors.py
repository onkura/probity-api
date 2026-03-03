class ProbityError(Exception):
    """Base error for Probity SDK."""


class CanonicalizationError(ProbityError):
    pass


class HashingError(ProbityError):
    pass


class RecorderError(ProbityError):
    pass