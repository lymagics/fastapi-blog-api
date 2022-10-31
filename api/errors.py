from fastapi import HTTPException


class UserNotFound(HTTPException):
    """404 User Not Found. Error type - custom."""
    def __init__(self, message: str = "User not found"):
        super().__init__(status_code=404, detail=message)


class PostNotFound(HTTPException):
    """404 Post Not Found. Error type - custom."""
    def __init__(self, message: str = "Post not found"):
        super().__init__(status_code=404, detail=message)


class FollowNotFound(HTTPException):
    """404 Follow Not Found. Error type - custom."""
    def __init__(self, message: str = "You are not following this user"):
        super().__init__(status_code=404, detail=message)


class Unauthorized(HTTPException):
    """401 Unauthorized. Error type - http."""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(status_code=401, detail=message)


class BadRequest(HTTPException):
    """400 Bad Request. Error type - http."""
    def __init__(self, message: str = "Bad Request"):
        super().__init__(status_code=400, detail=message)


class Forbidden(HTTPException):
    """403 Forbidden. Error type - http."""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(status_code=403, detail=message)


class Conflict(HTTPException):
    """409 Conflict. Error type - http."""
    def __init__(self, message: str = "Conflict"):
        super().__init__(status_code=409, detail=message)
