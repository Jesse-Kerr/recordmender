from flask import render_template, flash, redirect, request
from flask_pymongo import PyMongo
from app import app
from app.forms import LoginForm
import pandas as pd

app.config["MONGO_URI"] = "mongodb://localhost:27017/whosampled"
mongo = PyMongo(app)

@app.route("/", methods = ['GET', 'POST'])
def dropdown():
    df = pd.DataFrame(list(mongo.db.main_redo.find()))
    df = df[(df.new_song_producer != 'None Listed') & (df.sampled_artist != 'None Listed') & (df.sampled_song_name != 'None Listed')]
    top_twenty_djs = list(df.groupby('new_song_producer').count()['URL'].sort_values(ascending = False)[:20].index)
    return render_template('test.html', djs=top_twenty_djs)

@app.route("/submitted", methods = ['GET', 'POST'])
def hello():
    var = request.form.get("djs")
    return render_template('index.html', var=var)


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