from settings.global_config import BaseConfig


class Config(BaseConfig):
    TESTING = True
    DEBUG = True
    SECRET_KEY = "test-secret"
    WTF_CSRF_ENABLED = False
