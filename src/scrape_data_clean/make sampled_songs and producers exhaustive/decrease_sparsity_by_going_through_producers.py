'''
The purpose of this module is to go through the producers present in 
db.main_redo, and make sure we have exhaustive data for them. Many of them have
simply appeared by happenstance, and we want to actually search them, in order
to confirm that we have all of the songs they have ever sampled.

To do this, we get a list of all of the producers in the dataset. We then go 
through them one by one, inserting any of the songs they've db.song_sample_pages.
We then add them into db.exhaustive_producers, the list of the producers we are
confident we have gone through fully.

'''
from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

from time import sleep
from src.scrape_data_clean.whosampled_scrape import Scraper

if __name__ == "__main__":

    scraper = Scraper()

    # this is the set of all of the producers present in the df.
    prods_in_df = set(db.main_redo.distinct('new_song_producer'))
    
    # The producers we have to do is the difference between prods_in_df and the 
    # set from db.exhaustive_producers.
    producers_to_do = prods_in_df.difference(set(db.exhaustive_producers.distinct('dj')))

    # Get a set of all the links in song_sample_pages. We want to try not to 
    # redo these. It's not a big deal if we put in some duplicates, though.
    song_sample_pages = db.song_sample_pages.find({}, {"link": 1, "_id": 0})
    song_sample_pages = set([element['link'] for element in song_sample_pages])
    
    # Go through each prod in producers_to_do.
    for prod in producers_to_do:
        try:
            # Head to the home page to start working
            scraper.go_to_who_sampled_home_page()

            scraper.go_to_dj_page(prod)
            print("At {} page".format(prod))

            # I'm only looking for songs that the producer sampled. 
            scraper.filter_page_by_songs_artist_sampled()

            scraper.set_more_who_sampled_pages_true()
            
            #Initialize empty list.
            all_links_to_song_sample_pages = []

            # Only three sample pages are listed per track.
            # If there are more than 3, there is a link to another page which 
            # has all samples.
            # For the producer songs which sampled more than 3 songs, we will 
            # store the links to those pages, along with the number of samples 
            # that we missed.

            all_more_than_3_pages = []
            num_missed_for_more_than_3 = []

            # Later, we'll go to them, and take the last n samples on this page, 
            # since the order remains the same. 

            # E.g., Madlib sampled 7 songs for a track. We get 3 now and get the 
            # link to all of them. Later we go to that link and scrape the bottom
            # 4, since those are the ones we missed. 

            #As long as True, keep going
            while scraper.more_who_sampled_pages == True:
                links_on_page = scraper.get_link_to_tracks_by_dj()
                all_links_to_song_sample_pages += links_on_page

                all_more_than_3_pages, num_missed_for_more_than_3 = scraper.get_links_for_songs_with_more_than_3_samples(
                    all_more_than_3_pages, num_missed_for_more_than_3)
                
                scraper.go_to_next_who_sampled_page()
            
            # Turn to a set so we can use set operations.
            all_links_to_song_sample_pages = set(all_links_to_song_sample_pages)

            # Check whether the links to song_sample_pages are in song_sample_pages
            tracks_not_done = all_links_to_song_sample_pages.difference(
                song_sample_pages)

            #And add the sample_songs_to_do into the exhaustive list
            if len(tracks_not_done) > 0:
                db.song_sample_pages.insert_many([{'link': track} for track in tracks_not_done])

            print("{} sampled {} times, but we inserted only {} links".format(prod, len(all_links_to_song_sample_pages), len(tracks_not_done)))

            #If we found any songs with more than 3 samples, insert into db for later.
            if len(all_more_than_3_pages) > 0:
                db.tracks_with_more_than_3_samples.insert_many(
                    [{'link': link, 'num_missed': num} for link, num in 
                    zip(all_more_than_3_pages, num_missed_for_more_than_3)])
            
            # We finished with that producer, add him to db.exhaustive_producers.
            db.exhaustive_producers.insert({'dj': prod})

            print("We also saved {} links to go back to later".format(
                len(num_missed_for_more_than_3)))

            print("Done with {}!".format(prod))
            sleep(3)

        except:
            print("This failed for {}".format(prod))