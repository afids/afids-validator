[![AFIDs](https://github.com/afids/afids-validator/blob/master/afidsvalidator/static/images/banner.png)](./static/images/banner.png)

[![](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2Fafids_project)](https://twitter.com/afids_project)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7871819.svg)](https://doi.org/10.5281/zenodo.7871819)
[![AFIDs Validator CI](https://github.com/afids/afids-validator/actions/workflows/afids-validator_ci.yml/badge.svg)](https://github.com/afids/afids-validator/actions/workflows/afids-validator_ci.yml)
[![AFIDs Validator Release](https://github.com/afids/afids-validator/actions/workflows/afids-validator_release.yml/badge.svg)](https://github.com/afids/afids-validator/actions/workflows/afids-validator_release.yml)
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/afids/afids-validator?sort=semver)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Anatomical fiducials (AFIDs) is an open framework for evaluating correspondence in brain images and teaching neuroanatomy using anatomical fiducial placement. The AFIDs Validator project aims to build a web application that allows the user to upload an FCSV file generated using the AFIDs protocol, and validate that it conforms to the protocol.

# [afids-validator (https://validator.afids.io)](https://validator.afids.io)

## Development

`poetry` is used to manage dependencies. To install, run the following command:

```
curl -sSL https://install.python-poetry.org | python3 -
```

For detailed setup instructions, see the documentation [here](https://python-poetry.org/).

Once installed, you can set up your development environment by:

1. Git clone the afids-validator repository `git clone https://github.com/afids/afids-validator.git`
1. Set up python environment via `poetry shell`
1. Install the required libraries via `poetry install --with dev`
1. Install the pre-commit action via `poetry run poe setup`. This will automatically perform quality tasks for each new commit.
1. Update configuration in `.env.template` and rename to `.env` file

This will allow you to make changes and perform the necessary formatting and linting tasks. To test changes, the easiest way is via `docker compose`. To use this, you will need to install [Docker](https://docs.docker.com/get-docker/).

Once installed, you can run `docker compose up --build` in the terminal.

If there are no errors, you can test it out locally at http://localhost:5001

After you are done testing, you can hit `CTRL/CMD+C` on the terminal to exit out of the instance and run `docker compose down` to remove unused containers.

#### Testing afids upload

If `docker compose` successfully starts the required services, you will first want to enter the afids-validator container interactively to migrate the database, enabling testing of database uploads.

```bash
# Enter the container interactively
docker exec -it afids-validator-afidsvalidator-1 bash

# Migrate the database
flask db upgrade -d /usr/local/lib/python3.9/dist-packages/migrations/
```

_Note: You may need to change the container name (i.e. `afids-validator-afidsvalidator-1`) accordingly._

#### Testing login

To test the login with ORCID iD:

1. Create an account (with a mailinator.com email address) on sandbox.orcid.org
2. Follow [these instructions](https://info.orcid.org/documentation/integration-guide/registering-a-public-api-client/#easy-faq-2606) to get a client ID and client secret. Set the `Redirect URIs` to your local testing address (eg. `127.0.0.1:5001`, `localhost:5001`)
3. Update your local `.env` file with your new credentials.
4. Locally change the URLs in `afidsvalidator/orcid.py` to start with api.sandbox.orcid.org
5. Run the application and test your login.
