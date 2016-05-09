from flask import Blueprint, request, render_template

from copyright import db
from copyright.models import *

import requests, datetime, stripe, sys

# required for S3 storage and image processing
import os, hashlib, boto, StringIO, math
from werkzeug import secure_filename
from PIL import Image as PilImage
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

    success = True
    justification = ''

    if imageFile and allowed_file(imageFile.filename):

        # calculate SHA1 hash of image file
        sha1_hash = hashlib.sha1(imageFile.read()).hexdigest()

        if Image.query.filter_by(sha1_hash=sha1_hash).first() != None:
            success = False
            justification = 'That image has already been registered'

        else:
            # get form params
            stripe_id = request.form['stripe_id']
            allow_commercial = request.form['allow_commercial']
            allow_derivative = int(request.form['allow_derivative'])
            price_base = request.form['price_base']
            price_commercial = request.form['price_commercial']
            price_derivative = request.form['price_derivative']
            description = request.form['description']

            # process image
            filename_full = secure_filename(sha1_hash+getFileExt(imageFile.filename))
            
            # create thumbnail
            # output is of type StringIO
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

            # reset cursor of image file after reading it to create the thumbnail
            imageFile.seek(0)

            # connect to Amazon S3
            s3 = boto.connect_s3()
            bucket = s3.get_bucket(app.config['AWS_S3_BUCKET_NAME'])

            # upload full image
            key = bucket.new_key(filename_full)
            key.set_contents_from_file(imageFile)
            key.set_acl("public-read")

            # upload thumbnail image
            filename_thumb = filename_full + "_thumb200.jpg"
            key_thumb = bucket.new_key(filename_thumb)
            key_thumb.set_contents_from_string(thumbnailImageAsString, headers={"Content-Type": "image/jpeg"})
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
            newImage.sha1_hash = sha1_hash
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
    return render_template('create.html', token=token, stripe_id=stripe_id, stripe_key=access_key)

@createRoutes.route('/licensing-protocol')
def protocol():
    return jsonify(json.load(open('./copyright/static/survey/licensing-protocol.json', 'rb')))

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

def createThumbnailWithWatermark(imageFile, text="COPYRIGHT", opacity=0.25):
    output = StringIO.StringIO()
    FONT = 'arial.ttf'

    img = PilImage.open(imageFile).convert('RGB')
    img.thumbnail((200,200), PilImage.ANTIALIAS)

    watermark = PilImage.new('RGBA', img.size, (0,0,0,0))
    size = 2

    # Try to load desired FONT file, otherwise just use whatever the default is
    n_font = None
    n_width = None
    n_height = None

    try:
        # determine the maximum font size that will fit the image
        n_font = ImageFont.truetype(FONT, size)
        n_width, n_height = n_font.getsize(text)

        while n_width+n_height < watermark.size[0]:
            size += 2
            n_font = ImageFont.truetype(FONT, size)
            n_width, n_height = n_font.getsize(text)

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

    alpha = watermark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    watermark.putalpha(alpha)

    PilImage.composite(watermark, img, watermark).save(output, 'JPEG')
    return output.getvalue()