from flask import render_template, flash, redirect
from flask_pymongo import PyMongo
from app import app
from app.forms import LoginForm

app.config["MONGO_URI"] = "mongodb://localhost:27017/whosampled"
mongo = PyMongo(app)

@app.route("/")
@app.route("/index")
def index():
    dj = mongo.db.dj_meta_info.find_one({}, {"dj": 1, "_id": 0})
    djs = mongo.db.dj_meta_info.find({}, {"dj": 1, "_id": 0}).limit(5)
    return render_template("index.html",
        dj=dj, djs =djs)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login Requested for {}, remember_me = {}'.format(
                form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title = 'Sign In', form = form)