from time import sleep
from pyvirtualdisplay import Display
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--headless")

from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

class Scraper():

    def __init__(self):

        '''
        Initializes scraper. Sets who_sampled_more_pages = True
        '''
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.implicitly_wait(60)
        
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
            #sleep(2)
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
            #sleep(5)
        all_djs = [re.sub("[\(\[].*?[\)\]]", "", dj) for dj in all_djs]
        return all_djs

    def go_to_who_sampled_home_page(self):
        self.driver.get("http://www.whosampled.com")
        #sleep(5)

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
        #sleep(2)
        search.send_keys(self.dj)
        sleep(1)

        #This opens the dropdown of different responses to our query. We
        #generally want to click on the first element in the dropdown.
        artist = self.driver.find_element_by_xpath("//div[@id='searchArtists']/ul/li[1]")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", artist)
        artist.click()
        #sleep(5)

    def filter_page_by_songs_artist_sampled(self):

        '''
        The page for the artist contains more than just the songs they 
        sampled. It also has songs that sampled them, remixes, etc. So we need 
        to filter only for songs that they sampled.
        '''

        dropdown = self.driver.find_element_by_xpath("//div[@class='optionMenu artistPageMenu']")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        #sleep(2)
        dropdown.click()
        #sleep(5)

        # the tracks sampled is always the second one
        sampled = self.driver.find_element_by_xpath("//ul[@class = 'expanded']/li[2]")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", sampled)
        #sleep(2)
        sampled.click()
        #sleep(5)
        
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
        db.links_to_tracks_per_dj.update({'dj': self.dj}, {'$push': {'track_links': {'$each' :track_links}}}, upsert= True)    
        print("{} links inserted into Mongo".format(len(track_links)))

    def go_to_next_who_sampled_page(self):
        next_page = self.driver.find_elements_by_class_name("next")
        if len(next_page) > 0:
            next_page = next_page[0]
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            #sleep(10)
            next_page.click()
            #sleep(10)
        else:
            print("No more pages")    
            self.more_who_sampled_pages = False

    def get_and_insert_links_to_song_sample_songs(self, song_page):    

        '''
        Takes the link to a song_page and finds all of the song_sample_pages
        associated with it. Inserts those into mongo.
        '''    
        self.driver.get(song_page)
        #sleep(5)

        # find the first bordered list.
        # then get all the a's from the list entries in them.
        song_sample_pages = self.driver.find_elements_by_xpath(
        "(//div[@class = 'list bordered-list'])\
        [1]//div[@class='listEntry sampleEntry']/a")

        song_sample_pages = [song_sample_page.get_attribute('href') for song_sample_page in song_sample_pages]

        db.song_sample_pages.insert_many([{'link': link} for link in song_sample_pages])
        print("{} links inserted into db.song_sample_pages".format(len(song_sample_pages)))
        
    def insert_song_sample_info_into_db_main(self, song_sample_page):
        self.driver.get(song_sample_page)
        #sleep(2)
        self.driver.implicitly_wait(0)

        try:
            new_producer_list = self.driver.find_elements_by_xpath(
            "(//div[@class = 'sampleEntryBox'])[1]\
             /div[@class = 'sampleAdditionalInfo sample-layout-row']\
             /div[@class = 'sampleAdditionalInfoContainer sample-layout-row-right']\
             /div[@class = 'track-metainfo-wrapper']\
             /div[@class='track-metainfo']\
            /span[@itemprop='producer']/a/span")
            if len(new_producer_list) > 0:
                new_producer_list = [producer.get_attribute('innerHTML') for producer in new_producer_list]
            else: 
                new_producer_list = ["None Listed"]
        except:
            new_producer_list = ["None Listed"]
            
        try:
            old_producer_list = self.driver.find_elements_by_xpath(
            "(//div[@class = 'sampleEntryBox'])[2]\
             /div[@class = 'sampleAdditionalInfo sample-layout-row']\
             /div[@class = 'sampleAdditionalInfoContainer sample-layout-row-right']\
             /div[@class = 'track-metainfo-wrapper']\
             /div[@class='track-metainfo']\
             /span[@itemprop='producer']/a/span")
            old_producer_list = [producer.get_attribute('innerHTML') for producer in old_producer_list]
        except:
            old_producer_list = "None Listed"        

        try:
            new_song_artist = self.driver.find_element_by_xpath(
              "(//div[@class = 'sampleTrackMetadata'])[1]\
                /div[@class = 'sampleTrackInfo']/h3\
                /div[@class = 'sampleTrackArtists']\
                /a").get_attribute('text')
        except:
            new_song_artist = "None Listed"

        try:    
            new_song_name = self.driver.find_element_by_xpath(
              "(//div[@class = 'sampleTrackMetadata'])[1]\
                /div[@class = 'sampleTrackInfo']\
                /h3/a").get_attribute('text')
        except:
            new_song_name = "None Listed"

        try:
            new_song_year = int(self.driver.find_element_by_xpath(
                "(//div[@class = 'sampleTrackMetadata'])[1]\
                /div[@class = 'sampleReleaseDetails']\
                /div[@class = 'trackLabel']\
                /p[@class = 'label-details']\
                /a[@itemprop = 'datePublished']\
                ").get_attribute('text'))
        except:
            new_song_year ="None Listed"

        try:
            new_song_album = self.driver.find_element_by_xpath(
               "(//div[@class = 'sampleTrackMetadata'])[1]\
                /div[@class = 'sampleReleaseDetails']\
                /p[@class = 'release-name']\
                /a").get_attribute('text')
        except:
            new_song_album ="None Listed"

        try:
            sampled_song_name = self.driver.find_element_by_xpath(
              "(//div[@class = 'sampleTrackMetadata'])[2]\
                /div[@class = 'sampleTrackInfo']\
                /h3/a[@class = 'trackName']").get_attribute('text')
        except:
            sampled_song_name ="None Listed"

        try:    
            sampled_song_artist = self.driver.find_element_by_xpath(
              "(//div[@class = 'sampleTrackMetadata'])[2]\
                /div[@class = 'sampleTrackInfo']/h3\
                /div[@class = 'sampleTrackArtists']\
                /a").get_attribute('text')

        except: 
            sampled_song_artist = "None Listed"

        try:
            sampled_song_year = int(self.driver.find_element_by_xpath(
                "(//div[@class = 'sampleTrackMetadata'])[2]\
                /div[@class = 'sampleReleaseDetails']\
                /div[@class = 'trackLabel']\
                /p[@class = 'label-details']\
                /a[@itemprop = 'datePublished']\
                ").get_attribute('text'))
        except:
            sampled_song_year = "None Listed"

        try:
            sampled_album = self.driver.find_element_by_xpath(
               "(//div[@class = 'sampleTrackMetadata'])[2]\
                /div[@class = 'sampleReleaseDetails']\
                /p[@class = 'release-name']\
                /a").get_attribute('text')
        except:
            sampled_album = "None Listed"
            
        try:
            elements = self.driver.find_element_by_xpath(
                "//div[@class = 'section-header']/h2").get_attribute('innerHTML')
        except:
            elements = "None Listed"

        try:
            time_in_sampled_song_where_sample_appears = self.driver.find_element_by_xpath(
                "//strong[@id = 'sample-source-timing']/span").get_attribute('innerHTML')
        except:
            time_in_sampled_song_where_sample_appears = "None Listed"

        try:   
            contributor = self.driver.find_element_by_xpath(
                "//div[@class='sampleContributed sample-layout-row-right']/p/a").get_attribute('innerHTML')
        except:
            contributor = "None Listed"

        try:    
            contributor_votes = self.driver.find_element_by_xpath(
                "//div[@class='sampleContributed sample-layout-row-right']/p").text
        except:
            contributor_votes = "None Listed"
        
        try:
            presence_of_and_throughout = self.driver.find_element_by_xpath(
                "(//div[@class='timing-wrapper'])[1]").text
        except:
            presence_of_and_throughout = "None Listed"
        
        # Insert the information found on this page for each of the producers in
        # the producer_list
        db.main_redo.insert_many([{'new_song_producer' : producer,
                            'sampled_song_producer': old_producer_list,
                            'new_song_artist' : new_song_artist, 
                            'new_song_name' : new_song_name, 
                            'new_song_year': new_song_year,
                            'new_song_album': new_song_album, 
                            'sampled_artist': sampled_song_artist, 
                            'sampled_song_name': sampled_song_name,
                            'sampled_song_year': sampled_song_year, 
                            'sampled_song_album' : sampled_album,
                            'elements_sampled': elements,
                            'time_in_sampled_song_where_sample_appears': time_in_sampled_song_where_sample_appears,
                            'name_of_contributor': contributor, 
                            'contributor_points' : contributor_votes,
                            'presence_of_"and throughout"_in_description': presence_of_and_throughout,
                            'URL': song_sample_page}
                              for producer in new_producer_list])

        self.driver.implicitly_wait(10)