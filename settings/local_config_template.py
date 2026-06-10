from settings.global_config import BaseConfig


class Config(BaseConfig):
    DEBUG = True
    SECRET_KEY = "dev-secret-change-me"
    WTF_CSRF_ENABLED = True
