[![AFIDs](https://github.com/afids/afids-validator/blob/master/static/images/banner.png)](./static/images/banner.png)

[![](https://img.shields.io/twitter/url?style=social&url=https%3A%2F%2Ftwitter.com%2Fafids_project)](https://twitter.com/afids_project)
[![AFIDs Validator CI/CD](https://github.com/afids/afids-validator/actions/workflows/afids-validator_ci.yml/badge.svg)](https://github.com/afids/afids-validator/actions/workflows/afids-validator_ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Anatomical fiducials (AFIDs) is an open framework for evaluating correspondence in brain images and teaching neuroanatomy using anatomical fiducial placement. The AFIDs Validator project aims to build a web application that allows the user to upload an FCSV file generated using the AFIDs protocol, and validate that it conforms to the protocol.

# [afids-validator (https://afids-validator.herokuapp.com)](https://afids-validator.herokuapp.com)

## Development
### Required Packages
_Install via `apt-get` or `snap`_
* postgresql
* heroku

### Setup for local testing
1. Git clone the fid-validator repository `git clone https://github.com/afids/afids-validator.git`
2. Add heroku as a remote `heroku git:remote -a afids-validator`
3. Set up python virtual environment `python -m virtualenv <venv directory>`
4. In virtual environment, install required modules `pip install -r requirements.txt --no-cache-dir`
5. Create a superuser via postgres `sudo createuser --interactive`
6. Create a database via postgres `createdb fid_db`
7. Set password for the created database
    ```
    psql fid_db
    \password
    ```
8. Update configuration in `.env.template` and rename to `.env` file
9. `python manage.py db upgrade`
10. `python manage.py runserver`

If there are no errors, you can test it out locally at http://localhost:5000
