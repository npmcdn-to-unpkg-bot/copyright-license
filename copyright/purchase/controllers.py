from flask import Blueprint, session, request, render_template

from copyright import db
from copyright.models import *

import datetime, stripe, sys

# to print debug statements to Heroku console:
# import sys
# print "statement"
# sys.stdout.flush()
# source: http://stackoverflow.com/questions/12504588/

purchaseRoutes = Blueprint('purchaseRoutes', __name__)
app = purchaseRoutes

@purchaseRoutes.record
def record_params(setup_state):
  global app
  app = setup_state.app


@purchaseRoutes.route('/charge', methods=['POST'])
def charge():
    print "BEGINNING CHARGE"
    sys.stdout.flush()

    # error checking
    if ('current_image_id' not in session) or ('current_license_id' not in session):
        # TODO: actually handle the error
        print "Error: image ID or license ID not found in session"
        sys.stdout.flush()

    license_id = int(request.form['licenseId'])
    image_id = int(request.form['imageId'])

    if (license_id != session['current_license_id']) or (image_id != session['current_image_id']):
        # TODO: actually handle the error
        print "Error: mismatch between session and form submission for image ID or license ID"
        sys.stdout.flush()

    license = License.query.get(license_id)
    image = Image.query.get(image_id)

    if (license.image_id != image_id) or (image.license.id != license_id):
        # TODO: actually handle the error
        print "Error: mismatch between image and license"
        sys.stdout.flush()

    image.num_purchases += 1

    # is_commercial = False
    # if license.allow_commercial:
    #     is_commercial = (request.form['is_commercial'] == 'True')

    # is_derivative = False
    # if license.allow_derivative:
    #     is_derivative = (request.form['is_derivative'] == 'True')

    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        card=request.form['tokenId']
    )

    newReceipt = Receipt()
    newReceipt.license_id = license_id
    newReceipt.image_id = image_id
    newReceipt.transaction_date = datetime.datetime.now()
    # newReceipt.is_commercial = is_commercial
    # newReceipt.is_derivative = is_derivative
    newReceipt.stripe_email = customer.email

    # calculate price
    total_price = license.price_internal_1
    # if is_commercial:
    #     total_price += license.price_commercial
    # if is_derivative:
    #     total_price += license.price_derivative
    newReceipt.price = total_price

    if Receipt.query.filter_by(license_id=newReceipt.license_id, stripe_email=newReceipt.stripe_email).all():
        success = False
        justification = "You've already purchased a license for this image."
        download = True
    else:
        try:
            completed_charge = stripe.Charge.create(
                customer=customer.id,
                amount=total_price,
                currency='usd',
                description='License Purchase',
                destination=license.creator.stripe_id
            )
            db.session.add(newReceipt)
            db.session.commit()
            success = True
            download = True
            justification = "You've paid %d cents" % total_price
        except stripe.InvalidRequestError as e:
            print(e)
            sys.stdout.flush()
            success = False
            download = True
            justification = "The most likely reason the purchase failed is that you tried to buy your own photo. In the meantime, feel free to download your own photo below. The error message is as follows: " + str(e)

    return render_template('charge.html', success=success, justification=justification, url_full=license.image.url_full, download=download)


@purchaseRoutes.route('/purchase/<int:image_id>')
def purchase(image_id):
    image = Image.query.get(image_id)
    if not image:
        return render_template('404.html')
    license = License.query.filter_by(image_id=image_id).first()
    if not license:
        return render_template('404.html')
    image.num_clicks += 1
    db.session.commit()
    session['current_image_id'] = image.id
    session['current_license_id'] = image.license.id
    return render_template('purchase.html', image=image, license=license, api_key=app.config['STRIPE_PUBLISHABLE_KEY'])