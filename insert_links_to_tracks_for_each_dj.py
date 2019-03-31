
from whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    djs = scraper.get_all_wiki_djs()
    scraper.go_to_who_sampled_home_page()
    for dj in djs[4:]: 
        try:
            scraper.set_more_who_sampled_pages_true()
            scraper.go_to_dj_page(dj)
            print("At {} page".format(dj))
            scraper.filter_page_by_songs_artist_sampled()
            scraper.get_num_samples_insert_mongo()
            while scraper.more_who_sampled_pages == True:
                scraper.get_link_to_tracks_by_dj_insert_mongo()
                scraper.go_to_next_who_sampled_page()
        except:
            print("{} was unsuccessful!".format(dj))
    scraper.driver.quit()