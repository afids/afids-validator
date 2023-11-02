"""Instantiate Flask and set up plugins."""

import os

from flask import Flask
from flask_migrate import Migrate

from afidsvalidator.config import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
)
from afidsvalidator.model import db, login_manager
from afidsvalidator.orcid import orcid_blueprint
from afidsvalidator.views import validator


class ConfigException(Exception):
    """Exception raised when configuration is is invalid.

    Attributes:
        message -- explanation of why the config is invalid
    """

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


# Grab environment
CONFIG_MAP = {
    "development": DevelopmentConfig(),
    "testing": TestingConfig(),
    "production": ProductionConfig(),
}
FLASK_ENV = os.environ.get("FLASK_ENV", None)
if FLASK_ENV is None:
    raise ConfigException("Environment is not defined")
if FLASK_ENV.lower() in CONFIG_MAP:
    config_settings = CONFIG_MAP[FLASK_ENV.lower()]
else:
    raise ConfigException("Defined environment is invalid")


def create_app():
    """Create and initialize an app according to the config."""
    app = Flask(__name__)
    app.config.from_object(config_settings)

    if not os.path.isdir(app.config["UPLOAD_DIR"]):
        os.mkdir(app.config["UPLOAD_DIR"])

    # Initialize databases and login manager
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(render_as_batch=True, compare_type=True)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(validator)
    app.register_blueprint(orcid_blueprint)

    return app


if __name__ == "__main__":
    create_app().run()
