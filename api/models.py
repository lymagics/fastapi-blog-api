from typing import Optional
from datetime import datetime, timedelta
import secrets

from fastapi import Cookie, Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

from . import errors, schemas
from .database import get_db, Base
from .security import check_password_hash, generate_password_hash
from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="tokens")


class Updatable:
    def update(self, data: dict):
        for attr, value in data.items():
            if value:
                setattr(self, attr, value)


followers = sqla.Table(
    "followers",
    Base.metadata,
    sqla.Column("followed_id", sqla.Integer, sqla.ForeignKey("users.user_id")),
    sqla.Column("follower_id", sqla.Integer, sqla.ForeignKey("users.user_id"))
)


class Token(Base):
    """SQLAlchemy model to represent 'tokens' table."""
    __tablename__ = "tokens"

    token_id = sqla.Column(sqla.Integer, primary_key=True)
    access_token = sqla.Column(sqla.String(64), nullable=False, index=True)
    access_expiration = sqla.Column(sqla.DateTime)
    refresh_token = sqla.Column(sqla.String(64), nullable=False, index=True)
    refresh_expiration = sqla.Column(sqla.DateTime)
    user_id = sqla.Column(sqla.Integer, sqla.ForeignKey("users.user_id"))

    def generate(self):
        """Generate access and refresh token pair."""
        self.access_token = secrets.token_urlsafe()
        self.access_expiration = datetime.utcnow() + \
            timedelta(minutes=settings.access_token_expire_minutes)
        self.refresh_token = secrets.token_urlsafe() 
        self.refresh_expiration = datetime.utcnow() + \
            timedelta(days=settings.refresh_token_expire_days)

    def expire(self):
        """Expire token."""
        self.access_expiration = datetime.utcnow()
        self.refresh_expiration = datetime.utcnow()

    @staticmethod
    def clean(db: sqla_orm.Session):
        """Revoke all tokens that expired for more than one day."""
        yesterday = datetime.utcnow() - timedelta(days=1)
        db.query(Token).filter(Token.refresh_expiration < yesterday).delete()


class Post(Updatable, Base):
    """SQLAlchemy model to represent 'posts' table."""
    __tablename__ = "posts"

    post_id = sqla.Column(sqla.Integer, primary_key=True)
    title = sqla.Column(sqla.String(50), nullable=False)
    content = sqla.Column(sqla.Text, nullable=False)
    created_at = sqla.Column(sqla.DateTime, default=datetime.utcnow)
    author_id = sqla.Column(sqla.Integer, sqla.ForeignKey("users.user_id"))

    @staticmethod
    def select_all(db: sqla_orm.Session):
        """Return query to retrieve all posts."""
        return db.query(Post)

    def __repr__(self):
        return f"<Post {self.title}>"


class User(Updatable, Base):
    """SQLAlchemy model to represent 'users' table."""
    __tablename__ = "users"

    user_id = sqla.Column(sqla.Integer, primary_key=True)
    username = sqla.Column(sqla.String(64), nullable=False, unique=True, index=True)
    email = sqla.Column(sqla.String(120), nullable=False, unique=True, index=True)
    password_hash = sqla.Column(sqla.String(128), nullable=False)
    about_me = sqla.Column(sqla.Text)
    last_seen = sqla.Column(sqla.DateTime, default=datetime.utcnow)
    member_since = sqla.Column(sqla.DateTime, default=datetime.utcnow)

    tokens = sqla_orm.relationship("Token", backref="user", cascade="all, delete", lazy="dynamic")
    posts = sqla_orm.relationship("Post", backref="author", cascade="all, delete", lazy="dynamic")

    following = sqla_orm.relationship(
        "User", secondary=followers,
        primaryjoin=(followers.c.follower_id == user_id),
        secondaryjoin=(followers.c.followed_id == user_id),
        backref=sqla_orm.backref("followers", lazy="dynamic"), lazy="dynamic")

    @property
    def password(self):
        """Password getter."""
        raise AttributeError("Can't read user password.")

    @password.setter
    def password(self, password: str):
        """Password setter."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify password."""
        return check_password_hash(self.password_hash, password)

    def ping(self):
        """Update user last seen."""
        self.last_seen = datetime.utcnow()

    def generate_access_token(self):
        """Generate access token."""
        token = Token(user=self)
        token.generate()
        return token

    @staticmethod
    def verify_access_token(access_token: str = Depends(oauth2_scheme), db: sqla_orm.Session = Depends(get_db)):
        """Verify access token and return user."""
        token = db.query(Token).filter(Token.access_token == access_token).first()
        if token:
            if token.access_expiration > datetime.utcnow():
                token.user.ping()
                return token.user 
        raise errors.Unauthorized

    @staticmethod
    def verify_refresh_token(token: schemas.Token, refresh_token: Optional[str] = Cookie(None), db: sqla_orm.Session = Depends(get_db)):
        """Verify refresh token and return token."""
        refresh_token = token.refresh_token or refresh_token 
        if not refresh_token:
            raise errors.BadRequest
        token = db.query(Token).filter(Token.refresh_token == refresh_token).first()
        if token:
            if token.refresh_expiration > datetime.utcnow():
                return token 
        raise errors.Unauthorized

    def is_following(self, user):
        """Check if curretn user follows user."""
        return self in user.followers

    def is_followed_by(self, user):
        """Check if current user is followed by user."""
        return self in user.following

    def follow(self, user):
        """Follow user."""
        if not self.is_following(user):
            user.followers.append(self)

    def unfollow(self, user):
        """Unfollow user."""
        if self.is_following(user):
            user.followers.remove(self)

    @staticmethod
    def select_all(db: sqla_orm.Session):
        """Return query to retrieve all users."""
        return db.query(User)

    def select_following(self):
        """Select all users current user follows."""
        return self.following

    def select_followers(self):
        """Select current user followers."""
        return self.followers

    @staticmethod
    def validate_username(username: str, db: sqla_orm.Session) -> bool:
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            return True 
        return False

    @staticmethod
    def validate_email(email: str, db: sqla_orm.Session) -> bool:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            return True 
        return False

    def __repr__(self):
        return f"<User {self.username}>"
