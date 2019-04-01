from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

from whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    links = db.command(
        {"distinct": "links_to_tracks_per_dj", 
        "query": {"dj": {"$nin": ["9th Wonder", "4th Disciple"]}}, 
        "key":"track_links"})
    for link in links['values']:
        try:
            scraper.get_and_insert_links_to_song_sample_songs(link)
        except:
            print("Insertion into Mongo failed or was not complete for {}".format(link))
    #scraper.get_distinct_from_song_sample_pages_db()
    scraper.driver.quit()
