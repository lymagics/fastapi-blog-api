from datetime import datetime, timedelta
from time import sleep

from .base_test_case import set_connection, BaseTestCase
from api.models import Token, User


class TestTokenModel(BaseTestCase):
    def test_generate_tokens(self):
        u = User(username="alice", email="alice@example.com", password="cat")
        t = Token(user=u)
        t.generate()
        assert t.access_token is not None 
        assert t.refresh_token is not None 
        assert t.access_expiration > datetime.utcnow()
        assert t.refresh_expiration > datetime.utcnow()

    def test_expire(self):
        u = User(username="alice", email="alice@example.com", password="cat")
        t = Token(user=u)
        t.generate()
        t.expire()
        sleep(1)
        assert t.access_expiration < datetime.utcnow()
        assert t.refresh_expiration < datetime.utcnow()

    def test_clean(self):
        with set_connection() as db:
            u = User(username="alice", email="alice@example.com", password="cat")
            t = u.generate_access_token()
            t.refresh_expiration = datetime.utcnow() + timedelta(days=2)
            db.add_all([u, t])
            db.commit()
            Token.clean(db)
            db.commit()
            assert db.query(Token).all() == []
