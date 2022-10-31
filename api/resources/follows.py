from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import errors, models, schemas
from ..database import get_db
from .users import paginated_users

follows = APIRouter(tags=["Follows"])


@follows.post("/me/following/{user_id}", status_code=204)
def follow_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(models.User.verify_access_token)):
    """Follow a user."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise errors.UserNotFound
    if current_user.is_following(user):
        raise errors.Conflict("You already follow this user")
    current_user.follow(user)
    db.commit()
    return {} 


@follows.delete("/me/following/{user_id}", status_code=204)
def unfollow_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(models.User.verify_access_token)):
    """Unfollow a user."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise errors.UserNotFound
    if not current_user.is_following(user):
        raise errors.Conflict("You are not following this user")
    current_user.unfollow(user)
    db.commit()
    return {}


@follows.get("/me/following/{user_id}", status_code=204)
def check_me_following(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(models.User.verify_access_token)):
    """Check if a user is followed."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise errors.UserNotFound
    if not current_user.is_following(user):
        raise errors.FollowNotFound
    return {}


@follows.get("/me/following", response_model=schemas.UserPagination)
@paginated_users
def retrieve_me_following(current_user: models.User = Depends(models.User.verify_access_token), limit: int = 10, offset: int = 0):
    """Retrieve the users the logged in user is following."""
    return current_user.select_following()


@follows.get("/me/followers", response_model=schemas.UserPagination)
@paginated_users
def retrieve_my_followers(current_user: models.User = Depends(models.User.verify_access_token), limit: int = 10, offset: int = 0):
    """Retrieve the followers of the logged in user."""
    return current_user.select_followers()


@follows.get("/users/{user_id}/following", response_model=schemas.UserPagination)
@paginated_users
def retrieve_following(user_id: int, db: Session = Depends(get_db), limit: int = 10, offset: int = 0):
    """Retrieve the users this user is following."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise errors.UserNotFound
    return user.select_following()


@follows.get("/users/{user_id}/followers", response_model=schemas.UserPagination)
@paginated_users
def retrieve_followers(user_id: int, db: Session = Depends(get_db), limit: int = 10, offset: int = 0):
    """Retrieve the followers of the user."""
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if user is None:
        raise errors.UserNotFound
    return user.select_followers()
