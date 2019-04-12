from pymongo import MongoClient
client = MongoClient()
db = client.whosampled
import numpy as np
import pandas as pd

import implicit

import scipy.sparse as sparse
from scipy.sparse import csr_matrix

import os
os.environ["OPENBLAS_NUM_THREADS"]="1"

import random
import re

def clean_up_mongo_coll(mongo_coll):

    '''
    Takes a mongo collection. Removes duplicates, instances where producer or artist
    are not listed. Cleans up sampled artist.

    Returns df
    '''
    df=pd.DataFrame(list(db.main_redo.find()))
    df = df.drop_duplicates(['URL', 'new_song_producer'])
    df = df[(df.new_song_producer != 'None Listed') & (df.sampled_artist != 'None Listed') ]
    df.sampled_artist = df.sampled_artist.apply(lambda x: re.sub('\(.*\)', '', x))
    df['new_song_producer'] = df.new_song_producer.apply(lambda x: re.sub('\(.*\)', '', x))
    return df

def turn_df_to_util_mat_at_limits(df, col1, col2, lim_col1 = None, lim_col2 = None):
    '''
    Inputs: Df, col1, col2, lim_col_1, lim_col_2
    Returns: Utility matrix of two col, after filtering that
    the columns have the minimum numbers specified.
    '''
    if lim_col1:
        df = df.groupby(col1).filter(lambda x: len(x) > lim_col1)
    if lim_col2:
        df = df.groupby(col2).filter(lambda x: len(x) > lim_col2)

    return pd.crosstab(df[col1], df[col2])

def get_indices_of_test_set_values(ui_util_mat, percent):
    
    '''
    Given a utility matrix and a desired train/test split, returns two lists:
    The row and column indices of the test set data.
    
    Indices should be in user, item form- therefore, matrix needs to be in user_item form.
    
    '''
    
    #Get all nonzero inds in our utility matrix. This is two lists of row/pair indices.
    nonzero_inds = ui_util_mat.values.nonzero()
        
    # Turn into list of tuples
    nonzero_pairs = list(zip(nonzero_inds[0], nonzero_inds[1]))

    # Num_samples is percent % of len(interactions)
    num_samples = int(np.ceil((percent/100)*len(nonzero_pairs))) 
    
    # Take a % of these as a test set. 
    samples = random.sample(nonzero_pairs, num_samples) 
    
    user_inds = [index[0] for index in samples] # Get the user row indices
    item_inds = [index[1] for index in samples] # Get the item column indices
    
    return user_inds, item_inds

def make_train_set_and_test_set(user_inds, item_inds, ui_util_mat):
    '''
    Creates training set with all the values at the test set indices 
    replaced with zeros.
    
    Before doing this, copies train set to test set.
    '''
    train = ui_util_mat.copy()
    test = ui_util_mat.copy()
    
    train.iloc[user_inds, item_inds] = 0
    
    return train, test

def get_denominator_for_rank_algorithm(user_inds, item_inds, test):
    '''
    Given a list of row indices, list of column indices, and a test dataset, 
    sums up the values in the utility matrix at these indices. This is the 
    denominator of the ranking algorithm.
    
    It is the r value, in the test set, at indices u, i, summed.
    '''
    
    #Get the denominator value for ranking algorithm.
    total_score = 0
    for i in range(len(user_inds)):

        score = test.iloc[user_inds[i], item_inds[i]]
        total_score += score
    return total_score

def get_rank_ui(model, user_inds, item_inds):
    
    '''
    Takes a fitted model and calculates the ranking of recommendation for every item
    for every user. This is then turned into a percentage.
    
    Indices refer to the indices of the test set. We thus filter our rankings
    to only look at the test set.
    '''
    
    # The model is set to train on item/user/confidence weights. 
    #But I am training it on user/item.
    user_vecs = model.item_factors
    item_vecs = model.user_factors
    
    #predictions is user, items
    predictions = user_vecs.dot(item_vecs.T)
    
    #print(predictions.shape)
    #get the rank of each item for each user
    #Use axis =1 to sort across, across the artists for each producer.
    order = np.flip(predictions.argsort(axis = 1), axis = 1)
    ranks = order.argsort(axis = 1)

    #turn ranks into percentages
    rank_ui = ranks / (ranks.shape[1] - 1)
    
    rank_ui = rank_ui[user_inds, item_inds].reshape(-1, 1)
    return rank_ui

def get_rui(test, user_inds, item_inds):
    rui = test.values[user_inds, item_inds].reshape(-1,1)
    return rui

def get_rank_score(r_ui, rank_ui, denominator):
    
    '''
    Requires r_ui to be in form users, items.
    '''
    
    numerator = r_ui * rank_ui

    numer_summation = np.sum(numerator)

    rank = numer_summation / denominator
    return rank

def get_pop_rank_ui(test, item_inds):
    
    '''
    Returns pop_rank_ui for test data. It counts the samples per artist,
    then ranks the artists by their number of samples. 
    
    As before, we only need the percentages for the item_inds
    '''
    
    samples_per_artist = test.sum(axis = 0)
    order = np.flip(samples_per_artist.values.argsort(), axis = 0)
    ranks = order.argsort()

    pop_rank_ui = ranks / (len(samples_per_artist) - 1)
    pop_rank_ui = pop_rank_ui[item_inds].reshape(-1,1)
    
    return pop_rank_ui

def get_rank_and_pop_score_from_train_test_model(train, test, user_inds, item_inds, factors):
    '''
    Takes a train and test set, and its indices, and fits a ALS model to the train set.
    Returns rank_scores for the model and popularity(baseline)
    '''
    
    #initialize a new model
    train_model = implicit.als.AlternatingLeastSquares(factors=factors,iterations=15)

    # train the model on a sparse matrix of user/item/confidence weights
    sparse_train = csr_matrix(train)
    train_model.fit(sparse_train)

    #1
    denominator = get_denominator_for_rank_algorithm(user_inds, item_inds, test)
  
    #2
    rank_ui = get_rank_ui(train_model, user_inds, item_inds)

    #3
    rui = get_rui(test, user_inds, item_inds)

    #4
    rank_score = get_rank_score(rui, rank_ui, denominator)

    #5
    pop_rank_score = get_pop_rank_score(test, item_inds, rui, denominator)
    return rank_score, pop_rank_score

def get_pop_rank_score(test, item_inds, rui, denominator):
    
    pop_rank_ui = get_pop_rank_ui(test, item_inds)
    pop_rank_score = get_rank_score(rui, pop_rank_ui, denominator)
    return pop_rank_score