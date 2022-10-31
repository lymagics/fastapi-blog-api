from .base_test_case import BaseTestCase


class TestPosts(BaseTestCase):
    def test_create_post(self):
        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]

        data = {
            "title": "FastAPI Tutorial",
            "content": "Create restapi with FastAPI"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201
        post = resp.json()
        assert "post_id" in post
        assert "title" in post 
        assert "content" in post 
        assert "created_at" in post 
        assert "author" in post 
        assert post["title"] == "FastAPI Tutorial"
        assert post["content"] == "Create restapi with FastAPI"
        assert post["author"]["username"] == "bob"

    def test_retrieve_post_by_id(self):
        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]

        data = {
            "title": "FastAPI Tutorial",
            "content": "Create restapi with FastAPI"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201

        resp = self.client.get("/posts/1")
        assert resp.status_code == 200

        resp = self.client.get("/posts/2")
        assert resp.status_code == 404

    def test_edit_post(self):
        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]

        data = {
            "title": "FastAPI Tutorial",
            "content": "Create restapi with FastAPI"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201

        update_data = {
            "title": "New title",
            "content": "New content"
        }
        resp = self.client.put("/posts/1", headers={"Authorization": f"Bearer {access_token}"}, json=update_data)
        assert resp.status_code == 200
        post = resp.json()
        assert "post_id" in post
        assert "title" in post 
        assert "content" in post 
        assert "created_at" in post 
        assert "author" in post 
        assert post["title"] == "New title"
        assert post["content"] == "New content"
        assert post["author"]["username"] == "bob"

    def test_delete_post(self):
        resp = self.client.post("/tokens", data={"username": "bob", "password": "cat"})
        assert resp.status_code == 201
        access_token = resp.json()["access_token"]

        data = {
            "title": "FastAPI Tutorial",
            "content": "Create restapi with FastAPI"
        }
        resp = self.client.post("/posts", headers={"Authorization": f"Bearer {access_token}"}, json=data)
        assert resp.status_code == 201

        resp = self.client.delete("/posts/1", headers={"Authorization": f"Bearer {access_token}"})
        assert resp.status_code == 204

        resp = self.client.get("/posts/1")
        assert resp.status_code == 404
        