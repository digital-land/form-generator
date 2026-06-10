import re

from settings.global_config import BaseConfig
from tests.base import WebTestCase
from web_viewer.app import create_app


class TestWebPlanningCsrf(WebTestCase):
    """
    CSRF protection is enforced on the application POST when WTF_CSRF_ENABLED is on.
    """

    def setUp(self):
        class CsrfConfig(BaseConfig):
            TESTING = True
            SECRET_KEY = "test-secret"
            WTF_CSRF_ENABLED = True

        self.app = create_app(CsrfConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def test_get_renders_csrf_token(self):
        response = self.client.get("/application/outline-all")
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="csrf_token"', response.text)

    def test_post_without_token_is_rejected(self):
        response = self.client.post("/application/outline-all", data={})
        self.assertEqual(response.status_code, 400)

    def test_post_with_token_is_accepted(self):
        page = self.client.get("/application/outline-all")
        token = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)

        response = self.client.post("/application/outline-all", data={"csrf_token": token})
        self.assertEqual(response.status_code, 200)
        self.assertEqual("application/json", response.mimetype)
