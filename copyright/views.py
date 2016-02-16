from copyright import app, db
from copyright.models import *
from werkzeug import secure_filename

import requests, datetime, stripe, redis, io
from flask import render_template, request, jsonify, send_file, Response
from math import ceil

# required for file upload
from hashlib import sha1
import time, json, base64, hmac, urllib

images_per_page = 15

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    licenses = []
    if request.method == 'POST' and request.form['searchText'] != '':
        searchText = request.form['searchText']
        licenses = LicenseTerms.query.filter(LicenseTerms.description.match(searchText)).all()
    else: # GET
        licenses = LicenseTerms.query.filter_by().all()
    pages = list(range(1, int(ceil(len(licenses) / float(images_per_page)) + 1)))
    return render_template('search.html', licenses=licenses[0:images_per_page], pages=pages)

@app.route('/about')
def about():
    return render_template('about.html')

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

    return render_template('charge.html', success=success, justification=justification, url=term.image_url, download=download)


@app.route('/purchase/<int:term_id>')
def purchase(term_id):
    license_terms = LicenseTerms.query.get(term_id)
    if not license_terms:
        return render_template('404.html')
    payment_amounts = PaymentAmount.query.filter_by(term_id=term_id)
    if not payment_amounts:
        return render_template('404.html')
    return render_template('purchase.html', terms=license_terms, payments=payment_amounts, api_key=app.config['STRIPE_PUBLISHABLE_KEY'])


@app.route('/create')
def create():
    return render_template('create.html', token=None)


@app.route('/sign_s3/')
def sign_s3():
    print "------------------------------------"
    print "--------Now in sign_s3()------------"
    print "------------------------------------"

    AWS_ACCESS_KEY = app.config['AWS_ACCESS_KEY_ID']
    AWS_SECRET_KEY = app.config['AWS_SECRET_ACCESS_KEY']
    S3_BUCKET = app.config['S3_BUCKET_NAME']

    object_name = urllib.quote_plus(request.args.get('file_name'))
    mime_type = urllib.quote_plus(request.args.get('file_type'))

    print "FILE NAME = '" + object_name + "'"
    print "MIME TYPE = '" + mime_type + "'"

    expires = int(time.time()+60*60*24)
    amz_headers = "x-amz-acl:public-read"

    string_to_sign = "PUT\n\n%s\n%d\n%s\n/%s/%s" % (mime_type, expires, amz_headers, S3_BUCKET, object_name)

    signature = base64.encodestring(hmac.new(AWS_SECRET_KEY.encode(), string_to_sign.encode('utf8'), sha1).digest())
    signature = urllib.quote_plus(signature.strip())

    url = 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, object_name)

    content = json.dumps({
        'signed_request': '%s?AWSAccessKeyId=%s&Expires=%s&Signature=%s' % (url, AWS_ACCESS_KEY, expires, signature),
        'url': url,
    })
    return content


@app.route('/register', methods=['POST'])
def register_license():
    amount = request.form['amount']
    stripe_user_id = request.form['id']
    description = request.form['description']
    # file = request.files['image']
    # r = redis.from_url(app.config['REDIS_URL'])
    # r.set(file.filename, file.read())
    # url = '/uploads/'+file.filename
    url = request.form['image_url']
    print url
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
        new.description = description

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

    return render_template('creation-outcome.html', success=success, justification=justification)


@app.route('/oauth/callback')
def callback():
    code = request.args.get('code')
    data = {'grant_type': 'authorization_code',
            'client_id': app.config['CLIENT_ID'],
            'client_secret': app.config['STRIPE_SECRET_KEY'],
            'code': code}

    # Make /oauth/token endpoint POST request
    url = app.config['SITE'] + app.config['TOKEN_URI']
    resp = requests.post(url, params=data)

    # Grab access_token (use this as your user's API key)
    resp = resp.json()
    token = resp.get('access_token', None)
    username = resp.get('stripe_user_id', "(Didn't get an ID from Stripe)")
    access_key = resp.get('stripe_publishable_key', None)
    return render_template('create.html', token=token, stripe_username=username, stripe_key=access_key)

@app.route('/page')
def page():
    page_num = int(request.args.get('page'))
    licenses = LicenseTerms.query.filter_by().all()
    result = []
    start = (page_num - 1) * images_per_page
    end = min(page_num * images_per_page, len(licenses))
    for i in range(start, end):
        result.append({
            'id' : licenses[i].id,
            'url': licenses[i].image_url,
        })
    return(jsonify(result=result))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    r = redis.from_url(app.config['REDIS_URL'])
    return Response(response=r.get(filename),
                    mimetype="image/jpeg")
    #return send_from_directory(app.config['UPLOAD_FOLDER'],
    #                           filename)
