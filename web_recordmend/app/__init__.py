'''
A subdirectory that contains a __init__.py is considered a package, and can be 
imported. So when we import the app package, we get the variables inside of these
files.
'''

from flask import Flask

import os

#app object is an instance of Flask class
flask_app = Flask(__name__)

SECRET_KEY = os.urandom(32)
flask_app.config['SECRET_KEY'] = SECRET_KEY

#import the routes module
from app import routes