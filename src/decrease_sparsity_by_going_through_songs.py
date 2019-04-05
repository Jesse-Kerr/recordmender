'''
This module works in a series of alternating steps to decrease the sparsity of our matrix 
and make it exhaustive. 

1. Gets the list of sampled_songs present in the df.

For what we know at this point, these songs have been sampled at least once. 
However, we don't know whether they have been sampled other times, since 
the original webscraping was not exhaustive in this way.

To make this exhaustive, we:

2. Search the song and get all of the tracks_that_sampled_song.

3. We then check whether these are already in db.song_sample_pages. 
db.song_sample_pages is our exhaustive list of links which we are running through 
step by step. 

4. Insert sampled_songs into db.exhaustive_sample_songs

5. Insert producers into db.exhaustive_producers

'''
 
from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

from time import sleep
from whosampled_scrape import Scraper

if __name__ == "__main__":
    
    scraper = Scraper()
    djs = scraper.get_all_wiki_djs()

    #db.exhaustive producers tracks which producers have been finished. 
    # At start, it's just the 692 djs from wikipedia (assumption).
    db.exhaustive_producers.insert_many(djs)    
    
    # db.exhaustive_sampled_songs is all of the songs we have entirely finished.
    # at beginning, it's empty.
    db.create_collection(exhaustive_sampled_songs)

    while jesse_says_go:

        #Get the list of sampled_songs that appear in the df that we need to go through. 
        _, _, df = from_mongo_collection_to_utility_matrix(db.main_redo)
        sampled_songs_in_df = df.sampled_artist_song.unique()

        set(db.exhaustive_sample_songs.find())
        #Search each sampled_song in sampled_songs_in_df. 
        for sampled_song in sampled_songs_in_df:
            scraper.go_to_who_sampled_home_page()
            scraper.search_sampled_song_from_search_bar()

            #Get the list of songs that sampled that song.
            scraper.
            #function here to go to page, insert info, get list.
            #tracks_that_sampled_song = ##code here
            tracks_not_done = [track for track in tracks_that_sampled_song if track not in song_sample_pages]
            db.song_sample_pages_new.insert_many(tracks_that_sampled_song)
            sleep(9)

 
        # Get the list of song_sample_pages already in db.song_sample_pages.
        # If they're here, it means we've already covered them or are in the process. 
        song_sample_pages = db.song_sample_pages.distinct('link')

        # Go through song_sample_pages_new running insert_song_sample_info_into_main_template
        song_sample_pages_new = db.song_sample_pages_new.distinct('link')
        for new_song_sample_page in song_sample_pages_new:
            scraper.insert_song_sample_info_into_db_main(new_song_sample_page)

        # Now that we're done with these pages, insert them all into song_sample_pages
        db.song_sample_pages.insert_many(song_sample_pages_new)

        #And drop them from the song_sample_pages_new db
        db.song_sample_pages_new.drop()


        ##Get the list of unique producers that already appear in the df
        producers_in_df = df.new_song_producers.unique()
        

    scraper.driver.quit()
