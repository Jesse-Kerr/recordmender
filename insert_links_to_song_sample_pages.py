from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

from whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    for link in db.links_to_tracks_per_dj: 
        try:
            scraper.get_and_insert_links_to_song_sample_songs(link)
        except:
            print("Insertion into Mongo failed for {}".format(link))
    scraper.get_distinct_from_song_sample_pages_db()
    scraper.driver.quit()