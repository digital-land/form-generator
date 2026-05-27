import unittest

from web_viewer.app import create_app
import settings.test_config as test_config


class TestWeb(unittest.TestCase):
    def setUp(self):
        self.app = create_app(test_config.Config)
        self.client = self.app.test_client()

    def test_web_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Forms Generator", response.data)
