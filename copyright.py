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

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

db = SQLAlchemy(app)


class LicenseTerms(db.Model):
    """
    The terms under which an image can be licensed
    """
    __tablename__ = "terms"
    id = db.Column(db.Integer, primary_key=True)
    owner_stripe_id = db.Column(db.String())
    amount = db.Column(db.Integer())
    image_url = db.Column(db.String())
    time_recorded = db.Column(db.DateTime())


class License(db.Model):
    """
    A record of users who have paid for a license
    """
    __tablename__ = "licenses"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String())
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    time_recorded = db.Column(db.DateTime())


# TODO: make license logic match the layout
# update the registration
# update the purchasing

@app.route('/')
def index():
    return render_template('index.jade')


@app.route('/about')
def about():
    return render_template('about.jade')


@app.route('/charge', methods=['POST'])
def charge():
    term_id = request.form['termId']
    result = LicenseTerms.query.get(term_id)

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        card=request.form['stripeToken']
    )

    new = License()
    new.term_id = term_id
    new.time_recorded = datetime.datetime.now()
    new.user = customer.email

    if License.query.filter_by(term_id=new.term_id, user=new.user).all():
        success = False
        justification = "You've already purchased a license for this image."
    else:
        completed_charge = stripe.Charge.create(
            customer=customer.id,
            amount=result.amount,
            currency='usd',
            description='Flask Charge',
            destination=result.owner_stripe_id
        )

        db.session.add(new)
        db.session.commit()
        success = True
        justification = "You've paid %d cents" % result.amount

    return render_template('charge.jade', success=success, justification=justification)


@app.route('/purchase')
def purchase():
    licenses = LicenseTerms.query.filter_by().all()
    return render_template('purchase.jade', licenses=licenses, api_key=stripe_keys['publishable_key'])


@app.route('/create')
def create():
    return render_template('create.jade', token=None)


@app.route('/register', methods=['POST'])
def register_license():
    url = request.form['url']
    amount = request.form['amount']  # TODO convert to dollars
    stripe_user_id = request.form['id']

    success = True
    justification = ''

    if LicenseTerms.query.filter_by(image_url=url).all():
        success = False
        justification = 'That image has already been registered'
    else:
        new = LicenseTerms()
        new.amount = amount
        new.owner_stripe_id = stripe_user_id
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
            'client_secret': stripe_keys['secret_key'],
            'code': code}

    # Make /oauth/token endpoint POST request
    url = app.config['SITE'] + app.config['TOKEN_URI']
    resp = requests.post(url, params=data)

    # Grab access_token (use this as your user's API key)
    resp = resp.json()
    token = resp.get('access_token', None)
    username = resp.get('stripe_user_id', "(Didn't get an ID from Stripe)")
    access_key = resp.get('stripe_publishable_key', None)
    return render_template('create.jade', token=token, stripe_username=username, stripe_key=access_key)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.jade'), 404


if __name__ == '__main__':
    app.run(debug=True)
