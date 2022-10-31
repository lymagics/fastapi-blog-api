from .base_test_case import BaseTestCase


class TestUsers(BaseTestCase):
    def test_create_user(self):
        data = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "dog"
        }

        resp = self.client.post("/users", json=data)
        assert resp.status_code == 201
        user_data = resp.json()
        assert "username" in user_data
        assert "user_id" in user_data
        assert "last_seen" in user_data
        assert "member_since" in user_data
        assert "about_me" in user_data
        assert "email" not in user_data
        assert "password" not in user_data
        assert user_data["username"] == "alice"

        wrong_data = {
            "username": "bob",
            "email": "helloworld"
        }
        resp = self.client.post("/users", json=wrong_data)
        assert resp.status_code == 422

    def test_retrieve_user_by_username(self):
        resp = self.client.get("/users/bob")
        assert resp.status_code == 200
        assert resp.json()["username"] == "bob"

        resp = self.client.get("/users/alice")
        assert resp.status_code == 404

    def test_retrieve_authenticated_user(self):
        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201

        access_token = resp.json()["access_token"]

        resp = self.client.get("/me", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 200
        assert resp.json()["username"] == "bob"

    def test_edit_user(self):
        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201

        access_token = resp.json()["access_token"]

        data = {
            "username": "alice",
            "email": "alice@example.com",
            "about_me": "UI/UX designer"
        }
        resp = self.client.put("/me", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 200
        user_data = resp.json()
        assert user_data["username"] == "alice"
        assert user_data["about_me"] == "UI/UX designer"

        # Update with the same values
        resp = self.client.put("/me", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 200

        new_user = {
            "username": "bob",
            "email": "bob@example.com",
            "password": "dog"
        }

        resp = self.client.post("/users", json=new_user)
        assert resp.status_code == 201

        #Update with existing user data
        resp = self.client.put("/me", headers={"Authorization": f"Bearer {access_token}"}, json=new_user)
        assert resp.status_code == 400

