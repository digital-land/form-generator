class BaseConfig:
    DEBUG = False
    HTTP_PORT = 2121
    SECRET_KEY = None
    WTF_CSRF_ENABLED = True

    # filesystem path to local copy of https://github.com/digital-land/planning-application-data-specification
    # Only needed by `builder/build_schema.py`
    PLANNING_APPLICATION_DATA_SPECIFICATION_REPO = None
