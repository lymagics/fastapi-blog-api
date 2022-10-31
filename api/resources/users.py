from functools import wraps

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import errors, models, schemas
from ..database  import get_db

users = APIRouter(tags=["Users"])


def paginated_users(f):
    """If you decorate view with this, it will return paginated users response."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        limit = kwargs.get("limit", 10)
        offset = kwargs.get("offset", 0)
        res = f(*args, **kwargs)
        users = res.limit(limit).offset(offset).all()
        return {"users": users, "pagination": {"limit": limit, "offset": offset}}
    return wrapper


@users.post("/users", response_model=schemas.UserOut, status_code=201)
def create_user(data: schemas.UserIn, db: Session = Depends(get_db)):
    """Register a new user."""
    print(data)
    if not models.User.validate_username(data.username, db):
        raise errors.BadRequest("Username already in use.")
    if not models.User.validate_email(data.email, db):
        raise errors.BadRequest("Email already in use.")

    user = models.User(**data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user 


@users.get("/users/{username}", response_model=schemas.UserOut)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """Retrieve a user by username."""
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise errors.UserNotFound
    return user


@users.get("/users", response_model=schemas.UserPagination)
@paginated_users
def retrieve_all_users(db: Session = Depends(get_db), limit: int = 10, offset: int = 0):
    """Retrieve all users."""
    return models.User.select_all(db)


@users.get("/me", response_model=schemas.UserOut)
def get_current_user(current_user: models.User = Depends(models.User.verify_access_token)):
    """Retrieve the authenticated user."""
    return current_user


@users.put("/me", response_model=schemas.UserOut)
def update_user(data: schemas.UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(models.User.verify_access_token)):
    """Edit user information."""
    if data.username != current_user.username and not models.User.validate_username(data.username, db):
        raise errors.BadRequest("Username already in use.")
    if data.email != current_user.email and not models.User.validate_email(data.email, db):
        raise errors.BadRequest("Email already in use.")

    current_user.update(data.dict())
    db.commit()
    return current_user 
