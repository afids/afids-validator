# [fidvalidator (https://fidvalidator.herokuapp.com)](fidvalidator.herokuapp.com)

## Development
### Required Packages
_Install via `apt-get` or `snap`_
* postgresql
* heroku

### Setup for local testing
1. Git clone the fid-validator repository `git clone https://github.com/Park-Patrick/fidvalidator.git`
2. Add heroku as a remote `heroku git:remote -a fidvalidator`
3. Set up python virtual environment `python -m virtualenv <venv directory>`
4. In virtual environment, install required modules `pip install -r requirements.txt --no-cache-dir`
5. Create a superuser via postgres `sudo createuser --interactive`
6. Create a database via postgres `createdb fid_db`
7. Set password for the created database
    ```
    psql fid_db
    \password
    ```
8. Create environment for development `touch .env`
9. Add configuration to `.env` file
   ```
   export APP_SETTINGS="config.DevelopmentConfig"
   export DATABASE_URL="postgresql://<user>:<password>@localhost/fid_db"
   ```
10. `source .env`
11. `python manage.py db upgrade`
12. `python manage.py runserver`

If there are no errors, you can test it out locally at http://localhost:5000

### Development
**Ensure local repository is up-to-date prior to making changes and/or pushing back to Git. Best practice is to test locally on a new branch, and make a pull request (PR) to pull in new changes**
1. `git checkout master`
2. `git pull`
3. `git checkout -b feature-branch`
4. Make changes on local repository
2. Test changes by running `heroku local`, which will set up the server locally \
_If the migrations folder has been changed, run `python manage.py db upgrade`_
3. Push to git (`git push -u origin feature-branch`) and create a PR if needed
4. Push to heroku `git push heroku master`


## Update Templates
Templates for the validator stored under the `afids-templates` directory. Within this directory, there are sub-folders. Human-based templates are stored under the `human` sub-directory. To add templates to the validator, add them to the appropriate directory under `afids-templates` and create a pull request.


## To Do List:
* additional stats / insights availible for the user
* direct slicer connection
`
