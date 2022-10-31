from typing import Optional

from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import errors, schemas, models
from ..database import get_db
from config import settings

tokens = APIRouter(tags=["Tokens"])


def token_response(token: models.Token, response: Response):
    """Construct valid token response."""
    samesite = "strict"
    if settings.refresh_token_in_cookie:
        if settings.use_cors:
            samesite = "none" if not settings.debug else "lax"
        response.set_cookie("refresh_token", token.refresh_token,
        path="/tokens", secure=not settings.debug,
        httponly=True, samesite=samesite)

    return {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token
        if settings.refresh_token_in_body else None
    }


@tokens.post("/tokens", response_model=schemas.Token, status_code=201)
def create_access_token(response: Response, credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Create new access and refresh tokens."""
    user = db.query(models.User).filter(models.User.username == credentials.username).first()
    if user is None or not user.verify_password(credentials.password):
        raise errors.Unauthorized
    token = user.generate_access_token()
    db.add(token)
    models.Token.clean(db)
    db.commit()
    return token_response(token, response)


@tokens.put("/tokens", response_model=schemas.Token)
def refresh_access_token(response: Response, token: models.Token = Depends(models.User.verify_refresh_token), db: Session = Depends(get_db)):
    """Refresh an access token."""
    token.expire()
    db.commit()
    new_token = token.user.generate_access_token()
    db.add(new_token)
    db.commit()
    return token_response(new_token, response)


@tokens.delete("/tokens", status_code=204)
def revoke_access_token(token: schemas.Token, db: Session = Depends(get_db)):
    """Revoke an access token."""
    token = db.query(models.Token).filter(models.Token.access_token == token.access_token).first()
    if token is None:
        raise errors.Unauthorized
    token.expire()
    db.commit()
    return {}
