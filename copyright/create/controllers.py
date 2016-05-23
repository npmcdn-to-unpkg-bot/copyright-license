from flask import Blueprint, request, render_template, jsonify

from copyright import db
from copyright.models import *

import requests, datetime, stripe, sys, json

# required for S3 storage and image processing
import os, hashlib, boto, StringIO, math
from werkzeug import secure_filename
from PIL import Image as PilImage # don't want Image to conflict with our Image() model class
from PIL import ImageDraw, ImageFont, ImageEnhance

# to print debug statements to Heroku console:
# import sys
# print "statement"
# sys.stdout.flush()
# source: http://stackoverflow.com/questions/12504588/

createRoutes = Blueprint('createRoutes', __name__)
app = createRoutes

@createRoutes.record
def record_params(setup_state):
  global app
  app = setup_state.app

@createRoutes.route('/create')
def create():
    return render_template('create.html', token=None)

@createRoutes.route('/register', methods=['POST'])
def register_license():
    imageFile = request.files['imageFile']
    import sys
    print 'test'
    sys.stdout.flush()
    success = True
    justification = ''

    if imageFile and allowed_file(imageFile.filename):

        # calculate SHA1 hash of image file
        sha1_hash = hashlib.sha1(imageFile.read()).hexdigest()
        import sys
        print sha1_hash
        sys.stdout.flush()
        if Image.query.filter_by(sha1_hash=sha1_hash).first() != None:
            success = False
            justification = 'That image has already been registered'

        else:
            # get form params
            for key in request.form:
                print key
            sys.stdout.flush()
            stripe_id = request.form['stripe_id']
            categories = request.form['categories']
            edit_privilege = request.form['edit_privilege']
            credit_type = request.form['credit_type']
            credit_receiver = request.form['credit_receiver']
            keywords = request.form['keywords']
            price_internal_1 = request.form['price11']
            price_internal_2_50 = request.form['price21']
            price_internal_51 = request.form['price31']
            price_external_1 = request.form['price12']
            price_external_2_50 = request.form['price22']
            price_external_51 = request.form['price32']
            print 'test'
            sys.stdout.flush()

            # process image
            filename_full = secure_filename(sha1_hash+getFileExt(imageFile.filename))
            
            # create thumbnail
            # thumbnailImageAsString is of type StringIO
            thumbnailImageAsString = None
            try:
                thumbnailImageAsString = createThumbnailWithWatermark(imageFile)
                print "Created watermarked image thumbnail"
                sys.stdout.flush()
            except Exception as e:
                print "Reached exception"
                sys.stdout.flush()
                success = False
                justification = str(e)

            print 'test'
            sys.stdout.flush()

            # reset cursor of image file after reading it to create the thumbnail
            imageFile.seek(0)

            # connect to Amazon S3
            s3 = boto.connect_s3()
            bucket = s3.get_bucket(app.config['AWS_S3_BUCKET_NAME'])

            print 'test'
            sys.stdout.flush()

            # upload full image
            key = bucket.new_key(filename_full)
            key.set_contents_from_file(imageFile)
            key.set_acl("public-read")

            # upload thumbnail image
            filename_thumb = filename_full + "_thumb200.jpg"
            key_thumb = bucket.new_key(filename_thumb)
            key_thumb.set_contents_from_string(thumbnailImageAsString, headers={"Content-Type": "image/jpeg"})
            key_thumb.set_acl("public-read")

            print 'test'
            sys.stdout.flush()
            
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
            newImage.sha1_hash = sha1_hash
            newImage.creator_id = creator.id
            newImage.url_full = url_full
            newImage.url_thumb = url_thumb
            newImage.date_uploaded = now
            newImage.keywords = keywords
            newImage.categories = categories
            newImage.num_clicks = 0
            newImage.num_purchases = 0

            newLicense = License()
            newLicense.image = newImage
            newLicense.creator = creator
            newLicense.active = True
            newLicense.date_created = now
            newLicense.price_internal_1 = price_internal_1
            newLicense.price_internal_2_50 = price_internal_2_50
            newLicense.price_internal_51 = price_internal_51
            newLicense.price_external_1 = price_external_1
            newLicense.price_external_2_50 = price_external_2_50
            newLicense.price_external_51 = price_external_51

            db.session.add(newImage)
            db.session.add(newLicense)
            db.session.commit()

    else:
        success = False
        justification = 'Invalid Image File'

    return render_template('creation-outcome.html', success=success, justification=justification)


@createRoutes.route('/oauth/callback')
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
    return render_template('create.html', token=token, stripe_id=stripe_id, stripe_key=access_key,
        licensing_protocol=json.load(open('./copyright/static/survey/licensing-protocol.json', 'rb')))

## Helper Functions
def allowed_file(filename):
    return '.' in filename and \
       filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# generate random string of length N
def randomString(N):
    choices = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(choices) for _ in range(N))

# get file extension (including the dot): "picture.jpg" -> ".jpg"
def getFileExt(filename):
    return os.path.splitext(filename)[1]

# create a watermarked thumbnail of the given image, returns it as a binary string
# for convenient upload to Amazon S3
# - source: http://pythoncentral.io/watermark-images-python-2x/
def createThumbnailWithWatermark(imageFile, text="COPYRIGHT", opacity=0.5):
    output = StringIO.StringIO()
    FONT = 'arial.ttf'

    # scale image to fit in 200x200 square, while preserving its aspect ratio
    img = PilImage.open(imageFile).convert('RGB')
    img.thumbnail((200,200), PilImage.ANTIALIAS)

    # create empty image on which we will create the watermark
    watermark = PilImage.new('RGBA', img.size, (0,0,0,0))

    # determine the maximum font size that will fit the image
    # try to use the Arial font, but otherwise use whatever is available
    n_font = None
    n_width, n_height, size = 0
    try:
        # iteratively increase the font size until it is larger than fits
        while (n_width+n_height < watermark.size[0]) or (n_width+n_height < watermark.size[1]):
            size += 1
            n_font = ImageFont.truetype(FONT, size)
            n_width, n_height = n_font.getsize(text)

        # decrease the font size back to what fits
        size -= 1
        n_font = ImageFont.truetype(FONT, size)
    except Exception as e:
        n_font = ImageFont.load_default()
        n_width, n_height = n_font.getsize(text)

    # draw the watermark onto the image
    draw = ImageDraw.Draw(watermark, 'RGBA')
    draw.text(((watermark.size[0] - n_width) / 2,
              (watermark.size[1] - n_height) / 2),
              text, font=n_font)

    # angle the watermark from the bottom left to top right
    angle = math.atan2(watermark.size[1], watermark.size[0]) * 180 / math.pi
    watermark = watermark.rotate(angle,PilImage.BICUBIC)

    # add the correct opacity to the watermark
    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)

    # combine the watermark with the image, then save it to the output binary string
    PilImage.composite(watermark, img, watermark).save(output, 'JPEG')
    return output.getvalue()