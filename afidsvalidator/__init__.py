"""Instantiate Flask and set up plugins."""

import os

from flask import Flask

from config import *

from afidsvalidator.views import validator
from afidsvalidator.model import db, login_manager
from afidsvalidator.orcid import orcid_blueprint


class ConfigException(Exception):
    """Exception raised when configuration is is invalid.

    Attributes:
        message -- explanation of why the config is invalid
    """

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


# Grab environment
if os.environ.get("FLASK_ENV") is None:
    raise ConfigException("Environment is not defined")

if os.environ.get("FLASK_ENV").lower() == "development":
    config_settings = DevelopmentConfig()
elif os.environ.get("FLASK_ENV").lower() == "testing":
    config_settings = TestingConfig()
elif os.environ.get("FLASK_ENV").lower() == "production":
    config_settings = ProductionConfig()
else:
    raise ConfigException("Defined environment is invalid")

# Relative path of directory for uploaded files
UPLOAD_DIR = "uploads/"


def create_app():
    app = Flask(__name__)

    app.config.from_object(config_settings)

    app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
    app.secret_key = "MySecretKey"

    if not os.path.isdir(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)

    heroku_uri = os.environ["DATABASE_URL"]
    if heroku_uri.startswith("postgres://"):
        heroku_uri = heroku_uri.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = heroku_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    login_manager.init_app(app)
    app.register_blueprint(validator)
    app.register_blueprint(orcid_blueprint)

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
