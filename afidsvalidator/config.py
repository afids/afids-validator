"""Configuration classes for flask/heroku."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Configuration class

    This class contains all of the global configuration variables needed for
    the AFIDs validator. Ideally, variables such as secret keys and such should
    be set by environment variable rather than explicitely here.
    """

    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "this-really-needs-to-be-changed"
    )

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS") or False
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    ORCID_OAUTH_CLIENT_ID = os.environ.get("ORCID_OAUTH_CLIENT_ID")
    ORCID_OAUTH_CLIENT_SECRET = os.environ.get("ORCID_OAUTH_CLIENT_SECRET")


@dataclass
class ProductionConfig(Config):
    """Config used in production"""

    CSRF_ENABLED = True  # Security flag
    DEBUG = False
    TESTING = False


@dataclass
class DevelopmentConfig(Config):
    """Config used in development"""

    DEVELOPMENT = True
    DEBUG = True


@dataclass
class TestingConfig(Config):
    """Config used for pytest"""

    DEBUG = True
    TESTING = True
