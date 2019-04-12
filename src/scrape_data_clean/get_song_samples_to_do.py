from pymongo import MongoClient
client = MongoClient()
db = client.whosampled
import pandas as pd
import numpy as np
#Empty what we have, and check again.

#db.song_sampled_pages_to_do.drop()
db.song_sampled_pages_to_do.drop()

df = pd.DataFrame(list(db.main_redo.find()))
done_URLS = set(df.URL.unique())

#total pages we have links to
song_sample_pages = db.song_sample_pages.find({}, {"link": 1, "_id": 0})
song_sample_pages = set([element['link'] for element in song_sample_pages])

#total pages we've left
song_sampled_pages_to_do = song_sample_pages.difference(done_URLS)

db.song_sampled_pages_to_do.insert_many([{'link':song} for song in song_sampled_pages_to_do])