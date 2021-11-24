"""Set up blueprint for ORCID authentication."""

from flask_dance.consumer import OAuth2ConsumerBlueprint, oauth_authorized
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage
from flask_login import current_user, login_user
from sqlalchemy.orm.exc import NoResultFound

from afidsvalidator.model import db, OAuth, User

orcid_blueprint = OAuth2ConsumerBlueprint(
    "orcid",
    __name__,
    base_url="https://api.orcid.org/v3.0",
    token_url="https://orcid.org/oauth/token",
    authorization_url="https://orcid.org/oauth/authorize",
    storage=SQLAlchemyStorage(
        OAuth, db.session, user=current_user, user_required=True
    ),
    scope="openid",
)
orcid_blueprint.from_config["client_id"] = "ORCID_OAUTH_CLIENT_ID"
orcid_blueprint.from_config["client_secret"] = "ORCID_OAUTH_CLIENT_SECRET"


@oauth_authorized.connect_via(orcid_blueprint)
def orcid_logged_in(blueprint, token):
    """Create/login user on successful ORCID login."""
    if not token:
        return False

    orcid_id = token["orcid"]

    try:
        oauth = OAuth.query.filter_by(
            provider=orcid_blueprint.name, provider_user_id=orcid_id
        ).one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name, provider_user_id=orcid_id, token=token
        )

    if oauth.user:
        login_user(oauth.user)
    else:
        user = User(name=token["name"])
        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)

    return False
