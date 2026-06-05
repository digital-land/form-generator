import unittest

from web_viewer.app import create_app
import settings.test_config as test_config


class WebTestCase(unittest.TestCase):
    """
    Base for tests needing the Flask app. Provides a test client and an active request
    context (required for binding/rendering WTForms fields).
    """

    def setUp(self):
        self.app = create_app(test_config.Config)
        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()
