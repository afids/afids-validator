"""Configuration classes for flask/heroku."""

import os
from dataclasses import dataclass

from flask.cli import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Configuration class

    This class contains all of the global configuration variables needed for
    the AFIDs validator. Ideally, variables such as secret keys and such should
    be set by environment variable rather than explicitly here.
    """

    ORCID_OAUTH_CLIENT_ID = os.environ.get("ORCID_OAUTH_CLIENT_ID")
    ORCID_OAUTH_CLIENT_SECRET = os.environ.get("ORCID_OAUTH_CLIENT_SECRET")

    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "this-really-needs-to-be-changed"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
        "SQLALCHEMY_TRACK_MODIFICATIONS", False
    )

    UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads/")


@dataclass
class ProductionConfig(Config):
    """Config used in production"""

    CSRF_ENABLED = True  # Security flag
    DEBUG = False
    TESTING = False


@dataclass
class DevelopmentConfig(Config):
    """Config used in development"""

    DEBUG = True
    TESTING = False


@dataclass
class TestingConfig(Config):
    """Config used for pytest"""

    DEBUG = True
    TESTING = True
