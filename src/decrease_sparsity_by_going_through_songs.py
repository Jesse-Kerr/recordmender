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

4. Insert sampled_songs into db.exhaustive_sampled_songs

5. Insert producers into db.exhaustive_producers

'''
 
from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

from time import sleep
from whosampled_scrape import Scraper

if __name__ == "__main__":

    scraper = Scraper()

    #On the first step we needed to init_exhaustive, but not after that.
    #scraper.init_exhaustive_dbs()

    sampled_songs_to_do = scraper.get_sampled_songs_to_do() 
    
    # Head to the home page to start working

    #Search each sampled_song in sampled_songs_in_df. 
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
                total_tracks = total_tracks + tracks_on_page
                scraper.go_to_next_who_sampled_page()
                # sleep(3)

            # Check whether the tracks on the page are in song_sample_pages]
            tracks_not_done = scraper.get_tracks_from_page_not_done(total_tracks)
            
            #Add these into song_sample_pages
            if len(tracks_not_done) > 0:
                db.song_sample_pages.insert_many([{'link': track} for track in tracks_not_done])
            
            print("{} was sampled {} times, but we inserted only {} links".format(sampled_song, len(total_tracks), len(tracks_not_done)))
        
        #Add this song into the exhaustive list
        db.exhaustive_sampled_songs.insert({'sampled_song': sampled_song})
        print("Done with {}".format(sampled_song))
        sleep(4)
        #Producer section

        # producers_to_do = scraper.get_producers_to_do() 
        
        # #Search each sampled_song in sampled_songs_in_df. 
        # for prod in producers_to_do:

        #     # Head to the home page to start working
        #     scraper.go_to_who_sampled_home_page()

        #     #Initialize empty list to hold the tracks_sampled_by_prod
        #     tracks_sampled_by_prod = []

        #     #As long as True, keep going
        #     scraper.set_more_who_sampled_pages_true()
        #     scraper.go_to_dj_page(prod)
        #     print("At {} page".format(prod))
        #     scraper.filter_page_by_songs_artist_sampled()
        #     tracks_by_dj = []
        #     while scraper.more_who_sampled_pages == True:
        #         track_links = scraper.get_link_to_tracks_by_dj()
        #         tracks_by_dj = tracks_by_dj + track_links
        #         scraper.go_to_next_who_sampled_page()
    
        #     # Check whether the tracks on the page are in song_sample_pages]
        #     tracks_not_done = scraper.get_tracks_from_page_not_done(tracks_sampled_by_prod)

        #     for track in tracks_not_done:
        #         scraper.insert_song_sample_info_into_db_main(track)

        #     #And add the sample_songs_to_do into the exhaustive list
        #     db.song_sample_pages.insert_many([{'link': track} for track in tracks_not_done])
        #     db.exhaustive_producers.insert({'dj': prod})
        #     print("Done with {}".format(prod))

        # # move iteration up 1
        # i = i + 1
    scraper.driver.quit()

