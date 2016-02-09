from copyright import db

class Image(db.Model):
    """
    Information associated with each image
    """
    __tablename__ = "image" # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    license_id = db.Column(db.Integer, db.ForeignKey('license.id'))
    date_uploaded = db.Column(db.DateTime())
    filename_full = db.Column(db.String(), unique=True)
    filename_thumb = db.Column(db.String(), unique=True)
    tags = db.Column(db.String())
    num_clicks = db.Column(db.Integer)
    num_purchases = db.Column(db.Integer)

    # optional fields
    description = db.Column(db.String())
    location_take = db.Column(db.String())
    date_taken = db.Column(db.DateTime())


class User(db.Model):
    """
    Information about each user, for both clients and photographers
    """
    __tablename__ = 'user' # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    stripe_id = db.Column(db.String())
    date_created = db.Column(db.DateTime())
    active = db.Column(db.Boolean)
    
    # optional fields
    profilePic_filename = db.Column(db.String())
    
    # future fields
    # email = db.Column(db.String())
    # password = db.Column(db.String())
    # name = db.Column(db.String())


class License(db.Model):
    """
    The terms under which an image can be licensed
    """
    __tablename__ = "license" # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    active = db.Column(db.Boolean)
    date_created = db.Column(db.DateTime())
    duration_days = db.Column(db.Integer)
    price_low = db.Column(db.Integer) # low number of views
    price_high = db.Column(db.Integer) # high number of views
    
    image_id = db.Column(db.Integer, db.ForeignKey('image.id')) # not sure if this is necessary
    
    # optional fields
    # none

class Receipt(db.Model):
    """
    License purchase receipts
    """
    __tablename__ = "receipt" # this matches the default
    
    # required fields
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transaction_date = db.Column(db.DateTime())
    expiration_date = db.Column(db.DateTime())
    price = db.Column(db.Integer)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    
    # optional fields
    # none