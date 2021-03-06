from flask import Blueprint, request, render_template, jsonify, redirect, url_for

from copyright import db
from copyright.models import *

from sqlalchemy import desc
from math import ceil

import sys

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

# to print debug statements to Heroku console:
# import sys
# print "statement"
# sys.stdout.flush()
# source: http://stackoverflow.com/questions/12504588/

homeRoutes = Blueprint('homeRoutes', __name__)
app = homeRoutes

images_per_page = 15

@homeRoutes.record
def record_params(setup_state):
  global app
  app = setup_state.app


@homeRoutes.route('/')
def index():
    return render_template('index.html')


@homeRoutes.route('/login')
def login():
    return render_template('login.html')


@homeRoutes.route('/search')
def search():
    searchText = '%' + request.args.get('searchText') + '%'
    category = request.args.get('category')

    # use ilike() to get case-insensitive search
    images = Image.query.filter(Image.keywords.ilike(searchText))

    if category and int(category) != -1:
        images = images.filter(Image.categories.any(id=int(category)))

    images = images.order_by(desc(2*Image.num_purchases + Image.num_clicks)) \
                   .all()
    pages = list(range(1, int(ceil(len(images) / float(images_per_page)) + 1)))
    return render_template('search.html', images=images[0:images_per_page], pages=pages)


@homeRoutes.route('/page')
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
    return jsonify(result=result)


@homeRoutes.route('/about', methods=['GET'])
def about():
    feedback = Feedback.query.all()
    return render_template('about.html', feedback=feedback)


@homeRoutes.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    newFeedback = Feedback()
    newFeedback.input = request.form['feedback']
    db.session.add(newFeedback)

    fromaddr = "copyrightfeedback@gmail.com"
    toaddr = ['chrisyeh@stanford.edu', 'rbarcelo@stanford.edu']
    COMMASPACE = ', '
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = COMMASPACE.join(toaddr)
    msg['Subject'] = "You've received new feedback."
    body = "According to one user, \"" + request.form['feedback'] + "\""
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, app.config['EMAIL_PASSWORD'])
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()

    db.session.commit()
    return redirect(url_for('homeRoutes.about'))


@homeRoutes.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404