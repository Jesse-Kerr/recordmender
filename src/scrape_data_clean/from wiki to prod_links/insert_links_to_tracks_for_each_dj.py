'''
This module takes the list of DJs from Wikipedia, searches each of them in 
Whosampled.com, and returns the links to their song sample pages.
'''

from src.scrape_data_clean.whosampled_scrape import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    djs = scraper.get_all_wiki_djs()
    index = djs.index("Anthony Preston ")
    for dj in djs[index:]: 
        try:
            scraper.go_to_who_sampled_home_page()
            scraper.set_more_who_sampled_pages_true()
            scraper.go_to_dj_page(dj)
            print("At {} page".format(dj))
            scraper.filter_page_by_songs_artist_sampled()
            while scraper.more_who_sampled_pages == True:
                scraper.get_link_to_tracks_by_dj()
                scraper.go_to_next_who_sampled_page()
        except:
            print("{} was unsuccessful!".format(dj))