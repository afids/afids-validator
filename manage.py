"""Flask database management script."""

from flask_migrate import Migrate

from afidsvalidator import create_app
from afidsvalidator.model import db


migrate = Migrate(render_as_batch=True, compare_type=True)

# Set up app
app = create_app()
migrate.init_app(app, db)
