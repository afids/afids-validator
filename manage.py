"""Flask database management script."""

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import DevelopmentConfig

from afidsvalidator import create_app
from afidsvalidator.model import db

app = create_app()

app.config.from_object(os.environ["APP_SETTINGS"])

postgres_uri = os.environ["DATABASE_URL"]
if postgres_uri.startswith("postgres://"):
    postgres_uri.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

manager = Manager(app)

manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
