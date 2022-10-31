from functools import wraps

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import errors, models, schemas
from ..database import get_db

posts = APIRouter(tags=["Posts"])


def paginated_posts(f):
    """If you decorate view with this, it will return paginated posts response."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        limit = kwargs.get("limit", 10)
        offset = kwargs.get("offset", 0)
        res = f(*args, **kwargs)
        posts = res.limit(limit).offset(offset).all()
        return {"posts": posts, "pagination": {"limit": limit, "offset": offset}} 
    return wrapper


@posts.post("/posts", response_model=schemas.PostOut, status_code=201)
def create_post(data: schemas.PostIn, db: Session = Depends(get_db), current_user: models.User = Depends(models.User.verify_access_token)):
    """Create a new post."""
    post = models.Post(author=current_user, **data.dict())
    db.add(post)
    db.commit()
    db.refresh(post)
    return post 


@posts.get("/posts/{post_id}", response_model=schemas.PostOut)
def retrieve_post_by_id(post_id: int, db: Session = Depends(get_db)):
    """Retrieve a post by id."""
    post = db.query(models.Post).filter(models.Post.post_id == post_id).first()
    if post is None:
        raise errors.PostNotFound
    return post 


@posts.get("/posts", response_model=schemas.PostPagination)
@paginated_posts
def retrieve_all_posts(db: Session = Depends(get_db), limit: int = 10, offset: int = 0):
    """Retrieve all posts."""
    return models.Post.select_all(db)


@posts.get("/users/{user_id}/posts", response_model=schemas.PostPagination)
@paginated_posts
def retrieve_all_user_posts(user_id: int, db: Session = Depends(get_db), limit: int = 10, offset: int = 0):
    """Retrieve all posts from a user."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise errors.UserNotFound
    return user.posts
    

@posts.put("/posts/{post_id}", response_model=schemas.PostOut)
def update_post(post_id: int, data: schemas.PostUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(models.User.verify_access_token)):
    """Edit a post."""
    post = db.query(models.Post).filter(models.Post.post_id == post_id).first()
    if post is None:
        raise errors.PostNotFound
    if post.author != current_user:
        raise errors.Forbidden
    post.update(data.dict())
    db.commit()
    return post


@posts.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(models.User.verify_access_token)):
    """Delete a post."""
    post = db.query(models.Post).filter(models.Post.post_id == post_id).first()
    if post is None:
        raise errors.PostNotFound
    if post.author != current_user:
        raise errors.Forbidden
    db.delete(post)
    db.commit()
    return {}
