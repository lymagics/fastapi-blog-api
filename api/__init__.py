from fastapi import FastAPI


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI()

    register_routers(app)

    return app


def register_routers(app: FastAPI):
    """Register api routers."""
    from .resources.follows import follows
    app.include_router(follows)

    from .resources.users import users
    app.include_router(users) 

    from .resources.tokens import tokens
    app.include_router(tokens)

    from .resources.posts import posts
    app.include_router(posts)
