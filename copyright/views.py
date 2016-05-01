from copyright import app, db
from copyright.models import *
from werkzeug import secure_filename

import requests, datetime, stripe, sys
from flask import session, render_template, request, jsonify, Response, redirect, url_for
from sqlalchemy import desc
from math import ceil

# required for file upload
from hashlib import sha1
import time, json, base64, hmac, urllib

import boto
from PIL import Image as PIL
import StringIO

# to print debug statements to Heroku console:
# import sys
# print "statement"
# sys.stdout.flush()
# source: http://stackoverflow.com/questions/12504588/

images_per_page = 15

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    images = []
    if request.method == 'POST' and request.form['searchText'] != '':
        searchText = '%' + request.form['searchText'] + '%'
        images = Image.query.filter(Image.description.like(searchText)) \
                            .order_by(desc(2*Image.num_purchases + Image.num_clicks)) \
                            .all()
    else: # GET
        images = Image.query.order_by(desc(2*Image.num_purchases + Image.num_clicks)).all()
    pages = list(range(1, int(ceil(len(images) / float(images_per_page)) + 1)))
    return render_template('search.html', images=images[0:images_per_page], pages=pages)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    newFeedback = Feedback()
    newFeedback.input = request.form['feedback']
    db.session.add(newFeedback)
    db.session.commit()
    return redirect(url_for('about'))

@app.route('/charge', methods=['POST'])
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

    is_commercial = False
    if license.allow_commercial:
        is_commercial = (request.form['is_commercial'] == 'True')

    is_derivative = False
    if license.allow_derivative:
        is_derivative = (request.form['is_derivative'] == 'True')

    stripe.api_key = app.config['STRIPE_SECRET_KEY']

    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        card=request.form['tokenId']
    )

    newReceipt = Receipt()
    newReceipt.license_id = license_id
    newReceipt.image_id = image_id
    newReceipt.transaction_date = datetime.datetime.now()
    newReceipt.is_commercial = is_commercial
    newReceipt.is_derivative = is_derivative
    newReceipt.stripe_email = customer.email

    # calculate price
    total_price = license.price_base
    if is_commercial:
        total_price += license.price_commercial
    if is_derivative:
        total_price += license.price_derivative
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


@app.route('/purchase/<int:image_id>')
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


@app.route('/create')
def create():
    return render_template('create.html', token=None)


@app.route('/sign_s3')
def sign_s3():
    AWS_ACCESS_KEY = app.config['AWS_ACCESS_KEY_ID']
    AWS_SECRET_KEY = app.config['AWS_SECRET_ACCESS_KEY']
    S3_BUCKET = app.config['AWS_S3_BUCKET_NAME']

    object_name = urllib.quote_plus(request.args.get('file_name'))
    mime_type = request.args.get('file_type')

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
    imageFile = request.files['imageFile']

    success = True
    justification = ''

    if imageFile and allowed_file(imageFile.filename):

        # get form params
        stripe_id = request.form['stripe_id']
        allow_commercial = request.form['allow_commercial']
        allow_derivative = request.form['allow_derivative']
        price_base = request.form['price_base']
        price_commercial = request.form['price_commercial']
        price_derivative = request.form['price_derivative']
        description = request.form['description']

        # process image
        filename_full = secure_filename(imageFile.filename)
        s3 = boto.connect_s3()
        bucket = s3.get_bucket(app.config['AWS_S3_BUCKET_NAME'])

        if bucket.get_key(filename_full) != None:
            # TODO: if we randomize the image URLs, then we can't do this simple
            #   check anymore. Perhaps we should consider hashing?
            success = False
            justification = 'That image has already been registered'

        else:
            key = bucket.new_key(filename_full)
            key.set_contents_from_file(imageFile)
            key.set_acl("public-read")
            
            # create thumbnail
            output = StringIO.StringIO()
            try:
                im = PIL.open(imageFile)
                im.thumbnail((200,200), PIL.ANTIALIAS)
                im.convert('RGB').save(output, "JPEG")
            except Exception as e: 
                success = False
                justification = str(e)

            filename_thumb = filename_full + "_thumb200.jpg"
            key_thumb = bucket.new_key(filename_thumb)
            key_thumb.set_contents_from_string(output.getvalue(), headers={"Content-Type": "image/jpeg"})
            key_thumb.set_acl("public-read")
            
            url_full = key.generate_url(expires_in=0, query_auth=False)
            url_thumb = key_thumb.generate_url(expires_in=0, query_auth=False)

            now = datetime.datetime.now()

            # check if user already exists
            # TODO: once we implement a user login system, this needs to be
            #   largely redone
            creator = User.query.filter_by(stripe_id=stripe_id).first()
            if not creator:
                creator = User()
                creator.stripe_id = stripe_id
                creator.date_created = now
                creator.active = True
                db.session.add(creator)
                db.session.commit()

            newImage = Image()
            newImage.creator_id = creator.id
            newImage.url_full = url_full
            newImage.url_thumb = url_thumb
            newImage.date_uploaded = now
            newImage.description = description
            # newImage.tags = "" # TODO
            newImage.num_clicks = 0
            newImage.num_purchases = 0

            newLicense = License()
            newLicense.image = newImage
            newLicense.creator = creator
            newLicense.active = True
            newLicense.date_created = now
            newLicense.allow_commercial = allow_commercial
            newLicense.allow_derivative = allow_derivative
            newLicense.price_base = price_base
            newLicense.price_commercial = price_commercial
            newLicense.price_derivative = price_derivative

            db.session.add(newImage)
            db.session.add(newLicense)
            db.session.commit()

    else:
        success = False
        justification = 'Invalid Image File'

    return render_template('creation-outcome.html', success=success, justification=justification)


@app.route('/oauth/callback')
def callback():
    code = request.args.get('code')
    data = {'grant_type': 'authorization_code',
            'client_id': app.config['STRIPE_CLIENT_ID'],
            'client_secret': app.config['STRIPE_SECRET_KEY'],
            'code': code}

    # Make /oauth/token endpoint POST request
    url = app.config['STRIPE_SITE'] + app.config['STRIPE_TOKEN_URI']
    resp = requests.post(url, params=data)

    # Grab access_token (use this as your user's API key)
    resp = resp.json()
    token = resp.get('access_token', None)
    stripe_id = resp.get('stripe_user_id', "(Didn't get an ID from Stripe)")
    access_key = resp.get('stripe_publishable_key', None)
    return render_template('create.html', token=token, stripe_id=stripe_id, stripe_key=access_key)

@app.route('/page')
def page():
    page_num = int(request.args.get('page'))
    images = Image.query.filter_by().all()
    result = []
    start = (page_num - 1) * images_per_page
    end = min(page_num * images_per_page, len(images))
    for i in range(start, end):
        result.append({
            'id' : images[i].id,
            'url': images[i].url_thumb,
        })
    return(jsonify(result=result))

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']