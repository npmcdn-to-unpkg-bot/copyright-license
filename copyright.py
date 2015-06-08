import datetime
import os
import requests

from flask import Flask
from flask import render_template
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy

import stripe


app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('DEBUG', False)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.config['SITE'] = 'https://connect.stripe.com'
app.config['TOKEN_URI'] = '/oauth/token'
app.config['CLIENT_ID'] = os.environ['CLIENT_ID']
app.config['API_KEY'] = os.environ['API_KEY']

# stripe_keys = {
#     'secret_key': os.environ['SECRET_KEY'],
#     'publishable_key': os.environ['PUBLISHABLE_KEY']
# }
#
# stripe.api_key = stripe_keys['secret_key']

db = SQLAlchemy(app)


class LicenseTerms(db.Model):
    """
    The terms under which an image can be licensed
    """
    __tablename__ = "terms"
    id = db.Column(db.Integer, primary_key=True)
    owner_stripe_token = db.Column(db.String())
    amount = db.Column(db.String())
    image_url = db.Column(db.String())
    time_recorded = db.Column(db.DateTime())


class License(db.Model):
    """
    A record of users who have paid for a license
    """
    __tablename__ = "licenses"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String())
    license_id = db.Column(db.Integer) #TODO make foreign key
    time_recorded = db.Column(db.DateTime())

# TODO: Enable charges
# TODO: display licenses
# TODO: Create records


@app.route('/')
def index():
    return render_template('index.jade')


@app.route('/about')
def about():
    return render_template('about.jade')

@app.route('/charge', methods=['POST'])
def charge():
    pass

@app.route('/purchase')
def purchase():
    return render_template('purchase.jade')

@app.route('/create')
def create():
    return render_template('create.jade', token=None)


@app.route('/register', methods=['POST'])
def register_license():
    url = request.form['url']
    amount = request.form['amount']
    token = request.form['token']

    success = True
    justification = ''

    if LicenseTerms.query.filter_by(url=url).all():
        success = False
        justification = 'That image has already been registered'

    new = LicenseTerms()
    new.amount = amount
    new.owner_stripe_token = token
    new.image_url = url
    new.time_recorded = datetime.datetime.now()

    db.session.add(new)
    db.session.commit()
    return render_template('creation-outcome.jade', success=success, justification=justification)


@app.route('/oauth/callback')
def callback():
    code = request.args.get('code')
    data = {'grant_type': 'authorization_code',
            'client_id': app.config['CLIENT_ID'],
            'client_secret': app.config['API_KEY'],
            'code': code}

    # Make /oauth/token endpoint POST request
    url = app.config['SITE'] + app.config['TOKEN_URI']
    print("URL")
    print(url)
    resp = requests.post(url, params=data)
    print("RESP")
    print(resp)

    # Grab access_token (use this as your user's API key)
    resp = resp.json()
    token = resp.get('access_token', None)
    username = resp.get('stripe_user_id', "(Didn't get an ID from Stripe)")
    return render_template('create.jade', token=token, username=username)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.jade'), 404


if __name__ == '__main__':
    app.run(debug=True)
