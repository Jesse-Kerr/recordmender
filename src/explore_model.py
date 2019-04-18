import numpy as np

def get_top_recommends_not_yet_sampled_for_user(user, n_recommends, predictions_user_art, user_art, filter =True):
    
    '''
    Input: 
        user: Producer for whom you want to get recommendations for
        predictions_user_art: The predictions for the user, in user-artist format
        user_art: The original utility matrix used to train the model.

    Returns:
        Top_n_recommends, not filtered

    '''
    # Get index of user 
    index_of_user = user_art.index.get_loc(user)
    
    # Filter the predictions dataset for only this user
    filtered_preds = predictions_user_art[index_of_user,]

    # Return the indices which would sort the array. E.g, if you were to put
    # 110 at the front, you would win, so we know that 110 is the best

    order = np.flip(filtered_preds.argsort())

    if filter == True:

        #Get the list of everything our producer didn't sample
        indices_where_producer_didnt_sample = np.where(user_art.iloc[index_of_user] == 0)[0]

        # Filter the rankings to return only the highest rankings where the user didn't sample
        ordered_filtered = order[np.isin(order, indices_where_producer_didnt_sample)]
        
        # Select the top n of these
        ordered_filtered_top = ordered_filtered[:n_recommends]
        
        return [user_art.columns[n] for n in ordered_filtered_top]
        

    else:
        #Don't filter, just take top recommends.
        ordered_top = order[:n_recommends]
        return [user_art.columns[n] for n in ordered_top]

