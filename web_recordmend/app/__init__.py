from flask import Flask

import os

#app object is an instance of Flask class
flask_app = Flask(__name__)

SECRET_KEY = os.urandom(32)
flask_app.config['SECRET_KEY'] = SECRET_KEY

#import the routes module
from app import routes