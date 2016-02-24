Code the Change: Copyright-License Project
=======

### Team Information
  * Team Lead: Christopher Yeh (chrisyeh@stanford.edu)
  * Communication: [Code the Change - Slack](http://codethechange.slack.com)


### Getting Started
All of the commands should be run via Terminal (Mac) or Command Prompt / Git Bash (Windows). For Windows, sometimes it is more convenient to use one over the other, and I have indicated as such in these instructions.

1. Create GitHub and Heroku accounts, and request access from Chris Yeh (chrisyeh@stanford.edu).
2. Install Python 2.7 (with pip).
  * Mac: Python might already be installed, in which case you can skip this step.
  * Windows: be sure to [add Python to your PATH](http://superuser.com/questions/143119/how-to-add-python-to-the-windows-path).
  * Make sure that the path to Python's installation directory contains no spaces. Otherwise bad things will happen.
3. Install git, and clone this repository.
  * Make sure that the path to the folder where you clone this repo contains no spaces. Otherwise bad things will happen (namely, virtualenv won't work).
4. Install virtualenv (`pip install virtualenv`)
5. Install PostgresSQL (and add it to your PATH)
6. Setup / install Heroku by following the steps in Heroku's [Getting Started Guide](https://devcenter.heroku.com/articles/getting-started-with-python).
  * Add Heroku as a remote server for git: `git remote add heroku git@heroku.com:copyright-license.git`
  * If you don't have an SSH key yet, use Git Bash to [create a SSH key](https://confluence.atlassian.com/bitbucketserver/creating-ssh-keys-776639788.html)
  * Upload your SSH key to Heroku: `heroku keys:add`
  * Test that you can push to Heroku: `git push heroku master`
7. Set up your virtualenv
  * Make sure your current directory is `../copyright-license`
  * Create the virtual environment: `virtualenv env`
  * Activate the virtual environment
    * Windows (using Git Bash): `source env/Scripts/activate`
    * Windows (using Command Prompt): `env\Scripts\activate`
    * Mac OSX / Linux: `source env/bin/activate`
  * Install the required Python packages into the virtual environment: `pip install -r requirements.txt`
  * You can now deactivate the virtual environment: `deactivate`
  * For more information on how virtualenv works, check out the links under *Random Useful Stuff*
8. Set up appropriate configuration variables
  * Option 1 (__Recommended__)
    * Open Terminal / Command Prompt in the project folder
    * Export all of the variables to a `.env` file. This allows `heroku local` to read the proper environment variables: `heroku config -s >> .env`
    * To view the list of configuration variables needed for the app to run, either open the `.env` file or run: `heroku config`
    * To view the value of a specific variable: `heroku config:get CONFIG-VAR-NAME -s >> .env`, where we replace `CONFIG-VAR-NAME` with the variable name
  * Option 2 (_Only if option 1 doesn't work_)
    * For each configuration variable in `copyright\config.py`, set it to the value that shows up when you run `heroku config`
    * Comment out anything that starts with `os.environ.get(...)`
    * __IMPORTANT__: Make sure you don't commit the `config.py` file to the repository. We do not want to make our API keys public, especially since they ensure that the communication with the payment system is secure.


### Running the app locally
1. Activate the virtual environment using the steps above
2. Run `heroku local`
  * I sometimes have issues running `heroku local` on my on Windows laptop. In this case, try `python run.py`. You may have to use Option 2 above to set up the configuration variables. Just be sure to never commit the API keys to our repo.
3. Open up your web browswer and go to `http://localhost:5000`


### Making Changes to the App
1. Make whatever changes you want
2. Check that it works locally. See section "Running the app locally" above, and make sure everything works.
3. Commit the changes with an appropriate description: `git commit -m [COMMIT DESCRIPTION]`
4. Push to Heroku: `git push heroku master`
5. Check to make sure that it works on our live Heroku app: [copyright-license.herokuapp.com](http://copyright-license.herokuapp.com/). If there are any errors, check the logs: `heroku logs --tail`
6. Push to GitHub: `git push origin master`


### Managing the Database
* Accessing the database through a python shell
  1. Open Terminal / Command Prompt in the project folder
  2. Start a Heroku python shell: `heroku run python`
  3. Import the database and its tables. e.g.:
    * `from copyright import app`
    * `from copyright.models import db, LicenseTerms, PaymentAmount, LicenseReceipt`
  4. Run the appropriate database commands, e.g.:
    * `someItemToDelete = LicenseTerms.query.get(1)`
    * `db.session.delete(someItemToDelete)`
  5. To commit any changes to the database: `db.session.commit()`
* Accessing the database through a GUI (Windows or Mac)
  1. Open pgAdmin, which should have been installed with PostgreSQL
  2. File -> Add server...
  3. Enter the database connection information
    * Option 1: Login to Heroku in your web browser
      * Choose the `copyright-license` app
      * Click on the `Heroku Postgres :: Database` add-on
    * Option 2: Use Terminal / command line
      * `heroku pg:credentials DATABASE_URL`
  4. Look for the correct database in the sidebar
  5. To view and edit the actual data in the database:
    * Go to `Schemas -> public -> Tables` and choose the table you want to view
    * Click the icon in the toolbar for viewing table data
* Database Migrations
  1. Make sure you are in the virtual environment
  2. Make appropriate changes to the `models.py` file, which defines the database structure
  3. Run the migration: `python manage.py db migrate`
  4. Apply the upgrades to the actual database: `python manage.py db upgrade`
  5. You may need to run the migration on Heroku as well: `heroku run python manage.py db upgrade`
* Using a local database
  1. Create a local database in postgres: [https://youtu.be/fD7x8hd9yE4](https://youtu.be/fD7x8hd9yE4)
  2. Change `SQLALCHEMY_DATABASE_URI` in `config.py` to  `postgresql://postgres:PASSWORD@localhost/NAME_OF_LOCAL_DB`
  3. Make sure you are in the virtual environment
  4. run `python`
  5. In python, run the following commands:
    * `from copyright import db`
    * `db.create_all()`
  6. You should be good to go! Try running `heroku local`
  7. Remember to revert back to the original config variables before commiting to git.


### Stripe Integration
* Email Chris to get access to the Stripe Dashboard
* To have the Stripe authentication redirect to localhost, you can add a `redirect_uri` parameter to the URL in `create.html`. For example, https://connect.stripe.com/oauth/authorize?response_type=code&amp;client_id=ca_6MnivEyxNIcx1cNuyoGHc7u1dRcNevgW&amp;scope=read_write&amp;redirect_uri=http://localhost:5000/oauth/callback
* Note: this requires that the Stripe API be properly configured. In particular, `http://localhost:5000/oauth/callback` must be added as one of the Redirect URIs under the Stripe Account Settings.


### Random Useful Stuff
* How virtualenv works
  * [virtualenv User Guide](https://virtualenv.readthedocs.org/en/latest/userguide.html)
    * quite technical, not very easy to follow
    * contains instructions for Mac / Linux / Windows
  * [A non-magical introduction to Pip and Virtualenv for Python beginners](http://www.dabapps.com/blog/introduction-to-pip-and-virtualenv-python/)
    * easy to understand
    * uses Mac / Linux commands, so Windows users should refer to the user guide
* Complete Beginning to End Tutorials for running Flask and PostgreSQL on Heroku
  * [Flask and PostgreSQL on Heroku](http://blog.y3xz.com/blog/2012/08/16/flask-and-postgresql-on-heroku)
  * [Making a Flask app using a PostgreSQL database and deploying to Heroku](http://blog.sahildiwan.com/posts/flask-and-postgresql-app-deployed-on-heroku/)
  * [Flask web application development](http://www.vertabelo.com/blog/technical-articles/web-app-development-with-flask-sqlalchemy-bootstrap-introduction)
  * [Flask by Example](https://realpython.com/blog/python/flask-by-example-part-1-project-setup/)
  * [Flask Mega-Tutorial](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)
* SSH into heroku: `heroku run bash`


## Troubleshooting
* virtualenv seems to be not working?
  * Have you renamed the virtualenv folder recently? If so, you have to re-setup the virtualenv directory.