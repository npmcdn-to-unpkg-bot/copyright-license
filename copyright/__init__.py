from flask import Flask
from werkzeug import secure_filename
app = Flask(__name__)

import copyright.views
