from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
class ItemItemRecommender(object):
    """Item-item similarity recommender."""

    def __init__(self, neighborhood_size = 75):
        """Initialize the parameters of the model."""
        self.neighborhood_size = neighborhood_size


    def fit(self, ratings_mat):
        """Fit the model to the data specified as an argument.

        Store objects for describing model fit as class attributes.
        """
        self.ratings_mat = ratings_mat
        self.items_cos_sim = cosine_similarity(self.ratings_mat.T)

        least_to_most_sim_indexes = np.flip(np.argsort(self.items_cos_sim, 1), axis =1)
        self.neighborhood = least_to_most_sim_indexes[:, :self.neighborhood_size]

    def pred_one_user(self, user_id):
        """Accept user id as arg. Return the predictions for a single user.

        Optional argument to specify whether or not timing should be
        provided on this operation.
        """
        n_items = self.ratings_mat.shape[1]
        items_rated_by_this_user = np.nonzero(self.ratings_mat[user_id])[1]
        self.output = np.zeros(n_items)
        for item_to_rate in range(n_items):
            relevant_items = np.intersect1d(self.neighborhood[item_to_rate],
                                        items_rated_by_this_user,
                                        assume_unique=True)
            if len(relevant_items) == 0:
                self.output[item_to_rate] = 0
            else:
                self.output[item_to_rate] = (
                self.ratings_mat[user_id, relevant_items] * 
                self.items_cos_sim[item_to_rate, relevant_items] / 
                (self.items_cos_sim[item_to_rate, relevant_items].sum())
                )
        return self.output
    def pred_all_users(self):
        """Return a matrix of predictions for all users.

        Repeated calls of pred_one_user, are combined into a single matrix.
        Return value is matrix of users (rows) items (columns) and
        predicted ratings (values).

        Optional argument to specify whether or not timing should be
        provided on this operation.
        """
        pass

    def top_n_recs(self):
        """Take user_id argument and number argument.

        Return that number of items with the highest predicted ratings,
        after removing items that user has already rated.
        """
        pass
