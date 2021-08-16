"""Flask database management script."""

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import DevelopmentConfig

from afidsvalidator import create_app
from afidsvalidator.model import db

# Grab environment
if os.environ.get("FLASK_ENV").lower() == "production":
    from config import ProductionConfig

    config_settings = ProductionConfig
elif os.environ.get("FLASK_ENV").lower() == "testing":
    from config import TestingConfig

    config_settings = TestingConfig
else:
    config_settings = DevelopmentConfig

# Set up app
app = create_app()
app.config.from_object(config_settings)

# Set up db
manager = Manager(app)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
