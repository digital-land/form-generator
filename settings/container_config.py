from settings.global_config import BaseConfig


class Config(BaseConfig):
    DEBUG = False
    WTF_CSRF_ENABLED = True
