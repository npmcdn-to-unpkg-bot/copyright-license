from copyright import db

class Image(db.Model):
    """
    Information associated with each image
    """
    __tablename__ = 'images' # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # license_id = db.Column(db.Integer, db.ForeignKey('licenses.id'))
    date_uploaded = db.Column(db.DateTime())
    url_full = db.Column(db.String(), unique=True)
    url_thumb = db.Column(db.String(), unique=True)
    tags = db.Column(db.String())
    num_clicks = db.Column(db.Integer)
    num_purchases = db.Column(db.Integer)

    # optional fields
    category = db.Column(db.String())
    description = db.Column(db.String())
    location_take = db.Column(db.String())
    date_taken = db.Column(db.DateTime())

    # relationships
    creator = db.relationship('User', back_populates='created_images')
    license = db.relationship('License', back_populates='image', uselist=False)
    receipts = db.relationship('Receipt', back_populates='image')

    # TODO: should each image be associate with only 1 license? what if we want
    #   to create a new license for an existing image? or what if we want to
    #   edit an existing license?


class User(db.Model):
    """
    Information about each user, for both clients and photographers
    """
    __tablename__ = 'users' # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime())
    active = db.Column(db.Boolean)
    
    # optional fields
    profilePic_filename = db.Column(db.String())
    stripe_id = db.Column(db.String())

    # relationships
    created_images = db.relationship('Image', back_populates='creator')
    created_licenses = db.relationship('License', back_populates='creator')
    
    # future fields
    # name = db.Column(db.String())
    # email = db.Column(db.String(120), index=True, unique=True)
    # password = db.Column(db.String())
    # name = db.Column(db.String())

    def __repr__(self):
        return '<User %r>' % (self.id)

class License(db.Model):
    """
    The terms under which an image can be licensed
    """
    __tablename__ = 'licenses' # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    active = db.Column(db.Boolean)
    date_created = db.Column(db.DateTime()) # date that license was created
    credit_type = db.Column(db.Integer)
        # 0: Do not want credit
        # 1: Image Already Includes Credit (e.g., watermark, embedded credit)
        # 2: Text Near the Image (e.g., text at the website)
    credit_entity = db.Column(db.String())
        # only filled out if "Text Near the Image" is selected
    allow_commercial = db.Column(db.Boolean)
    allow_derivative = db.Column(db.Integer)
        # 0: No edits allowed
        # 1: Edits allowed
        # 2: Minor edits only (e.g., crop, color shift, resize)
    price_base = db.Column(db.Integer)
    price_commercial = db.Column(db.Integer)
    price_derivative = db.Column(db.Integer)
    
    # relationships
    image = db.relationship('Image', back_populates='license')
    creator = db.relationship('User', back_populates='created_licenses')
    receipts = db.relationship('Receipt', back_populates='license')

    # optional fields
    # none

    # future fields

class Receipt(db.Model):
    """
    License purchase receipts
    """
    __tablename__ = 'receipts' # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    license_id = db.Column(db.Integer, db.ForeignKey('licenses.id'))
    transaction_date = db.Column(db.DateTime())
    is_commercial = db.Column(db.Boolean)
    is_derivative = db.Column(db.Boolean)
    price = db.Column(db.Integer)
    stripe_email = db.Column(db.String())

    # relationships
    image = db.relationship('Image', back_populates='receipts')
    license = db.relationship('License', back_populates='receipts')
    
    # optional fields
    # none

    # future fields

class Feedback(db.Model):
    """
    User feedback from "About" page
    """
    __tablename__ = 'feedback' # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.String())

    # relationships
    
    # optional fields
    # none

    # future fields