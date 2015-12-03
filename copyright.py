import app.models
import app.views

import datetime
import os
import requests
import stripe

# update the license registration with more possible terms
# TODO turn stripe on for real

if __name__ == '__main__':
    app.run(debug=True)
