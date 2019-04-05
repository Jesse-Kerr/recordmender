from pymongo import MongoClient
client = MongoClient()
db = client.whosampled
import re

import pandas as pd

def make_util(utility_matrix, df):
    '''
    Goes through the items in the nested utility matrix dictionary, checking whether 
    their row name and column name exist together in df. If so, replaces that cell with a 1.
    '''
    for producer, songs in utility_matrix.items():
        for song in songs:
            cond1 = df.sampled_song_name == song
            cond2 = df.new_song_producer == producer
            if len(df[cond1 & cond2]) > 0:
                utility_matrix[producer][song] = 1
                
def from_mongo_collection_to_utility_matrix(mongo_collection):
    '''
    Takes data from mongo_Collection and returns a pandas dataframe as a utility matrix
    '''
    
    df = pd.DataFrame(list(mongo_collection.find()))

    #Turn sampled_song_producer from list to string
    df['sampled_song_producer'] = df.sampled_song_producer.apply( lambda x: ', '.join(x))

    #Remove any possible duplicates
    df = df.drop_duplicates(['URL', 'new_song_producer'])

    #drop rows with none_listed for essential columns
    #Only lists 100 out of 17,000 times there is no new_song_producer, similar low amounts for other columns below.

    df = df[(df.new_song_producer != 'None Listed') & (df.sampled_artist != 'None Listed') & (df.sampled_song_name != 'None Listed')]

    df['new_song_producer'] = df.new_song_producer.apply(lambda x: re.sub('\(.*\)', '', x))
    # Make utility matrix: Get lists of producers and songs
    #sampled_songs = list(df.drop_duplicates('sampled_song_name')['sampled_song_name'])
    #new_song_producers = list(df.drop_duplicates('new_song_producer')['new_song_producer'])

    # Make new dict with zeros everywhere using the columns and rows above.
    #utility_matrix = pd.DataFrame(0, index=sampled_songs, columns= new_song_producers).to_dict()
    df.sampled_song_name = df.sampled_song_name\
    .apply(lambda x: x.strip())\
    .apply(lambda x: x.lower())\
    .apply(lambda x: re.sub('\(.* version\)$|instrumental$', '', x))\
    .apply(lambda x: re.sub('\(live\)|\(.* remix\)', '', x))\
    .apply(lambda x: re.sub('\(version .*', '', x))\
    .apply(lambda x: re.sub('\(|\)|"|\'', '', x))\
    .apply(lambda x: re.sub('-', ' ', x))\
    .apply(lambda x: x.strip())\
    .apply(lambda x: re.sub(' +', ' ', x))

    df.sampled_artist = df.sampled_artist.apply(lambda x: re.sub('\(.*\)', '', x))
    
    #Create new column with both sampled_artist and sampled_name    
    df['sampled_artist_song'] = df.sampled_artist + ' - ' + df.sampled_song_name

    # make_util(utility_matrix, df)
    utility_to_song = pd.crosstab(df.sampled_artist_song, columns=df.new_song_producer)
    utility_to_artist = pd.crosstab(df.sampled_artist, columns=df.new_song_producer )

    #utility_to_artist.set_index('new_song_producer', inplace = True)
    # utility2 = pd.DataFrame.from_dict(utility_matrix, orient = 'index')
    return utility_to_song, utility_to_artist, df