from copyright import app

import os
import stripe

app.config['CLIENT_ID'] = os.environ['CLIENT_ID']
app.config['DEBUG'] = os.environ.get('DEBUG', False)
app.config['SITE'] = 'https://connect.stripe.com'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['TOKEN_URI'] = '/oauth/token'
app.config['UPLOAD_FOLDER'] = '/tmp/copyright'
app.config['REDIS_URL'] = os.environ['REDIS_URL']
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

stripe_keys = {
    'secret_key': os.environ['SECRET_KEY'],
    'publishable_key': os.environ['PUBLISHABLE_KEY']
}
stripe.api_key = stripe_keys['secret_key']


