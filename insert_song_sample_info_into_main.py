from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

from whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    for song_sample_page in db.song_sample_pages: 
        try:
            scraper.insert_song_sample_info_into_db_main(song_sample_page)
        except:
            print("Insertion into Mongo failed for {}".format(link))
    scraper.get_distinct_from_song_sample_pages_db()
    scraper.driver.quit()