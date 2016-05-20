from copyright import db

image_categories = db.Table('image_categories',
   db.Column('image_id', db.Integer, db.ForeignKey('images.id'), nullable=False),
   db.Column('category_id', db.Integer, db.ForeignKey('categories.id'), nullable=False),
   db.PrimaryKeyConstraint('image_id', 'category_id')
)

class Category(db.Model):
    """
    Information associated with each image
    """
    __tablename__ = 'categories' # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)

    # backrefs: images

class Image(db.Model):
    """
    Information associated with each image
    """
    __tablename__ = 'images' # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    sha1_hash = db.Column(db.String, unique=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # license_id = db.Column(db.Integer, db.ForeignKey('licenses.id'))
    date_uploaded = db.Column(db.DateTime)
    url_full = db.Column(db.String, unique=True)
    url_thumb = db.Column(db.String, unique=True)
    tags = db.Column(db.String)
    num_clicks = db.Column(db.Integer)
    num_purchases = db.Column(db.Integer)
    keywords = db.Column(db.String)
    date_taken = db.Column(db.DateTime)

    # relationships
    creator = db.relationship('User', back_populates='created_images')
    license = db.relationship('License', back_populates='image', uselist=False)
    receipts = db.relationship('Receipt', back_populates='image')
    categories = db.relationship('Category', secondary=image_categories, backref='images')

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
    date_created = db.Column(db.DateTime)
    active = db.Column(db.Boolean)
    
    # optional fields
    profilePic_filename = db.Column(db.String)
    stripe_id = db.Column(db.String)

    # relationships
    created_images = db.relationship('Image', back_populates='creator')
    created_licenses = db.relationship('License', back_populates='creator')
    
    # future fields
    # name = db.Column(db.String)
    # email = db.Column(db.String(120), index=True, unique=True)
    # password = db.Column(db.String)
    # name = db.Column(db.String)

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
    date_created = db.Column(db.DateTime) # date that license was created
    credit_type = db.Column(db.Integer)
        # 0: Do not want credit
        # 1: Image Already Includes Credit (e.g., watermark, embedded credit)
        # 2: Text Near the Image (e.g., text at the website)
    credit_receiver = db.Column(db.String)
        # only filled out if "Text Near the Image" is selected
    edit_privilege = db.Column(db.Integer)
        # 0: No ("as is" only)
        # 1: Yes (anything)
        # 2: only minor edits

    # in cents
    price_internal_1 = db.Column(db.Integer)
    price_internal_2_50 = db.Column(db.Integer)
    price_internal_51 = db.Column(db.Integer)
    price_external_1 = db.Column(db.Integer)
    price_external_2_50 = db.Column(db.Integer)
    price_external_51 = db.Column(db.Integer)
    
    # relationships
    image = db.relationship('Image', back_populates='license')
    creator = db.relationship('User', back_populates='created_licenses')
    receipts = db.relationship('Receipt', back_populates='license')


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
    transaction_date = db.Column(db.DateTime)
    credit_type = db.Column(db.Integer)
        # 0: Do not want credit
        # 1: Image Already Includes Credit (e.g., watermark, embedded credit)
        # 2: Text Near the Image (e.g., text at the website)
    credit_receiver = db.Column(db.String)
        # only filled out if "Text Near the Image" is selected
    edit_privilege = db.Column(db.Integer)
        # 0: No ("as is" only)
        # 1: Yes (anything)
        # 2: only minor edits
    price = db.Column(db.Integer)
    stripe_email = db.Column(db.String)

    # relationships
    image = db.relationship('Image', back_populates='receipts')
    license = db.relationship('License', back_populates='receipts')


class Feedback(db.Model):
    """
    User feedback from "About" page
    """
    __tablename__ = 'feedback' # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.String)