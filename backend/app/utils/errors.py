from fastapi import HTTPException, status


class AuthError(HTTPException):
    def __init__(
        self, detail="Authentication failed", status_code=status.HTTP_401_UNAUTHORIZED
    ):
        super().__init__(status_code=status_code, detail=detail)
