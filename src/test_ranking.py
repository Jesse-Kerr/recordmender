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
    df = pd.DataFrame(list(db.main_redo.find()))
    df = df.drop_duplicates(['URL', 'new_song_producer'])
    df = df[(df.new_song_producer != 'None Listed') & (df.sampled_artist != 'None Listed') ]
    df.sampled_artist = df.sampled_artist.apply(lambda x: re.sub('\(.*\)', '', x))
    df['new_song_producer'] = df.new_song_producer.apply(lambda x: re.sub('\(.*\)', '', x))

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

    df['sampled_artist_song'] = df.sampled_artist + ' - ' + df.sampled_song_name
    return df

def turn_df_to_util_mat(df, col1, col2):
    '''
    Inputs: Df, col1, col2, lim_col_1, lim_col_2
    Returns: Utility matrix of two col, after filtering that
    the columns have the minimum numbers specified.
    '''
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

    Changes as a for loop
    '''
    train = ui_util_mat.copy()
    test = ui_util_mat.copy()
    train = csr_matrix(train.values)
    train[user_inds, item_inds] = 0
    train = pd.DataFrame(train.todense(), columns= ui_util_mat.columns, index = ui_util_mat.index)

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

def get_rank_and_pop_score_from_train_test_model(
    train, test, user_inds, item_inds, factors = 10, regularization = 74, iterations = 50):
    '''
    Takes a train and test set, and its indices, and fits a ALS model to the train set.
    Returns rank_scores for the model and popularity(baseline)
    '''
    
    #initialize a new model
    train_model = implicit.als.AlternatingLeastSquares(
        factors=factors, iterations=iterations, regularization= regularization)

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

def get_rank_and_pop_score_of_two_columns(df, col1, col2, split_pct, factors = 4, regularization = 70, iterations = 50):
    
    '''
    Input: 
        Col1: Users
        Col2: Items
        Df: Dataframe to get columns data from
        Split.pct: % of data to send to hide for testing.
        Factors, regularization, iterations: Parameters for the ALS algorithm
        
    Returns: Rank_score and pop_score of those two columns
    '''
    
    user_item = turn_df_to_util_mat(
            df, col1, col2)

    user_inds, item_inds = get_indices_of_test_set_values(user_item, split_pct)

    train, test = make_train_set_and_test_set(user_inds, item_inds, user_item)

    rank_score, pop_rank_score = get_rank_and_pop_score_from_train_test_model(
        train, test, user_inds, item_inds, factors, regularization ,iterations)
    
    return rank_score, pop_rank_score

def get_sparsity_of_training_data(train):
    '''
    Input:
        train: A utility matrix with specific interactions replaced with zeros
    Return:
        sparsity: The percentage of nonzero interactions in the matrix
    '''
    
    # Number of possible interactions in the matrix
    matrix_size = train.shape[0]*train.shape[1] 
    
    # Number of actual interactions
    nonzeros = sum(train.sum(axis=0))
    
    sparsity = 100*(1 - (nonzeros/matrix_size))
    
    return sparsity


def filter_dataset_by_requisite_interactions(train, test, user_inds, item_inds,
 user_lim = None, item_lim = None):
    
    '''
    Limits dataframes for model building to samples with requisite interactions.

    Input: 
        train: The training data
        test: The test data
        user_lim: The lower limit of interactions you will accept for user
        item_lim: The lower limit of interactions you will accept for items

    Returns: 
        train_lim: Training set with users and items above user_lim and item_lim
        test_lim: Test set with users and items above user_lim and item_lim
        user_inds_lim: New user indices 
        item_inds_lim: New item indices
        
    '''
    
    if user_lim:
        
        #Count interactions for each user
        inters_per_user = train.sum(axis = 1)
        
        #Get a list of users with more than user_lim of interactions.
        users_above_lim = list(inters_per_user[inters_per_user > user_lim].index)
    
    else:
        
        #If user_lim not provided, simply get the users
        users_above_lim = list(train.index)

    if item_lim:
        
        #Count interactions for each item
        inters_per_item = train.sum(axis = 0)
        
        #Get a list of items with more than item_lim of interactions.
        items_above_lim = list(inters_per_item[inters_per_item > item_lim].index)

    else:
        items_above_lim = list(train.columns)
    
    # filter the training and test sets to only have these producers
    train_lim = train.loc[users_above_lim, items_above_lim]
    test_lim = test.loc[users_above_lim, items_above_lim]

    #For the ranking, need the indices of this subset.
    #Find where train and test differ- this seems to work.
    inds_lim = np.where(train_lim != test_lim)

    user_inds_lim= inds_lim[0]
    item_inds_lim = inds_lim[1]
    
    return train_lim, test_lim, user_inds_lim, item_inds_lim

if __name__ == "__main__":
    
    df = clean_up_mongo_coll(db.main_redo)
    user_art = turn_df_to_util_mat(
        df, 'new_song_producer', 'sampled_artist')
    
    user_inds, item_inds = get_indices_of_test_set_values(user_art, 5)

    train, test = make_train_set_and_test_set(user_inds, item_inds, user_art)
    
    rows = []

    columns = ['user_lim', 'item_lim', 'num_users_at_lim', 'num_items_at_lim', 
                    'sparsity', 'percent_users_lost', 'percent_items_lost', 
                   'rank_score', 'pop_rank_score']

    for user_lim in range(-1, 1):
        for item_lim in range(-1, 0):
            
            train_lim, test_lim, user_inds_lim, item_inds_lim = filter_dataset_by_requisite_interactions(
            train, test, user_inds, item_inds, user_lim, item_lim)
            
            sparsity = get_sparsity_of_training_data(train_lim)
            
            num_users_at_lim = train_lim.shape[0]
            num_items_at_lim = train_lim.shape[1]
            
            percent_users_lost = 1 - (num_users_at_lim / train.shape[0])
            percent_items_lost = 1 - (num_items_at_lim / train.shape[1])
            
            rank_score, pop_rank_score = get_rank_and_pop_score_from_train_test_model(
                train_lim, test_lim, user_inds_lim, item_inds_lim, 10, 74, 50)
            
            rows.append([user_lim, item_lim, num_users_at_lim, num_items_at_lim, 
                        sparsity, percent_users_lost, percent_items_lost, 
                    rank_score, pop_rank_score])
            
    statistics_at_interaction_limits = pd.DataFrame(rows, columns = columns)

    statistics_at_interaction_limits.to_csv("statistics_at_interaction_limits.csv")