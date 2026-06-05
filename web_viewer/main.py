"""
Run a Flask app using gunicorn in a container.

inspired by-
https://github.com/Aye-Aye-Dev/Fossa
"""

import os

import gunicorn.app.base

from web_viewer.app import create_app


class StandaloneApplication(gunicorn.app.base.BaseApplication):
    """
    Run a WSGI web-app using gunicorn.
    """

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def run_flask_app(deployment_config):
    """
    Use gunicorn to run Flask app.

    @param deployment_config: (str or class or anything accepted by Flask's `app.config.from_object`)
        Used to choose the settings file. i.e. 'prod' uses .....settings.prod_config.Config
    """
    app = create_app(deployment_config)

    options = {
        "bind": "%s:%s" % ("0.0.0.0", app.config["HTTP_PORT"]),
        "workers": 4,
        "syslog": True,
        "timeout": 80,
        "access_log_format": '%(t)s %(h)s INFO "%(r)s" %(s)s %(b)s "%(a)s"',
        "accesslog": "-",
        "errorlog": "-",
    }

    # switch to TLS mode if certs are available.
    # security-wise these shouldn't be optional but just making this demo code easier to
    # stand-up.
    tls_options = {
        "certfile": "/etc/ssl/private/fullchain.pem",
        "keyfile": "/etc/ssl/private/privkey.pem",
    }

    if os.path.exists(tls_options["certfile"]) and os.path.exists(tls_options["keyfile"]):
        options.update(tls_options)
        options["bind"] = "0.0.0.0:443"

    StandaloneApplication(app, options).run()


if __name__ == "__main__":
    config_package = "settings.container_config.Config"
    run_flask_app(config_package)
