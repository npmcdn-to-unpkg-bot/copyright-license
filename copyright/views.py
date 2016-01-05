from copyright import app
from copyright.models import db, LicenseTerms, PaymentAmount, LicenseReceipt
from copyright.config import stripe_keys

import requests, datetime, stripe
from flask import render_template, request

@app.route('/')
def index():
    licenses = LicenseTerms.query.filter_by().all()
    return render_template('index.jade', licenses=licenses)


@app.route('/about')
def about():
    return render_template('about.jade')


@app.route('/charge', methods=['POST'])
def charge():
    print("BEGINNING CHARGE")
    term_id = request.form['termId']
    payment_amount_id = request.form['paymentAmountId']
    for_profit = request.form['profitRadios']

    term = LicenseTerms.query.get(term_id)
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
        download = True
    else:
        try:
            completed_charge = stripe.Charge.create(
                customer=customer.id,
                amount=selected_payment.cents,
                currency='usd',
                description='License Purchase',
                destination=term.owner_stripe_id
            )
            db.session.add(new)
            db.session.commit()
            success = True
            download = True
            justification = "You've paid %d cents" % selected_payment.cents
        except stripe.InvalidRequestError as e:
            print(e)
            success = False
            download = True
            justification = "The most likely reason the purchase failed is that you tried to buy your own photo. Try buying a photo someone else uploaded. In the meantime, feel free to download your own photo below."

    return render_template('charge.jade', success=success, justification=justification, url=term.image_url, download=download)


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
