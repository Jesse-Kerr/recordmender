from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

import numpy as np
from time import sleep
from whosampled_scrape import Scraper

from turn_db_main_into_utility_matrix import from_mongo_collection_to_utility_matrix

if __name__ == "__main__":
    scraper = Scraper()
    failed_links = []

    #All song_samples we have
    song_sample_pages = db.song_sample_pages.distinct('link')

    _, _, df = from_mongo_collection_to_utility_matrix(db.main_redo)
    
    #Filter that by only the ones we haven't done.
    song_sampled_pages_to_do = np.where(np.in1d(song_sample_pages, df.URL.unique()) == False)[0]

    for song_sample_page in song_sampled_pages_to_do[:2000]: 
        try:
            scraper.insert_song_sample_info_into_db_main(song_sample_page)
            print('Done with {}'.format(song_sample_page))
        except:
            print("Insertion into Mongo failed for {}".format(song_sample_page))
            failed_links.append(song_sample_page)
        sleep(7)
    print(failed_links)
    scraper.driver.quit()