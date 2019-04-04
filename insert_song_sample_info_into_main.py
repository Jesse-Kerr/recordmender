from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

from time import sleep
from whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    failed_links = []
    song_sample_pages = db.song_sample_pages.distinct('link')
    start = song_sample_pages.index("https://www.whosampled.com/sample/226359/Pooh-Man-Niggas-Ain%27t-Playin%27-The-Gap-Band-Shake/")
    for song_sample_page in song_sample_pages[start:23000]: 
        try:
            scraper.insert_song_sample_info_into_db_main(song_sample_page)
            print('Done with {}'.format(song_sample_page))
        except:
            print("Insertion into Mongo failed for {}".format(song_sample_page))
            failed_links.append(song_sample_page)
        sleep(5)
    print(failed_links)
    scraper.driver.quit()