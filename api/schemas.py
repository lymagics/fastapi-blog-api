from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserIn(BaseModel):
    """Pydantic model to validate 'user' input data."""
    username: str 
    email: EmailStr 
    password: str
    about_me: Optional[str] = ""


class UserOut(BaseModel):
    """Pydantic model to validate 'user' output data."""
    user_id: int 
    username: str 
    about_me: Optional[str] = ""
    last_seen: datetime 
    member_since: datetime
    
    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    """Pydantic model to validate 'user' update data."""
    username: Optional[str]
    email: Optional[EmailStr]
    about_me: Optional[str]


class Pagination(BaseModel):
    """Pydantic model to validate 'pagination' query data."""
    limit: int 
    offset: int 


class UserPagination(BaseModel):
    """Pydantic model to validate 'user' pagination data."""
    users: list[UserOut]
    pagination: Pagination


class Token(BaseModel):
    """Pydantic model to validate 'token' data."""
    access_token: str 
    refresh_token: Optional[str]

    class Config:
        orm_mode = True


class Post(BaseModel):
    """Pydantic model to validate 'post' data."""
    title: str 
    content: str 


class PostIn(Post):
    """Pydantic model to validate 'post' input data."""
    pass 


class PostOut(Post):
    """Pydantic model to validate 'post' output data."""
    post_id: int 
    created_at: datetime
    author: UserOut

    class Config:
        orm_mode = True 


class PostUpdate(BaseModel):
    """Pydantic model to validate 'post' update data."""
    title: Optional[str]
    content: Optional[str]


class PostPagination(BaseModel):
    """Pydantic model to validate 'post' pagination data."""
    posts: list[PostOut]
    pagination: Pagination
