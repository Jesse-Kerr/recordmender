from time import sleep
from pyvirtualdisplay import Display
from selenium import webdriver
import re

display = Display(visible=0, size=(1024, 768))
display.start()

from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

links_to_tracks_per_dj=db.links_to_tracks_per_dj
dj_meta_info = db.dj_meta_info

class Scraper():

    def __init__(self):

        '''
        Initializes scraper. Sets who_sampled_more_pages = True
        '''

        self.driver = webdriver.Firefox()
        self.who_sampled_more_pages = True
        self.more_wiki_pages = True

    def get_links_from_wikipage(self):

        '''
        Returns all of the artists (djs) off of a specific wikipage. 
        '''
        page_artists = self.driver.find_elements_by_xpath("//div[@class='mw-category-group']/ul/li/a")
        return [artist.get_attribute('title') for artist in page_artists]

    def go_to_next_wiki_page(self):
        '''
        Tries to go to next wiki_page. If fails, sets more_wiki_pages = False
        '''
        
        try:
            next_page = driver.find_element_by_link_text('next page')
            driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            next_page.click()
        except: 
            print("Done with Wiki Section")
            self.more_wiki_pages = False

    def get_all_wiki_artists(self):
        
        '''
        Gets all DJs from a specific category of Wikipedia
        Returns a list of strings with any information in paranthese or brackets
        removed (usually just specifies that they are a musician.)
        '''
        
        all_artists = []
        self.driver.get("https://en.wikipedia.org/wiki/Category:American_hip_hop_record_producers")
        while self.more_wiki_pages == True:
            page_artists = self.get_links_from_wikipage()
            all_artists += page_artists
            self.go_to_next_wiki_page()
        all_artists = [re.sub("[\(\[].*?[\)\]]", "", artist) for artist in all_artists]
        return all_artists
    
    def go_to_dj_page(self, dj):
        '''
        Inputs the DJ you're working on into the search box. Gets you to his/her home page.
        Inserts URLS for all songs a DJ has sampled into Mongo. 
        Input: DJ (string)
        Returns: None
        '''
        self.dj = dj
        self.driver.get("http://www.whosampled.com")
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
        links_to_tracks_per_dj.update({'dj': self.dj}, {'$push': {'track_links': {'$each' :track_links}}})    
        return track_links

    def go_to_next_page(self):
        try:
            next_page = self.driver.find_element_by_class_name("next")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            next_page.click()
            sleep(10)
        except:
            print("No more pages")    
            self.who_sample = False
    def insert_links_to_song_sample_songs(self, song_page):    
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

    def get_distinct_from_song_sample_pages_db(self):
        pass 

    def get_list_of_producers_credited_on_page(self, page):
        pass
    
    def insert_song_sample_info_into_db_main(self, producer):
        pass