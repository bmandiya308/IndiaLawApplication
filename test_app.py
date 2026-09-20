import os
import tempfile
import unittest

from app import app


class IpcCatalogTestCase(unittest.TestCase):
    def setUp(self):
        self.database = tempfile.NamedTemporaryFile(delete=False)
        self.database.close()
        app.config["TESTING"] = True
        app.config["DATABASE"] = self.database.name
        app.config["ADMIN_PASSWORD"] = "test-password"
        with app.app_context():
            from app import init_db
            init_db()
        self.client = app.test_client()

    def tearDown(self):
        os.unlink(self.database.name)

    def test_homepage_and_search(self):
        response = self.client.get("/?q=theft")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Punishment for theft", response.data)

    def test_article_api_rejects_missing_fields_and_creates_entry(self):
        response = self.client.post("/api/articles", json={"section_code": "600"})
        self.assertEqual(response.status_code, 401)
        response = self.client.post("/login", data={
            "username": "bmandiya308", "password": "test-password",
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.post("/api/articles", json={"section_code": "600"})
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/articles", json={
            "section_code": "600", "title": "Test section", "chapter": "Test chapter",
            "text": "Test text", "details": "Test details", "punishment": "Test punishment",
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["section_code"], "600")
        self.assertEqual(response.get_json()["punishment"], "Test punishment")


if __name__ == "__main__":
    unittest.main()