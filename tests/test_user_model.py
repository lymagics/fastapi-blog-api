import pytest
from datetime import datetime

from .base_test_case import set_connection, BaseTestCase
from api.models import User


class TestUserModel(BaseTestCase):
    def test_password_inaccessible(self):
        u = User(username="alice", email="alice@example.com", password="cat")
        with pytest.raises(AttributeError):
            u.password

    def test_password_is_valid(self):
        u = User(username="alice", email="alice@example.com", password="cat")
        assert u.verify_password("cat")
        assert u.verify_password("dog") == False 

    def test_passwords_salts_are_random(self):
        u1 = User(username="alice", email="alice@example.com", password="cat")
        u2 = User(username="charlie", email="charlie@example.com", password="cat")
        assert u1.password_hash != u2.password_hash

    def test_ping(self):
        u = User(username="alice", email="alice@example.com", password="cat")
        ping = u.last_seen
        u.ping()
        assert ping != u.last_seen

    def test_generate_access_token(self):
        u = User(username="alice", email="alice@example.com", password="cat")
        t = u.generate_access_token()
        assert t.access_token is not None 
        assert t.refresh_token is not None 
        assert t.access_expiration > datetime.utcnow()
        assert t.refresh_expiration > datetime.utcnow()
        assert t.user == u

    def test_verify_access_token(self):
        with set_connection() as db:
            u = User(username="alice", email="alice@example.com", password="cat")
            db.add(u)
            t = u.generate_access_token()
            db.add(t)
            db.commit()
            db.refresh()
            assert User.verify_access_token(t.access_token, db) == u 

    def test_verify_refresh_token(self):
        with set_connection() as db:
            u = User(username="alice", email="alice@example.com", password="cat")
            db.add(u)
            t = u.generate_access_token()
            db.add(t)
            db.commit()
            db.refresh()
            assert User.verify_refresh_token(t, db=db) == t 

    def test_follow(self):
        u1 = User(username="alice", email="alice@example.com", password="cat")
        u2 = User(username="charlie", email="charlie@example.com", password="cat")
        u1.follow(u2)
        assert u1.is_following(u2)
        assert u2.is_followed_by(u1)
        assert u2.is_following(u1) == False 

    def test_unfollow(self):
        u1 = User(username="alice", email="alice@example.com", password="cat")
        u2 = User(username="charlie", email="charlie@example.com", password="cat")
        u1.follow(u2)
        u1.unfollow(u2)
        assert u1.is_following(u2) == False
        assert u2.is_followed_by(u1) == False

    def test_validate_username(self):
        with set_connection() as db:
            assert User.validate_username("alice", db)
            assert User.validate_username("bob", db) == False 

    def test_validate_email(self):
        with set_connection() as db:
            assert User.validate_email("alice@example.com", db)
            assert User.validate_email("bob@example.com", db) == False
