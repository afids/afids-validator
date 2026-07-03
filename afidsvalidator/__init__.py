"""Instantiate Flask and set up plugins."""

import os

import click
from flask import Flask
from flask_migrate import Migrate

from afidsvalidator.config import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
)
from afidsvalidator.model import db, login_manager
from afidsvalidator.learn import learn
from afidsvalidator.orcid import orcid_blueprint
from afidsvalidator.rag import KnowledgeChunk  # noqa: F401 — registers model
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
    app.register_blueprint(learn)

    # ── CLI commands ──────────────────────────────────────────────────────────
    @app.cli.command("ingest-knowledge")
    @click.option(
        "--file",
        "filepath",
        default=None,
        help="Path to a plain-text document to ingest (optional).",
    )
    @click.option(
        "--source",
        default=None,
        help="Source label for the document (required with --file).",
    )
    def ingest_knowledge_cmd(filepath, source):
        """Embed and store knowledge chunks in the RAG store.

        Without arguments, ingests the 32 AFIDs landmark definitions from
        landmark_info.py.  Pass --file and --source to ingest additional
        documents such as the AFIDs protocol paper.

        Example:
            flask ingest-knowledge
            flask ingest-knowledge --file afids_paper.txt --source afids_paper
        """
        from afidsvalidator.rag import ingest_landmarks, ingest_text_file

        if filepath:
            if not source:
                raise click.UsageError("--source is required when using --file")
            click.echo(f"Ingesting {filepath} as source={source!r} …")
            count = ingest_text_file(filepath, source)
        else:
            click.echo("Ingesting 32 AFIDs landmark definitions …")
            count = ingest_landmarks()

        click.echo(f"Done — {count} chunk(s) stored.")

    return app


if __name__ == "__main__":
    create_app().run()
