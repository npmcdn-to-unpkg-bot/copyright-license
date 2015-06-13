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
    image_url = db.Column(db.String())
    time_recorded = db.Column(db.DateTime())


class PaymentAmount(db.Model):
    __tablename__ = "payment_amounts"
    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    minimum_views = db.Column(db.Integer)
    maximum_views = db.Column(db.Integer)
    cents = db.Column(db.Integer)


class LicenseReceipt(db.Model):
    """
    A record of users who have paid for a license
    """
    __tablename__ = "receipts"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String())
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    time_recorded = db.Column(db.DateTime())
    minimum_views = db.Column(db.Integer)
    maximum_views = db.Column(db.Integer)
    for_profit = db.Column(db.Boolean)


# update the license registration with more possible terms
# TODO turn stripe on for real

@app.route('/')
def index():
    licenses = LicenseTerms.query.filter_by().all()
    return render_template('index.jade', licenses=licenses)


@app.route('/about')
def about():
    return render_template('about.jade')


@app.route('/charge', methods=['POST'])
def charge():
    term_id = request.form['termId']
    payment_amount_id = request.form['paymentAmountId']
    for_profit = request.form['profitRadios']

    result = LicenseTerms.query.get(term_id)
    selected_payment = PaymentAmount.query.get(payment_amount_id)

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        card=request.form['tokenId']
    )

    new = LicenseReceipt()
    new.term_id = term_id
    new.time_recorded = datetime.datetime.now()
    new.user = customer.email
    new.minimum_views = selected_payment.minimum_views
    new.maximum_views = selected_payment.maximum_views

    if LicenseReceipt.query.filter_by(term_id=new.term_id, user=new.user).all():
        success = False
        justification = "You've already purchased a license for this image."
    else:
        completed_charge = stripe.Charge.create(
            customer=customer.id,
            amount=selected_payment.cents,
            currency='usd',
            description='License Purchase',
            destination=result.owner_stripe_id
        )
        db.session.add(new)
        db.session.commit()
        success = True
        justification = "You've paid %d cents" % selected_payment.cents

    return render_template('charge.jade', success=success, justification=justification)


@app.route('/purchase/<int:term_id>')
def purchase(term_id):
    license_terms = LicenseTerms.query.get(term_id)
    if not license_terms:
        return render_template('404.jade')
    payment_amounts = PaymentAmount.query.filter_by(term_id=term_id)
    if not payment_amounts:
        return render_template('404.jade')
    return render_template('purchase.jade', terms=license_terms, payments=payment_amounts, api_key=stripe_keys['publishable_key'])


@app.route('/create')
def create():
    return render_template('create.jade', token=None)


@app.route('/register', methods=['POST'])
def register_license():
    url = request.form['url']
    amount = request.form['amount']
    stripe_user_id = request.form['id']

    success = True
    justification = ''

    if LicenseTerms.query.filter_by(image_url=url).all():
        success = False
        justification = 'That image has already been registered'
    else:
        new = LicenseTerms()
        new.owner_stripe_id = stripe_user_id
        new.image_url = url
        new.time_recorded = datetime.datetime.now()

        db.session.add(new)
        db.session.commit()

        payment = PaymentAmount()
        payment.minimum_views = 0
        payment.maximum_views = 1000
        payment.cents = amount
        payment.term_id = new.id
        db.session.add(payment)

        payment_two = PaymentAmount()
        payment_two.minimum_views = 1001
        payment_two.maximum_views = 10000
        payment_two.cents = int(amount)*2
        payment_two.term_id = new.id

        db.session.add(payment_two)
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
