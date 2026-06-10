from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()


def create_app(settings_class):
    app = Flask(__name__)
    app.config.from_object(settings_class)

    # validates the csrf_token on every state changing request (honours WTF_CSRF_ENABLED) and
    # exposes csrf_token() to templates
    csrf.init_app(app)

    from web_viewer.views.main_view import main_blueprint

    app.register_blueprint(main_blueprint, url_prefix="/")

    return app


def run_local_app():
    import settings.local_config as local_config

    app = create_app(local_config.Config)
    app.run(
        host="0.0.0.0",
        port=app.config["HTTP_PORT"],
        debug=app.config["DEBUG"],
    )


if __name__ == "__main__":
    run_local_app()
