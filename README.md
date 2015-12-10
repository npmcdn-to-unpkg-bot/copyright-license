Code the Change: Copyright-License Project
=======

### Team Information
  * Team Lead: Christopher Yeh (chrisyeh@stanford.edu)
  * Communication: [Code the Change - Slack](http://codethechange.slack.com)

### Getting Started
1. Create GitHub and Heroku accounts, and request access from Chris Yeh (chrisyeh@stanford.edu).
2. Install Python 2.7 (with Pip). If you are running Windows, you may need to [add Python to your PATH](http://superuser.com/questions/143119/how-to-add-python-to-the-windows-path).
3. Install git, and clone this repository.
4. Install virtualenv (`pip install virtualenv`)
5. Install PostgresSQL (and add it to your PATH)
6. Setup / install Heroku by following the steps in Heroku's [Getting Started Guide](https://devcenter.heroku.com/articles/getting-started-with-python).
  * `git remote add heroku git@heroku.com:copyright-license.git`
  * use git bash to create SSH key, then run `heroku keys:add`
  * test that you can push to Heroku with `git push heroku master`
  * if you are running Windows, you may need to install the Microsoft Visual C++ compiler for Python 2.7

### Running the app locally
1. In Terminal (Mac) or Git Bash (Windows), run `source copyenv/bin/activate`
2. Run `python run.py` or `heroku local`
  * I have been having problems running `heroku local` on my on Windows laptop, so if you encounter the same error, that's not your fault.
3. Open up your web browswer and go to `http://localhost:5000`

### Making Changes to the App
1. Make whatever changes you want
2. Check that it works locally. See section "Running the app locally" above, and make sure everything works.
3. In Terminal (Mac) or Git Bash (Windows), run `git commit -m [COMMIT DESCRIPTION]`
4. Push to heroku: `git push heroku master`
5. Check to make sure that it works on our live heroku app: [copyright-license.herokuapp.com](http://copyright-license.herokuapp.com/). If there are any errors, check `heroku logs --tail`
6. Push to GitHub: `git push origin master`

### Random Useful Stuff
* SSH into heroku: `heroku run bash`