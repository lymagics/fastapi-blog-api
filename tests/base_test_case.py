import unittest
from contextlib import contextmanager

from fastapi.testclient import TestClient 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api import create_app
from api.database import get_db, Base
from api.models import User

engine = create_engine("sqlite:///testdb.sqlite")
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def set_connection():
    db = TestingSessionLocal()
    try:
        yield db 
    except:
        db.rollback()
    finally:
        db.close()


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        Base.metadata.create_all(bind=engine)
        self.app = create_app()
        self.app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(self.app)

        db = TestingSessionLocal()
        user = User(username="bob", email="bob@example.com", password="cat")
        db.add(user)
        db.commit()
        db.close()

    def tearDown(self):
        Base.metadata.drop_all(bind=engine)
