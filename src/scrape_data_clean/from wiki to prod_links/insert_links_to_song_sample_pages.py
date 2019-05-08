from pymongo import MongoClient
from pymongo import DESCENDING
client = MongoClient()
db = client.whosampled

from src.scrape_data_clean.whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    records = db.links_to_tracks_per_dj.find(
        sort=[("_id", DESCENDING)]).limit(156)
    links = [i['track_links']for i in records]
    links = [item for sublist in links for item in sublist]
    for link in links:
        try:
            scraper.get_and_insert_links_to_song_sample_songs(link)
        except:
            print("Insertion into Mongo failed or was not complete for {}".format(link))
