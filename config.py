"""Configuration classes for flask/heroku."""

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(f"{basedir}/.env")


class Config(object):
    """Configuration class

    This class contains all of the global configuration variables needed for
    the AFIDs validator. Ideally, variables such as secret keys and such should
    be set by environment variable rather than explicitely here.
    """

    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "this-really-needs-to-be-changed"
    )
<<<<<<< HEAD
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
<<<<<<< HEAD
    AFIDS_DIR = "afidsvalidator/afids-templates"
    ALLOWED_EXTENSIONS = ["fcsv", "csv", "json"]
=======
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS") or False
    )
>>>>>>> fd43009... Add sql tracking to config
=======
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS") or False
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
>>>>>>> df63271... update to use config.py rather than grab from environ


class ProductionConfig(Config):
    """Config used in production"""

    CSRF_ENABLED = True  # Security flag
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    """Config used in development"""

    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    """Config used for pytest"""

    DEBUG = True
    TESTING = True
