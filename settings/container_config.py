import os

from settings.global_config import BaseConfig


class Config(BaseConfig):
    DEBUG = False
    WTF_CSRF_ENABLED = True
    # CSRF is in place but fully public open data without auth so not actually needed yet.
    # Set the SECRET_KEY environment variable (e.g. a Heroku config var) to override the fallback.
    SECRET_KEY = os.environ.get("SECRET_KEY", "not-actually-secret")
    # Docker: cloned in the Dockerfile. Heroku: downloaded by bin/post_compile (app root is /app).
    PLANNING_APPLICATION_DATA_SPECIFICATION_REPO = "/app/planning-application-data-specification"
