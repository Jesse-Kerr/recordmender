# this module contains all the different URLs that the application implements.

from flask import render_template, flash, redirect, request
from flask_pymongo import PyMongo

#we get the instance of our flask app here. 
from app import flask_app

from app.forms import LoginForm
import pandas as pd
from turn_db_main_into_utility_matrix import from_mongo_collection_to_utility_matrix
import pickle

flask_app.config["MONGO_URI"] = "mongodb://localhost:27017/whosampled"
mongo = PyMongo(flask_app)

# the decorator here connects the function below it to the route
# above it. 
@flask_app.route("/", methods = ['GET', 'POST'])
def dropdown():
    _, _, df = from_mongo_collection_to_utility_matrix(mongo.db.main_redo)    
    df = df[(df.new_song_producer != 'None Listed') & (df.sampled_artist != 'None Listed') & (df.sampled_song_name != 'None Listed')]
    top_twenty_djs = list(df.groupby('new_song_producer').count()['URL'].sort_values(ascending = False)[:20].index)
    
    #render_template uses Jinja2 to put data into the 
    return render_template('test.html', djs=top_twenty_djs)

@flask_app.route("/submitted", methods = ['GET', 'POST'])
def hello():
    _, artist_prod, df = from_mongo_collection_to_utility_matrix(mongo.db.main_redo)    
    var = request.form.get("djs")
    idx = artist_prod.get_loc(var)
    model = pickle.load(open('model.pkl', 'rb'))  
    recommendations = model.recommend(idx)
    return render_template('index.html', var=recommendations)


@flask_app.route("/index")
def index():
    dj = mongo.db.dj_meta_info.find_one({}, {"dj": 1, "_id": 0})
    djs = mongo.db.dj_meta_info.find({}, {"dj": 1, "_id": 0}).limit(5)
    return render_template("index.html",
        dj=dj, djs =djs)

@flask_app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login Requested for {}, remember_me = {}'.format(
                form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title = 'Sign In', form = form)