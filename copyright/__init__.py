from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from copyright import models

from copyright.home.controllers import homeRoutes
app.register_blueprint(homeRoutes)

from copyright.create.controllers import createRoutes
app.register_blueprint(createRoutes)

from copyright.purchase.controllers import purchaseRoutes
app.register_blueprint(purchaseRoutes)