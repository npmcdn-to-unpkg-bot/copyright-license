Code the Change: Copyright-License Project
=======

### Team Information
  * Team Lead: Christopher Yeh (chrisyeh@stanford.edu)
  * Communication: [Code the Change - Slack](http://codethechange.slack.com)


### Setup Instructions
Follow the instructions in the [Wiki](https://github.com/chrisyeh96/copyright-license/wiki/Setup-Guide) for how to setup your dev environment.


### Running the app locally
1. Activate the virtual environment
  * Windows (using Git Bash): source env/Scripts/activate
  * Windows (using Command Prompt): env\Scripts\activate
  * Mac OSX / Linux: source env/bin/activate
2. Run `heroku local`
  * I sometimes have issues running `heroku local` on my on Windows laptop. In this case, try `python run.py`. You may have to use Option 2 above to set up the configuration variables. Just be sure to never commit the API keys to our repo.
3. Open up your web browswer and go to `http://localhost:5000`


### Making Changes to the App
1. Pull the latest changes into your local master branch
  * `git checkout master` and `git pull`
2. Checkout your own branch if you have one, or create a new branch if you don't.
  * Creating a new branch: e.g. `git branch chris-dev`
  * Switching branches: e.g. `git checkout chris-dev`
  * Merge in the latest changes from the `master` branch: `git merge master`
3. Make changes to the app.
4. Check that it works locally. See section "Running the app locally" above.
5. Commit the changes with an appropriate description
  * Select files from your working directory with `git add [FILENAME]`
  * Commit the files: `git commit -m [COMMIT DESCRIPTION]`
6. Push to your branch on GitHub: `git push origin`
7. Submit a pull request on GitHub to merge your changes into the `master` branch.
8. Once someone has reviewed your changes and merged them into master, pull the latest changes to master: `git checkout master` and `git pull`
9. Push to Heroku: `git push heroku master`
10. Check to make sure that it works on our live Heroku app: [copyright-license.herokuapp.com](http://copyright-license.herokuapp.com/). If there are any errors, check the logs: `heroku logs --tail`


### Managing the Database
Check the Wiki page [here](https://github.com/chrisyeh96/copyright-license/wiki/Managing-the-Database)


### Stripe Integration
* Email Chris to get access to the Stripe Dashboard
* To have the Stripe authentication redirect to localhost, you can add a `redirect_uri` parameter to the URL in `create.html`. For example, https://connect.stripe.com/oauth/authorize?response_type=code&amp;client_id=ca_6MnivEyxNIcx1cNuyoGHc7u1dRcNevgW&amp;scope=read_write&amp;redirect_uri=http://localhost:5000/oauth/callback
* Note: this requires that the Stripe API be properly configured. In particular, `http://localhost:5000/oauth/callback` must be added as one of the Redirect URIs under the Stripe Account Settings.


### Random Useful Stuff
Check the Wiki page [here](https://github.com/chrisyeh96/copyright-license/wiki/Random-Useful-Stuff)


## Troubleshooting
* virtualenv seems to be not working?
  * Have you renamed the virtualenv folder recently? If so, you have to re-setup the virtualenv directory.