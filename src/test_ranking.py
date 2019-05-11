from pymongo import MongoClient
client = MongoClient()
db = client.whosampled
import numpy as np
import pandas as pd

import implicit # great library for implicit recommendations

import scipy.sparse as sparse
from scipy.sparse import csr_matrix

import os
# Advised by developer of implicit to make the code run faster.
os.environ["OPENBLAS_NUM_THREADS"]="1" 

import random
import re

def clean_up_mongo_coll(mongo_coll):

    '''
    Takes a mongo collection. Removes duplicates, instances where producer or 
    artist are not listed. Cleans up sampled artist.

    Input:
        mongo_coll

    Returns:
        df: Cleaned up pandas dataframe.
    '''
    df = pd.DataFrame(list(db.main_redo.find()))

    #Remove any possible duplicates
    df = df.drop_duplicates(['URL', 'new_song_producer'])

    #drop rows with none_listed for essential columns
    df = df[(df.new_song_producer != 'None Listed') & (df.sampled_artist != 'None Listed') ]

    #remove parantheses from sampled artist or new_song_producer
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

    # Create new column with both sampled_artist and sampled_name, separated by
    # a hyphen.
    df['sampled_artist_song'] = df.sampled_artist + ' - ' + df.sampled_song_name
    return df

def turn_df_to_util_mat(df, col1, col2):
    '''
    Inputs: 
        Df, col1, col2, lim_col_1, lim_col_2
    Returns: 
        Utility matrix of two col.
    '''
    return pd.crosstab(df[col1], df[col2])

class trainModelAndEvaluateIt():

    def __init__(self, iu_util_mat):
        '''
        Takes a iu_util_matrix and makes it available to other methods in the 
        class. 
        '''
        self.iu_util_mat = iu_util_mat

    def make_train_set_and_test_set(self, percent):
        
        '''
        This method takes a utility matrix and returns a train and test set, 
        where the train set is the utility matrix with a certain percentage 
        of the actual interactions (1's) "hidden" (replaced with zeros), and 
        the test set is the original matrix.

        To do this, it creates two lists: 
            self.item_inds: The row indices of the interactions that will be 
            hidden (turned into zeros).
            self.user_inds: The column inds of the interactions that will be hidden. 
        
        Input: 
            iu_util_mat: A utility matrix in item, user form
            percent: Desired percentage of interactions to hide (turn into zeros)
        
        Return:
            self.train: utility matrix with percentage of interactions hidden.
            self.test: original matrix.
        '''
        
        # Get all nonzero inds in our utility matrix. This is two lists of row/pair indices.
        nonzero_inds = self.iu_util_mat.values.nonzero()
            
        # Turn into list of tuples
        nonzero_pairs = list(zip(nonzero_inds[0], nonzero_inds[1]))

        # Num_samples is percent % of len(interactions)
        num_samples = int(np.ceil((percent/100)*len(nonzero_pairs))) 
        
        # Take a % of these as a test set. 
        samples = random.sample(nonzero_pairs, num_samples) 
        
        self.test_item_inds = [index[0] for index in samples] # Get the user row indices
        self.test_user_inds = [index[1] for index in samples] # Get the item column indices
        
        self.train = self.iu_util_mat.copy()
        self.test = self.iu_util_mat.copy()
        
        # It is necessary to turn to a sparse matrix before applying the 
        # following step. Otherwise it does not work correctly and the wrong 
        # indices are replaced with zeroes.
        self.train = csr_matrix(self.train.values)
        self.train[self.test_item_inds, self.test_user_inds] = 0
        self.train = pd.DataFrame(
            self.train.todense(), columns= self.iu_util_mat.columns, 
            index = self.iu_util_mat.index)

    def get_sparsity_of_mat(self, util_mat):
        '''
        Input:
            train: A utility matrix with specific interactions replaced with zeros
            util_mat: The df to assess the sparsity of. Only supports 
            self.train or self.iu_util_mat
        Return:
            sparsity: The percentage of nonzero interactions in the matrix
        '''
        if util_mat not in [self.train, self.iu_util_mat]:
            raise ValueError("df must be one of train or iu_util_mat.")
        # Number of possible interactions in the matrix
        matrix_size = util_mat.shape[0]*util_mat.shape[1] 
        
        # Number of actual interactions
        nonzeros = sum(util_mat.sum(axis=0))
        
        sparsity = 100*(1 - (nonzeros/matrix_size))
        
        return sparsity

    def filter_dataset_by_requisite_interactions(
        self, item_lim, user_lim, train_test = True):
        
        '''
        Limits dataframes for model building to samples with requisite interactions.
        As of now user_lim and item_lim must be provided

        Input: 
            user_lim: The lower limit of interactions you will accept for user
            item_lim: The lower limit of interactions you will accept for items
            train_test: Boolean for whether you want to apply this to the train
            and test sets, or to the entire dataframe (the ui_util_mat). Set to
            False if you are not splitting your data. 
        Returns: 
            self.train: Training set with users and items above user_lim and item_lim
            self.test: Test set with users and items above user_lim and item_lim
            self.item_inds: New item indices 
            self.user_inds: New user indices
        
        '''    
        if train_test:

            #Count interactions for each item
            inters_per_item = self.train.sum(axis = 1)

            #Count interactions for each user
            inters_per_user = self.train.sum(axis = 0)

            #Get a list of items with more than item_lim of interactions.
            items_above_lim = list(inters_per_item[inters_per_item > item_lim].index)
             
            #Get a list of users with more than user_lim of interactions.
            users_above_lim = list(inters_per_user[inters_per_user > user_lim].index)
  
            # filter the train set to only have these items
            self.train = self.train[self.train.index.isin(items_above_lim)]

            # We are taking the intersection of the columns with the users_above_lim.
            self.train = self.train[self.train.columns.intersection(users_above_lim)]

            # Repeat for test set.
            self.test = self.test[self.test.index.isin(items_above_lim)]
            self.test = self.test[self.test.columns.intersection(users_above_lim)]

            #For the ranking, need the indices of this subset.
            #Find where train and test differ- this seems to work.
            inds_lim = np.where(self.train != self.test)

            self.test_item_inds= inds_lim[0]
            self.test_user_inds = inds_lim[1]
    
    def train_model(self, rec_algo = "bpr"):
        '''

        This method takes a type of algorithm, and returns a fitted version of 
        that model.
        Input:
            rec_algo: The type of algorithm to use to create the recommender.
        '''
        if rec_algo == "bpr":
            self.model = implicit.bpr.BayesianPersonalizedRanking()
        elif rec_algo == "als":
            self.model = implicit.als.AlternatingLeastSquares(
                factors=10, iterations=50, regularization= 74)
        else: 
            raise ValueError("Only ALS and BPR are supported at this time")
        
        #fit the model to the taining data
        self.model.fit(sparse.coo_matrix(self.train))

    def get_predictions_matrix(self):

        '''
        Creates prediction matrix using the model.
        '''
        self.predictions = self.model.item_factors.dot(self.model.user_factors.T)
    
    def get_denominator_of_rank_algorithm(self):
        '''
        The denominator of the rank algorithm is the sum of the actual values 
        (number of times a producer sampled an artist) at the test set indices.

        This method finds the denominator of the rank algorithm by summing up
        the actual values at those indices. 
        
        To use the terminology from Yifan Hu paper, it is the summation at r_ui
        for indices u,i in the test set.
        '''
        
        self.denominator = 0
        for i in range(len(self.test_item_inds)):
            
            # Get the actual value at r_ui for u, i in test set.
            score = self.test.iloc[self.test_item_inds[i], self.test_user_inds[i]]
            self.denominator += score
        return self.denominator

    def get_rank_ui(self):
        
        '''
        Calculates the ranking of recommendation for 
        every item for every user. This is then turned into a percentage.
        
        Indices refer to the indices of the test set. We thus filter our rankings
        to only look at the test set.
        '''
        
        #get the rank of each item for each user
        #Use axis =1 to sort across, across the artists for each producer.
        order = np.flip(self.predictions.argsort(axis = 0), axis = 0)
        ranks = order.argsort(axis = 0)

        #turn ranks into percentages
        self.rank_ui = ranks / (ranks.shape[0] - 1)
        
        self.rank_ui = self.rank_ui[self.test_item_inds, self.test_user_inds].reshape(-1, 1)

    def get_rui(self):
        self.rui = self.test.values[self.test_item_inds, self.test_user_inds].reshape(-1,1)

    def get_rank_score(self, to_score):
        
        '''
        Requires r_ui to be in form users, items.
        '''
        
        numerator = self.rui * to_score

        numer_summation = np.sum(numerator)

        return numer_summation / self.denominator

    def get_pop_rank_ui(self):
        
        '''
        Returns pop_rank_ui for test data. It counts the inters_per_item,
        then ranks the items by the number of interactions. 
        
        As before, we only need the percentages for the item_inds.

        The ranking is such that ties are given the same score. 
        '''
        
        inters_per_item = self.test.sum(axis = 1)
        order = np.flip(inters_per_item.values.argsort())
        ranks = order.argsort()

        self.pop_rank_ui = ranks / (len(inters_per_item) - 1)
        self.pop_rank_ui = self.pop_rank_ui[self.test_item_inds].reshape(-1,1)
    
    def get_pop_rank_score(self):
    
        self.get_pop_rank_ui()
        pop_rank_score = self.get_rank_score(self.pop_rank_ui)
        return pop_rank_score

    def get_rank_and_pop_score_from_train_test_model(
        self):
        '''
        Uses the ranking score implemented in "Collaborative Filtering for Implicit 
        Feedback Datasets" to take an already trained model, a split train and test set.
        Returns rank_scores for the model and popularity(baseline)
        '''
        self.get_predictions_matrix()
        self.get_denominator_of_rank_algorithm()
        self.get_rank_ui()
        self.get_rui()
        rank_score = self.get_rank_score(self.rank_ui)
        pop_rank_score = self.get_pop_rank_score()
        return rank_score, pop_rank_score

    def get_top_recommends_for_user(self, user, n_recommends =10, filter =True):
        
        '''
        Input: 
            user: Producer for whom you want to get recommendations for
        Returns:
            Top_n_recommends

        '''
        # Get index of user 
        index_of_user = self.train.columns.get_loc(user)
        
        # Filter the predictions dataset for only this user
        filtered_preds = self.predictions[:,index_of_user]

        # Get the indices which would sort the array.
        order = np.flip(filtered_preds.argsort())

        if filter == True:

            #Get the list of everything our user did not interact with.
            indices_where_producer_didnt_sample = np.where(
                self.iu_util_mat[[index_of_user]] == 0)[0]

            # Filter the rankings to return only the rankings where the user didn't sample.
            ordered_filtered = order[np.isin(order, indices_where_producer_didnt_sample)]

        # Select the top n of these
            ordered_filtered_top = ordered_filtered[:n_recommends]
            
            return [self.iu_util_mat.index[n] for n in ordered_filtered_top]
            
        #Don't filter, just take top recommends.
        ordered_top = order[:n_recommends]
        return [self.iu_util_mat.index[n] for n in ordered_top]

    def get_similar_to_user(self, user, n_similar=2):
        
        # Get index of user 
        index_of_user = self.iu_util_mat.columns.get_loc(user)
        
        similar_users = self.model.similar_users(index_of_user, N= n_similar)
        
        similar_user_inds = [sim[0] for sim in similar_users]
        
        return [self.iu_util_mat.columns[n] for n in similar_user_inds]