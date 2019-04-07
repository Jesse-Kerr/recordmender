from pymongo import MongoClient
client = MongoClient()
db = client.whosampled
from time import sleep

from whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    failed_links = []
    song_sample_pages = db.song_sample_pages.distinct('link')
    start = song_sample_pages.index("https://www.whosampled.com/sample/352391/Ghetto-Commission-Master-P-Hustla-Baller-Silkk-the-Shocker-Master-P-Big-Ed-Murder/")
    for song_sample_page in song_sample_pages[start:33000]:
        try:
            scraper.insert_song_sample_info_into_db_main(song_sample_page)
            print('Done with {}'.format(song_sample_page))
        except:
            print("Insertion into Mongo failed for {}".format(song_sample_page))
            failed_links.append(song_sample_page)
        sleep(14)
    print(failed_links)
    scraper.driver.quit()