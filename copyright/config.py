from copyright import app

import os
import stripe

app.config['DEBUG'] = True # os.environ.get('DEBUG', False)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
app.config['SITE'] = 'https://connect.stripe.com'
app.config['TOKEN_URI'] = '/oauth/token'
app.config['CLIENT_ID'] = 'test' # os.environ['CLIENT_ID']

stripe_keys = {
    'secret_key': 'test', # os.environ['SECRET_KEY'],
    'publishable_key': 'test' # os.environ['PUBLISHABLE_KEY']
}
stripe.api_key = stripe_keys['secret_key']