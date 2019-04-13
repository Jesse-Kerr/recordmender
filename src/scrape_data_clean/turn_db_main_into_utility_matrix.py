from pymongo import MongoClient
client = MongoClient()
db = client.whosampled
import re

import pandas as pd

                
def from_mongo_collection_to_utility_matrix(mongo_collection):
    '''
    Takes data from mongo_Collection and returns a pandas dataframe as a utility matrix
    '''
    
    df = pd.DataFrame(list(mongo_collection.find()))

    #Turn sampled_song_producer from list to string

    #Remove any possible duplicates
    #df = df.drop_duplicates(['URL', 'new_song_producer'])

    #drop rows with none_listed for essential columns
    #Only lists 100 out of 17,000 times there is no new_song_producer, similar low amounts for other columns below.

    #df = df[(df.new_song_producer != 'None Listed') & (df.sampled_artist != 'None Listed') ]

    #Need to remove this step for now. 

    # Make utility matrix: Get lists of producers and songs
    #sampled_songs = list(df.drop_duplicates('sampled_song_name')['sampled_song_name'])
    #new_song_producers = list(df.drop_duplicates('new_song_producer')['new_song_producer'])

    # Make new dict with zeros everywhere using the columns and rows above.
    #utility_matrix = pd.DataFrame(0, index=sampled_songs, columns= new_song_producers).to_dict()
    #df.sampled_song_name = df.sampled_song_name\
    # .apply(lambda x: x.strip())\
    # .apply(lambda x: x.lower())\
    # .apply(lambda x: re.sub('\(.* version\)$|instrumental$', '', x))\
    # .apply(lambda x: re.sub('\(live\)|\(.* remix\)', '', x))\
    # .apply(lambda x: re.sub('\(version .*', '', x))\
    # .apply(lambda x: re.sub('\(|\)|"|\'', '', x))\
    # .apply(lambda x: re.sub('-', ' ', x))\
    # .apply(lambda x: x.strip())\
    # .apply(lambda x: re.sub(' +', ' ', x))

    df.sampled_artist = df.sampled_artist.apply(lambda x: re.sub('\(.*\)', '', x))
    
    #Create new column with both sampled_artist and sampled_name    
    df['sampled_artist_song'] = df.sampled_artist + ' - ' + df.sampled_song_name

    # make_util(utility_matrix, df)
    # prod_song = pd.crosstab(df.new_song_producer, df.sampled_artist_song)
    prod_artist = pd.crosstab(df.new_song_producer, df.sampled_artist)

    return prod_artist, df