from tests.base import WebTestCase


class TestWeb(WebTestCase):
    def test_web_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Forms Generator", response.data)
