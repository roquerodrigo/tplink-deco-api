from .base import DecoError


class ApiError(DecoError):
    def __init__(self, error_code: int):
        super().__init__(f"API returned error_code={error_code}")
        self.error_code = error_code
