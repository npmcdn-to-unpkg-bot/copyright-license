from copyright import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class LicenseTerms(db.Model):
    """
    The terms under which an image can be licensed
    """
    __tablename__ = "terms"
    id = db.Column(db.Integer, primary_key=True)
    owner_stripe_id = db.Column(db.String())
    image_url = db.Column(db.String())
    time_recorded = db.Column(db.DateTime())


class PaymentAmount(db.Model):
    __tablename__ = "payment_amounts"
    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    minimum_views = db.Column(db.Integer)
    maximum_views = db.Column(db.Integer)
    cents = db.Column(db.Integer)


class LicenseReceipt(db.Model):
    """
    A record of users who have paid for a license
    """
    __tablename__ = "receipts"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String())
    term_id = db.Column(db.Integer, db.ForeignKey('terms.id'))
    time_recorded = db.Column(db.DateTime())
    minimum_views = db.Column(db.Integer)
    maximum_views = db.Column(db.Integer)
    for_profit = db.Column(db.Boolean)
