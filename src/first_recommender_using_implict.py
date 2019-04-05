import scipy.sparse as sparse
import os
os.environ["OPENBLAS_NUM_THREADS"]="1"

import implicit

#Using the github benfred implicit. Docstring says confidence matrix is important.

def get_model_and_user_items_from_utility_matrix(utility_mat, calculate_training_loss = True, iterations=100, factors=50):

    '''
    Takes in a utility matrix from turn_db_main function.
    Return a fitted model.
    '''

    # Turns to sparse matrix
    sparse_util = sparse.lil_matrix(utility_mat)

    model = implicit.als.AlternatingLeastSquares(factors = factors, calculate_training_loss = calculate_training_loss,iterations = iterations)
    model.fit(sparse_util)

    user_items = sparse_util.T.tocsr()
    return model, user_items


    # #Since our matrix is in form of items user, need to transpose for user_items
    # user_items = sparse_util.T.tocsr()

    # recommendations = model.recommend(1000, user_items)