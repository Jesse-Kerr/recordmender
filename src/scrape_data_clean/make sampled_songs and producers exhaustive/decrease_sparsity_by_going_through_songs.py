'''
We are going through sampled songs present in the df and making them exhaustive.

The sampled_songs present in the df have been sampled at least once. However, 
we don't know whether they have been sampled other times, since the original 
webscraping was not exhaustive.

To make this exhaustive, we search the song in WhoSampled, and find all of the 
instances when it was sampled. Then we add it to db.exhaustive_sampled_songs,
which is the sampled_songs we know we have exhausted and gone through entirely. 

'''
import pandas as pd
from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

from time import sleep
from src.scrape_data_clean.whosampled_scrape import Scraper

if __name__ == "__main__":
    
    # Get list of all the sampled_artist_songs we have in the dataframe, 
    # i.e., that we have already finished.
    df = pd.DataFrame(list(db.main_redo.find()))
    df['sampled_artist_song'] = df.sampled_artist + ' - ' + df.sampled_song_name

    #this set song_sampled_in_df is all of the sampled songs in df.
    song_sampled_in_df = set(df.sampled_artist_song.unique())

    # db.exhaustive_sampled_songs is all of the sampled songs we have gone 
    # through exhaustively.
    # We get a list of all the songs we have left to go through, by taking the 
    # difference of set(db.exhaustive_sampled_songs) and 
    # set(db.exhaustive_sampled_songs).  
    sampled_songs_to_do = song_sampled_in_df.difference(set(db.exhaustive_sampled_songs.distinct('sampled_song')))
    
    # Get list of all the song sample pages we've already collected. 
    song_sample_pages = db.song_sample_pages.find({}, {"link": 1, "_id": 0})
    song_sample_pages = set([element['link'] for element in song_sample_pages])

    #initialize scraper
    scraper = Scraper()

    #Search each sampled_song in sampled_songs_to_do. 
    for sampled_song in sampled_songs_to_do:

        scraper.go_to_who_sampled_home_page()

        scraper.get_to_connections_page_for_input(sampled_song)

        #Sometimes the search input doesn't return anything- means move on. 
        if scraper.has_connections:
            
            scraper.set_more_who_sampled_pages_true()

            #Initialize empty list to hold the tracks_that_sampled_song        
            total_tracks = []        

            #As long as True, keep going
            while scraper.more_who_sampled_pages == True:
            
                #Get the list of songs that sampled that song.
                tracks_on_page = scraper.get_all_tracks_from_page()
                total_tracks += tracks_on_page
                scraper.go_to_next_who_sampled_page()
            
            # Turn to a set to allow for set operations
            total_tracks = set(total_tracks) 
            # Get the tracks on the page that are not already in song_sample_pages
            tracks_not_done = total_tracks.difference(song_sample_pages)
            
            # If there are any, add them into song_sample_pages
            if len(tracks_not_done) > 0:
                db.song_sample_pages.insert_many([{'link': track} for track in tracks_not_done])
            
            print("{} was sampled {} times, but we inserted only {} links".format(sampled_song, len(total_tracks), len(tracks_not_done)))
        
        #Add this song into the exhaustive_sampled_songs list
        db.exhaustive_sampled_songs.insert({'sampled_song': sampled_song})
        print("Done with {}".format(sampled_song))
        sleep(3.8)