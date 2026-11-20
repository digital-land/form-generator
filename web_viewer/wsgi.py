"""
WSGI entrypoint for hosting platforms that run gunicorn directly (e.g. Heroku).

    gunicorn web_viewer.wsgi:app
"""

import os

from web_viewer.app import create_app

app = create_app(os.environ.get("FLASK_CONFIG", "settings.container_config.Config"))
