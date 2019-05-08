from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

import numpy as np
from time import sleep
from src.scrape_data_clean.whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    failed_links = []

    song_sampled_pages_to_do = db.song_sampled_pages_to_do.distinct('link')

    for song_sample_page in song_sampled_pages_to_do[-10000:]: 
        try:
            scraper.insert_song_sample_info_into_db_main(song_sample_page)
            print('Done with {}'.format(song_sample_page))
        except:
            print("Insertion into Mongo failed for {}".format(song_sample_page))
            failed_links.append(song_sample_page)
        sleep(1.1)
    print(failed_links)
    scraper.driver.quit()