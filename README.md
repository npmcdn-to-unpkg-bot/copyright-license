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
    * View the list of configuration variables needed for the app to run: `heroku config`
    * For each variable in the list, add it to a `.env` file: `heroku config:get CONFIG-VAR-NAME -s >> .env`, where we replace `CONFIG-VAR-NAME` with the variable name.
      * Example: `heroku config:get API_KEY -s >> .env`
  * Option 2 (_Only if option 1 doesn't work_)
    * For each configuration variable in `copyright\config.py`, set it to the value that shows up when you run `heroku config`
    * Comment out anything that starts with `os.environ.get(...)`
    * __IMPORTANT__: Make sure you don't commit the `config.py` file to the repository. We do not want to make our API keys public, especially since they ensure that the communication with the payment system is secure.


### Running the app locally
1. Activate the virtual environment using the steps above
2. Run `python run.py` or `heroku local`
  * I sometimes have been having problems running `heroku local` on my on Windows laptop, so if you encounter the same error, that's not your fault.
  * If you do `python run.py`, then you may have to use Option 2 above to set up the configuration variables.
3. Open up your web browswer and go to `http://localhost:5000`


### Making Changes to the App
1. Make whatever changes you want
2. Check that it works locally. See section "Running the app locally" above, and make sure everything works.
3. Commit the changes with an appropriate description: `git commit -m [COMMIT DESCRIPTION]`
4. Push to Heroku: `git push heroku master`
5. Check to make sure that it works on our live Heroku app: [copyright-license.herokuapp.com](http://copyright-license.herokuapp.com/). If there are any errors, check the logs: `heroku logs --tail`
6. Push to GitHub: `git push origin master`


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
* SSH into heroku: `heroku run bash`


## Troubleshooting
* virtualenv seems to be not working?
  * Have you renamed the virtualenv folder recently? If so, you have to re-setup the virtualenv directory.