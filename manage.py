"""Flask database management script."""

import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from afidsvalidator import create_app
from afidsvalidator.model import db

# Set up app
app = create_app()

# Set up db
manager = Manager(app)
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
    manager.run()
