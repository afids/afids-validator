"""Instantiate Flask and set up plugins."""

import os

from flask import Flask

from afidsvalidator.views import validator
from afidsvalidator.model import db

app = Flask(__name__)
app.register_blueprint(validator)

app.config.from_object(os.environ["APP_SETTINGS"])

# Relative path of directory for uploaded files
UPLOAD_DIR = "uploads/"

app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.secret_key = "MySecretKey"

if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

heroku_uri = os.environ["DATABASE_URL"]
if heroku_uri.startswith("postgres://"):
    heroku_uri = heroku_uri.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = heroku_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
app.register_blueprint(validator)

if __name__ == "__main__":
    app.run(debug=True)
