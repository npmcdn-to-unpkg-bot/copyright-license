Code the Change: Copyright-License Project
=======

### Team Information
  * Team Lead: Christopher Yeh (chrisyeh@stanford.edu)
  * Communication: [Code the Change - Slack](http://codethechange.slack.com)


### Getting Started
All of the commands should be run via Terminal (Mac) or Command Prompt / Git Bash (Windows). For Windows, sometimes it is more convenient to use one over the other, and I have indicated as such in these instructions.

1. Create GitHub and Heroku accounts, and request access from Chris Yeh (chrisyeh@stanford.edu).
2. Install Python 2.7 (with pip). If you are running Windows, you may need to [add Python to your PATH](http://superuser.com/questions/143119/how-to-add-python-to-the-windows-path).
3. Install git, and clone this repository.
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
    * Windows (using Git Bash): `source env\Scripts\activate`
    * Windows (using Command Prompt): `env\Scripts\activate`
    * Mac OSX / Linux: `source env/bin/activate`
  * Install the required Python packages into the virtual environment: `pip install -r requirements.txt`
  * You can now deactivate the virtual environment: `deactivate`
  * For more information on how virtualenv works, check out the links under *Random Useful Stuff*


### Running the app locally
1. Activate the virtual environment using the steps above
2. Run `python run.py` or `heroku local`
  * I have been having problems running `heroku local` on my on Windows laptop, so if you encounter the same error, that's not your fault.
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
* SSH into heroku: `heroku run bash`