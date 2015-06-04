import os

from flask import Flask
from flask import render_template
from flask import request
from flask.ext.sqlalchemy import SQLAlchemy

import stripe


app = Flask(__name__)
app.config['DEBUG'] = os.environ.get('DEBUG', False)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

# stripe_keys = {
#     'secret_key': os.environ['SECRET_KEY'],
#     'publishable_key': os.environ['PUBLISHABLE_KEY']
# }
#
# stripe.api_key = stripe_keys['secret_key']

db = SQLAlchemy(app)

@app.route('/')
def index():
    return render_template('index.jade')


@app.route('/about')
def about():
    return render_template('about.jade')

@app.route('/charge', methods=['POST'])
def charge():
    pass

@app.route('/purchase')
def purchase():
    return render_template('purchase.jade')

@app.route('/create')
def create():
    return render_template('create.jade')



@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.jade'), 404


if __name__ == '__main__':
    app.run(debug=True)
