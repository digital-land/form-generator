from settings.global_config import BaseConfig


class Config(BaseConfig):
    DEBUG = False
    WTF_CSRF_ENABLED = True
    # CSRF is in place but fully public open data without auth so not actually needed yet
    SECRET_KEY = "not-actually-secret"
