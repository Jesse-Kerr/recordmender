from time import sleep
from pyvirtualdisplay import Display
from selenium import webdriver

# display = Display(visible=0, size=(1024, 768))
# display.start()

from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

links_to_tracks_per_dj=db.links_to_tracks_per_dj
dj_meta_info = db.dj_meta_info

class whoSampledScraper():

    def __init__(self):

        '''
        Initializes scraper and goes to who_sampled.com
        '''
        self.driver = webdriver.Firefox()
        self.driver.get("http://www.whosampled.com")

    def go_to_dj_page(self, dj):
        '''
        Inputs the DJ you're working on into the search box. Gets you to his/her home page.
        Inserts URLS for all songs a DJ has sampled into Mongo. 
        Input: DJ (string)
        Returns: None
        '''
        search = self.driver.find_element_by_id('searchInput')
        search.send_keys(dj)
        sleep(2)
        artist = self.driver.find_element_by_id('searchArtists')
        artist.click()
        sleep(2)
    
    def filter_page_by_songs_artist_sampled(self):
        pass

    def get_num_samples(self):
        meta = self.driver.find_elements_by_xpath("//span[@class='section-header-title']")[0].get_attribute('innerHTML')

    def get_metadata_from_list(meta):
        '''
        Takes the result of Selenium query and sets these values for each artist:
        sample_num, cover_num, remix_num. If Selenium doesn't have data on these 
        numbers, sets them to 0. Implemented in get_metadata_and_links_to_tracks_by_dj
        Returns sample_num, cover_num, remix_num
        '''
        meta_list = [meta.strip() for meta in meta_list]
        meta_list = meta.split(" ")
        sample_num = 0
        cover_num = 0
        remix_num = 0

        for i, v in enumerate(meta_list):
            if 'sample' in v:
                sample_num = meta_list[i-1]
            if 'cover' in v:
                cover_num = meta_list[i-1]  
            if 'remix' in v:
                remix_num = meta_list[i-1]  
        return sample_num, cover_num, remix_num

    def get_metadata_and_links_to_tracks_by_dj(dj):


    # Get producer metadata. This returns # samples, # covers, # remixes
    # if all of those are present.


    sample_num, cover_num, remix_num = get_metadata_from_list(meta)
    total_num = sample_num + cover_num + remix_num
    #insert into MongoDB    
    dj_meta_info.insert_one({"dj" : dj,
                                "num_samples":sample_num, 
                                "num_covers" : cover_num,
                                "num_remixes": remix_num,
                                "num_total" : total_num})

    # Gets the links to the tracks for the DJ on that page (10 at most)
    tracks = driver.find_elements_by_xpath("//h3[@class='trackName']/a")
    track_links = [track.get_attribute('href') for track in tracks]

    #insert into MongoDB
    links_to_tracks_per_dj.update({'dj': dj}, {'$pushALL': {'track_links': track_links}})    

    #driver.quit()

    def links_to_sample_songs_per_track(track):    
    # Goes to each track and 
    for track in tracks:
        track.click()
        sleep(2)
        sampled_songs = driver.find_elements_by_xpath(
        # find the first bordered list, then get all the a's from the list entries in them
        "(//div[@class = 'list bordered-list'])\
        [1]//div[@class='listEntry sampleEntry']/a")
        driver.execute_script("window.scrollTo(800,1000)")
        for sampled_song in sampled_songs:
            sampled_song.click()
            sampled_song_artist = driver.find_element_by_xpath(
            #There are two artist info (the sampler and the sampled. Go to second, get artist. )
            "(//div[@class = 'sampleTrackInfo'])\
            [2]//div[@class = 'sampleTrackArtists']/a").get_attribute('text')
            print(sampled_song_artist)    

if __name__ == "__main__":
    scraper = whoSampledScraper()
    scraper.go_to_dj_page("Kanye West")
    get_links_to_tracks_by_dj()


