from time import sleep
from pyvirtualdisplay import Display
from selenium import webdriver
import re

# display = Display(visible=0, size=(1024, 768))
# display.start()

from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

class Scraper():

    def __init__(self):

        '''
        Initializes scraper. Sets who_sampled_more_pages = True
        '''
        self.driver = webdriver.Firefox()

    def get_links_from_wikipage(self):

        '''
        Returns all of the djs off of a specific wikipage. 
        '''
        page_djs = self.driver.find_elements_by_xpath("//div[@class='mw-category-group']/ul/li/a")
        return [dj.get_attribute('title') for dj in page_djs]

    def go_to_next_wiki_page(self):
        
        '''
        Tries to go to next wiki_page. If fails, sets more_wiki_pages = False
        '''
        
        try:
            next_page = self.driver.find_element_by_link_text('next page')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            next_page.click()
        except: 
            print("Done with Wiki Section")
            self.more_wiki_pages = False

    def get_all_wiki_djs(self):
        
        '''
        Gets all DJs from a specific category of Wikipedia
        Returns a list of strings with any information in paranthese or brackets
        removed (usually just specifies that they are a musician.)
        '''

        self.more_wiki_pages = True
        all_djs = []
        self.driver.get("https://en.wikipedia.org/wiki/Category:American_hip_hop_record_producers")
        while self.more_wiki_pages == True:
            page_djs = self.get_links_from_wikipage()
            all_djs += page_djs
            self.go_to_next_wiki_page()
            sleep(10)
        all_djs = [re.sub("[\(\[].*?[\)\]]", "", dj) for dj in all_djs]
        return all_djs

    def go_to_who_sampled_home_page(self):
        self.driver.get("http://www.whosampled.com")
        sleep(10)

    def set_more_who_sampled_pages_true(self):
        self.more_who_sampled_pages = True

    def go_to_dj_page(self, dj):
        '''
        Inputs the DJ you're working on into the search box. Gets you to his/her home page.
        Inserts URLS for all songs a DJ has sampled into Mongo. 
        Input: DJ (string)
        Returns: None
        '''
        self.dj = dj

        # The search box. This is where we will input the dj to search.
        search = self.driver.find_element_by_id('searchInput')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", search)
        search.send_keys(self.dj)
        sleep(10)

        #This opens the dropdown of different responses to our query. We
        #generally want to click on the first element in the dropdown.
        artist = self.driver.find_element_by_id('searchArtists')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", artist)
        artist.click()
        sleep(10)
    
    def filter_page_by_songs_artist_sampled(self):
        
        '''
        The page for the artist contains more than just the songs they 
        sampled. It also has songs that sampled them, remixes, etc. So we need 
        to filter only for songs that they sampled.
        '''

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

        '''
        Inserts num_samples and prints it out.
        '''

        num_samples = self.driver.find_elements_by_xpath("//span[@class='section-header-title']")[0].get_attribute('innerHTML')
        #num_samples = int(re.sub('a-z|A-Z| ', '', num_samples))
        db.dj_meta_info.insert_one({"dj" : self.dj, "num_samples" : num_samples})
        print("{} has {} samples, inserted into Mongo.".format(self.dj, num_samples))

    def get_link_to_tracks_by_dj_insert_mongo(self):
        '''
        Gets the links to the tracks for the DJ on that page (10 at most)
        '''
        tracks = self.driver.find_elements_by_xpath("//h3[@class='trackName']/a")
        track_links = [track.get_attribute('href') for track in tracks]

        #insert into MongoDB
        db.links_to_tracks_per_dj.update({'dj': self.dj}, {'$push': {'track_links': {'$each' :track_links}}})    
        print("{} links inserted into Mongo".format(len(track_links)))

    def go_to_next_who_sampled_page(self):
        
        try:
            next_page = self.driver.find_element_by_class_name("next")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            next_page.click()
            sleep(10)
        except:
            print("No more pages")    
            self.more_who_sampled_pages = False

    def get_and_insert_links_to_song_sample_songs(self, song_page):    

        '''
        Takes the link to a song_page and finds all of the song_sample_pages
        associated with it. Inserts those into mongo.
        '''    
        self.driver.get(song_page)
        sleep(10)

        # find the first bordered list.
        # then get all the a's from the list entries in them.
        sampled_songs = self.driver.find_elements_by_xpath(
        "(//div[@class = 'list bordered-list'])\
        [1]//div[@class='listEntry sampleEntry']/a")
        
        db.song_sample_pages.insert_many([{'link': link} for link in sampled_songs])
        print("{} inserted into db.song_sample_pages".format(sampled_songs))
        
    def get_distinct_from_song_sample_pages_db(self):
        pass 

    def get_list_of_producers_credited_on_page(self):
        '''
        Takes in a link to a sample song page. Return the producers credited on
        the page as a list of strings.
        '''
        pass
        #return producer_list
        
    def insert_song_sample_info_into_db_main(self, sample_song_page):
        self.driver.get(sample_song_page)
        sleep(10)

        producer_list = self.get_list_of_producers_credited_on_page()

        # there are two artist info -the sampler and the sampled. 
        # go to second, get artist.
        sampled_song_artist = self.driver.find_element_by_xpath(
            "(//div[@class = 'sampleTrackInfo'])\
            [2]//div[@class = 'sampleTrackArtists']/a").get_attribute('text')

        # Get all the rest of the information.
        # ...
        # ...

        # Insert the information found on this page for each of the producers in
        # the producer_list
        # db.main.insert_many([{'sampled_song_artist': sampled_song_artist,
        #                       'new_song_producer' :  producer,
        #                       'new_song_artist' : ,  
        #                       'new_song_name' : , 
        #                       'new_song_year': , 
        #                       'all_songs_sampled_for_this_song': 
        #                       'sampled_song' : ,
        #                       'sampled_song_year': , 
        #                       'sampled_artist': , 
        #                       'sampled_album': ,  
        #                       'elements_sampled': ,
        #                       'time_in_sampled_song_where_sample_appears': , 
        #                       'overall_length_of_sample_song': ,
        #                       'name_of_contributor': , 
        #                       'presence_of_"and throughout"_in_description':  } 
        #                       for producer in producer_list])

