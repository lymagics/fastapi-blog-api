from .base_test_case import BaseTestCase


class TestPagination(BaseTestCase):
    def test_retrieve_all_users(self):
        resp = self.client.get("/users?limit=2")
        assert resp.status_code == 200 

        data = resp.json()
        assert "users" in data 
        assert "pagination" in data 
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert len(data["users"]) == 1

    def test_retrieve_all_posts(self):
        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]

        data = {
            "title": "FastAPI Tutorial",
            "content": "Create restapi with FastAPI"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201

        resp = self.client.get("/posts?limit=2")
        assert resp.status_code == 200 

        data = resp.json()
        assert "posts" in data 
        assert "pagination" in data 
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert len(data["posts"]) == 1

    def test_retrieve_all_posts_from_user(self):
        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]

        data = {
            "title": "FastAPI Tutorial",
            "content": "Create restapi with FastAPI"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201

        resp = self.client.get("/users/1/posts?limit=2")
        assert resp.status_code == 200 

        data = resp.json()
        assert "posts" in data 
        assert "pagination" in data 
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert len(data["posts"]) == 1
        assert data["posts"][0]["author"]["username"] == "bob"

    def test_retrieve_current_user_following(self):
        data = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "dog"
        } 
        resp = self.client.post("/users", json=data)
        assert resp.status_code == 201

        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201

        access_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        resp = self.client.post("/me/following/2", headers=headers)
        assert resp.status_code == 204

        resp = self.client.get("/me/following?limit=2", headers=headers)
        assert resp.status_code == 200 

        data = resp.json()
        assert "users" in data 
        assert "pagination" in data 
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert len(data["users"]) == 1

    def test_retrieve_current_user_followers(self):
        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201

        access_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        resp = self.client.get("/me/followers?limit=2", headers=headers)
        assert resp.status_code == 200 

        data = resp.json()
        assert "users" in data 
        assert "pagination" in data 
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert len(data["users"]) == 0 

    def test_retrieve_user_following(self):
        data = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "dog"
        } 
        resp = self.client.post("/users", json=data)
        assert resp.status_code == 201

        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201

        access_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        resp = self.client.post("/me/following/2", headers=headers)
        assert resp.status_code == 204

        resp = self.client.get("/users/1/following?limit=2")
        assert resp.status_code == 200  

        data = resp.json()
        assert "users" in data 
        assert "pagination" in data 
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert len(data["users"]) == 1

    def test_retrieve_user_followers(self):
        data = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "dog"
        } 
        resp = self.client.post("/users", json=data)
        assert resp.status_code == 201

        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201

        access_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        resp = self.client.post("/me/following/2", headers=headers)
        assert resp.status_code == 204

        resp = self.client.get("/users/2/followers?limit=2")
        assert resp.status_code == 200  

        data = resp.json()
        assert "users" in data 
        assert "pagination" in data 
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["offset"] == 0
        assert len(data["users"]) == 1
