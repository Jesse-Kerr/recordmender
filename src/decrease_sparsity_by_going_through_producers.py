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

import pandas as pd
from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

from time import sleep
from whosampled_scrape import Scraper

if __name__ == "__main__":

    scraper = Scraper()

    # Producer section
    prods_in_df = set(db.main_redo.distinct('new_song_producer'))
    
    producers_to_do = prods_in_df.difference(set(db.exhaustive_producers.distinct('dj')))

    # Get a set of all the links in song_sample_pages. We want to try not to redo these.
    song_sample_pages = db.song_sample_pages.find({}, {"link": 1, "_id": 0})
    song_sample_pages = set([element['link'] for element in song_sample_pages])
    
    #Search each sampled_song in sampled_songs_in_df. 
    for prod in producers_to_do:
        try:
            # Head to the home page to start working
            scraper.go_to_who_sampled_home_page()

            scraper.go_to_dj_page(prod)
            print("At {} page".format(prod))

            #We just want all the connections. 
            #However, if we don't filter, we lose songs that were sampled.
            scraper.filter_page_by_songs_artist_sampled()
            scraper.set_more_who_sampled_pages_true()
            
            #Initialize empty list to hold the tracks_sampled_by_prod
        
            all_links_to_song_sample_pages = []

            #Only three sample pages are listed per track.
            #If there are more than 3, there is a link to another page which has all samples.
            # We are going to store the links to those pages, along with the number of 
            # samples that we missed. 
            # Later, we'll go to them, and say, take the last n samples on this page, 
            # since the order remains the same. 
            #E.g., Madlib samples 7 songs for a track. We get three now, get the link
            # to all of them. Later we go to that link and tell selenium to scrape the bottom
            # 4, since those are the ones we missed. 
            #As long as True, keep going

            all_more_than_3_pages = []
            num_missed_for_more_than_3 = []

            while scraper.more_who_sampled_pages == True:
                links_on_page = scraper.get_link_to_tracks_by_dj()
                all_links_to_song_sample_pages = all_links_to_song_sample_pages + links_on_page

                all_more_than_3_pages, num_missed_for_more_than_3 = scraper.get_links_for_songs_with_more_than_3_samples(
                    all_more_than_3_pages, num_missed_for_more_than_3)
                
                scraper.go_to_next_who_sampled_page()
                sleep(3)
            all_links_to_song_sample_pages = set(all_links_to_song_sample_pages)

            # Check whether the links to song_sample_pages are in song_sample_pages]

            tracks_not_done = all_links_to_song_sample_pages.difference(song_sample_pages)

            #And add the sample_songs_to_do into the exhaustive list
            if len(tracks_not_done) > 0:
                db.song_sample_pages.insert_many([{'link': track} for track in tracks_not_done])

            print("{} sampled {} times, but we inserted only {} links".format(prod, len(all_links_to_song_sample_pages), len(tracks_not_done)))

            #If we found any songs with more than 3 samples, insert into db for later.
            if len(all_more_than_3_pages) > 0:
                db.tracks_with_more_than_3_samples.insert_many([{'link': link, 'num_missed': num} for link, num in zip(all_more_than_3_pages, num_missed_for_more_than_3)])
            db.exhaustive_producers.insert({'dj': prod})

            print("We also saved {} links to go back to later".format(len(num_missed_for_more_than_3)))

            print("Done with {}!".format(prod))
            sleep(3)

        except:
            print("This shit failed for {}".format(prod))