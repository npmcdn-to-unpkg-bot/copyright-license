import os
import stripe

# Miscellaneous
DEBUG = os.environ.get('DEBUG', False)

# Database
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# File Upload
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

# Stripe
STRIPE_SITE = 'https://connect.stripe.com'
STRIPE_TOKEN_URI = '/oauth/token'
STRIPE_CLIENT_ID = os.environ.get('STRIPE_CLIENT_ID')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')