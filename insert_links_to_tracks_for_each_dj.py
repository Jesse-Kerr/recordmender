
from whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    djs = scraper.get_all_wiki_artists()
    for dj in djs: 
        try:
            scraper.go_to_dj_page(dj)
            print("At {} page".format(dj))
            scraper.filter_page_by_songs_artist_sampled()
            num_samples = scraper.get_num_samples_insert_mongo()
            print("{} has {}".format(dj, num_samples))
            while scraper.more_pages == True:
                track_links = scraper.get_link_to_tracks_by_dj()
                print("{} links inserted into Mongo".format(len(track_links)))
                scraper.go_to_next_page()
        except:
            print("{} was unsuccessful!".format(dj))
    scraper.driver.quit()