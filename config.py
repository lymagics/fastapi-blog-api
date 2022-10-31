from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application config."""
    debug: bool = False
    database_url: str = "sqlite:///db.sqlite"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    refresh_token_in_cookie: bool = True
    refresh_token_in_body: bool 
    use_cors: bool

    class Config:
        env_file = ".env"


settings = Settings()