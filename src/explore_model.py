import numpy as np

def get_top_recommends_not_yet_sampled_for_user(user, predictions_user_item, user_item, n_recommends =10, filter =True):
    
    '''
    Input: 
        user: Producer for whom you want to get recommendations for
        predictions_user_art: The predictions for the user, in user-artist format
        user_art: The original utility matrix used to train the model.

    Returns:
        Top_n_recommends, not filtered

    '''
    # Get index of user 
    index_of_user = user_item.index.get_loc(user)
    
    # Filter the predictions dataset for only this user
    filtered_preds = predictions_user_item[index_of_user,]

    # Return the indices which would sort the array. E.g, if you were to put
    # 110 at the front, you would win, so we know that 110 is the best

    order = np.flip(filtered_preds.argsort())

    if filter == True:

        #Get the list of everything our producer didn't sample
        indices_where_producer_didnt_sample = np.where(user_item.iloc[index_of_user] == 0)[0]

        # Filter the rankings to return only the highest rankings where the user didn't sample
        ordered_filtered = order[np.isin(order, indices_where_producer_didnt_sample)]
        
        # Select the top n of these
        ordered_filtered_top = ordered_filtered[:n_recommends]
        
        return [user_item.columns[n] for n in ordered_filtered_top]
        

    else:
        #Don't filter, just take top recommends.
        ordered_top = order[:n_recommends]
        return [user_item.columns[n] for n in ordered_top]

def get_similar_to_prod(user, n_similar, model, artist_user):
    
    # Get index of user 
    index_of_user = artist_user.columns.get_loc(user)
    
    similar_users = model.similar_users(index_of_user, N= n_similar)
    
    similar_user_inds = [sim[0] for sim in similar_users]
    
    return [artist_user.columns[n] for n in similar_user_inds]