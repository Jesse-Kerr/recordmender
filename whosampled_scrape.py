from time import sleep
from pyvirtualdisplay import Display
from selenium import webdriver

display = Display(visible=0, size=(1024, 768))
display.start()

from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

links_to_tracks_per_dj=db.links_to_tracks_per_dj
dj_meta_info = db.dj_meta_info

# get DJs
driver = webdriver.Firefox()
from wikipedia_scrape import get_all_artists, go_to_next_page, get_links_from_wikipage
djs = get_all_artists()

class whoSampledScraper():

    def __init__(self, driver):

        '''
        Initializes scraper and goes to who_sampled.com
        '''
        self.driver = driver
        self.driver.get("http://www.whosampled.com")
        self.more_pages = True

    def go_to_dj_page(self, dj):
        '''
        Inputs the DJ you're working on into the search box. Gets you to his/her home page.
        Inserts URLS for all songs a DJ has sampled into Mongo. 
        Input: DJ (string)
        Returns: None
        '''
        self.dj = dj
        search = self.driver.find_element_by_id('searchInput')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", search)
        search.send_keys(self.dj)
        sleep(10)
        artist = self.driver.find_element_by_id('searchArtists')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", artist)
        artist.click()
        sleep(10)
    
    def filter_page_by_songs_artist_sampled(self):
        dropdown = self.driver.find_element_by_xpath("//div[@class='optionMenu artistPageMenu']")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        dropdown.click()
        sleep(10)

        # the tracks sampled is always the second one
        sampled = self.driver.find_element_by_xpath("//ul[@class = 'expanded']/li[2]")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", sampled)
        sampled.click()
        sleep(10)
        
    def get_num_samples_insert_mongo(self):
        num_samples = self.driver.find_elements_by_xpath("//span[@class='section-header-title']")[0].get_attribute('innerHTML')
        dj_meta_info.insert_one({"dj" : self.dj, "num_samples" : num_samples})
        return num_samples

    def get_link_to_tracks_by_dj(self):
        '''
        Gets the links to the tracks for the DJ on that page (10 at most)
        '''
        tracks = self.driver.find_elements_by_xpath("//h3[@class='trackName']/a")
        track_links = [track.get_attribute('href') for track in tracks]

        #insert into MongoDB
        links_to_tracks_per_dj.update({'dj': self.dj}, {'$push': {'track_links': {'$each' :track_links}}}, upsert=True)    
        return track_links

    def go_to_next_page(self):
        try:
            next_page = self.driver.find_element_by_class_name("next")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            next_page.click()
            sleep(10)
        except:
            print("No more pages")    
            self.more_pages = False
    def links_to_sample_songs_per_track(self, track):    
        # Goes to each track and 
        for track in tracks:
            track.click()
            sleep(2)
            sampled_songs = self.driver.find_elements_by_xpath(
            # find the first bordered list, then get all the a's from the list entries in them
            "(//div[@class = 'list bordered-list'])\
            [1]//div[@class='listEntry sampleEntry']/a")
            self.driver.execute_script("window.scrollTo(800,1000)")
            for sampled_song in sampled_songs:
                sampled_song.click()
                sampled_song_artist = self.driver.find_element_by_xpath(
                #There are two artist info (the sampler and the sampled. Go to second, get artist. )
                "(//div[@class = 'sampleTrackInfo'])\
                [2]//div[@class = 'sampleTrackArtists']/a").get_attribute('text')
                print(sampled_song_artist)    

if __name__ == "__main__":
    scraper = whoSampledScraper(driver)
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
