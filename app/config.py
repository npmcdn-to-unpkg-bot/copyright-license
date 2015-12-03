import os

from flask import Flask

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
