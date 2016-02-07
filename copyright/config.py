from copyright import app

import os
import stripe

# Miscellaneous
app.config['DEBUG'] = os.environ.get('DEBUG', False)
app.config['TOKEN_URI'] = '/oauth/token'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# File Upload
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = '/tmp/copyright'
app.config['REDIS_URL'] = os.environ.get('REDIS_URL')

# Stripe
app.config['SITE'] = 'https://connect.stripe.com'
app.config['CLIENT_ID'] = os.environ.get('CLIENT_ID')
stripe_keys = {
    'secret_key': os.environ.get('SECRET_KEY'),
    'publishable_key': os.environ.get('PUBLISHABLE_KEY')
}
stripe.api_key = stripe_keys['secret_key']