from flask import render_template
from flask_pymongo import PyMongo
from app import app

app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)

@app.route("/")
def home_page():
    dj = mongo.db.dj_meta_info.find_one()
    return render_template("index.html",
        dj=dj)

@app.route("/index")
def index():
    return "index"