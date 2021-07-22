"""Flask database management script."""

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import DevelopmentConfig

from afidsvalidator import create_app
from afidsvalidator.model import db

app = create_app()

<<<<<<< HEAD
app.config.from_object(os.environ["APP_SETTINGS"])

postgres_uri = os.environ["DATABASE_URL"]
if postgres_uri.startswith("postgres://"):
    postgres_uri.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

=======
if os.environ.get("FLASK_ENV").lower() == "production":
    from config import ProductionConfig

    config_settings = ProductionConfig
elif os.environ.get("FLASK_ENV").lower() == "testing":
    from config import TestingConfig

    config_settings = TestingConfig
else:
    config_settings = DevelopmentConfig
app.config.from_object(config_settings)

migrate = Migrate(app, db)
>>>>>>> 92c7a0f... lint manage.py
manager = Manager(app)

manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
