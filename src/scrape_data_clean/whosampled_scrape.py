# Used to stop the scraper so that it doesn't get caught by WhoSampled.
from time import sleep 
import re # Regular expression module
from selenium import webdriver # The webdriver.

# The Keys module allows you to send keys like Enter, Tab, without using the UTF
#code for them. 
from selenium.webdriver.common.keys import Keys 

# Allows you to set the webdriver options
from selenium.webdriver.chrome.options import Options

# Connect to the specific mongo db.
from pymongo import MongoClient
client = MongoClient()
db = client.whosampled

class Scraper():

    def __init__(self):

        '''
        Initializes an instance of the Selenium scraper with options inherited
        from an instance of the Options class.  
        '''
        # Initialize an instance of Options, with the below arguments added.
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions") #not sure why
        chrome_options.add_argument("--disable-gpu") #not sure why
        # So that you don't have to see the chrome browser.
        chrome_options.add_argument("--headless") 

        # Initialize the webdriver with the above options.
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

        # The implicitly_wait parameter means when you search for an element, 
        # Selenium will wait this long before failing and saying that it's not 
        # there. This is good when you want it to wait while a website loads, but 
        # bad when you put it in a Try, Except and you want it to fail- then it 
        # takes 60 seconds to fail.
        self.driver.implicitly_wait(60)

    def get_prod_names_from_wikipage(self):

        '''
        Returns all of the producer names off of a specific wikipage. 
        '''
        page_djs = self.driver.find_elements_by_xpath(
            "//div[@class='mw-category-group']/ul/li/a")
        return [dj.get_attribute('title') for dj in page_djs]

    def go_to_next_wiki_page(self):
        
        '''
        Tries to go to next wiki_page. If fails, sets more_wiki_pages = False
        '''
        
        try:
            # Find the link that has the text "next page" on it.
            next_page = self.driver.find_element_by_link_text('next page')
            # Make sure it's in view.
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            # Click on it.
            next_page.click()
        except: 
            #If there is no element with the text "next page" on it, end.
            print("Done with Wiki Section")
            self.more_wiki_pages = False

    def get_all_wiki_djs(self):
        
        '''
        Gets all DJs from a specific category of Wikipedia.
        Returns a list of strings with any information in parantheses or brackets
        removed (usually just specifies that they are a musician.)
        '''
        # As long as more_wiki_pages is True, Selenium will run the 
        # go_to_next_wiki_page function.
        self.more_wiki_pages = True
        all_djs = [] # Empty list that will be filled with the DJs.

        # Go to the wikipedia page that has the American hip hop record producers.
        self.driver.get(
            "https://en.wikipedia.org/wiki/Category:American_hip_hop_record_producers")
        while self.more_wiki_pages == True:
            # Get all producer names from the wikipage.
            page_djs = self.get_prod_names_from_wikipage()
            all_djs += page_djs
            self.go_to_next_wiki_page()

        # Remove any information in parantheses or brackets.
        all_djs = [re.sub("[\(\[].*?[\)\]]", "", dj) for dj in all_djs]
        return all_djs

    def go_to_who_sampled_home_page(self):
        '''
        Takes webscraper to the who_sampled homepage
        '''
        self.driver.get("http://www.whosampled.com")

    def set_more_who_sampled_pages_true(self):
        '''
        Set at the beginning, when going through list of pages for a DJ.
        '''
        self.more_who_sampled_pages = True

    def go_to_dj_page(self, dj):
        '''
        1. Inputs the DJ you're working on into the search box, then clicks on 
        the first response to the query that comes up.
        Input: 
            DJ (string)
        Returns: 
            None
        '''
        # Ampersands mess up the search function- everything after the ampersand 
        # gets deleted. So I replace it with and.
        dj = re.sub('&amp;', 'and', dj)
        
        # Hyphens also mess up the search functionality.
        dj = re.sub('-', ' ', dj)
        
        # The search box. This is where we will input the dj to search.
        search = self.driver.find_element_by_id('searchInput')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", search)
        
        # Input the dj name to the search box.
        search.send_keys(dj)

        # By inputting the DJ name into the search, a dropdown opens with all the
        # different responses to our query. We select and click on the first 
        # element in the dropdown (the most relevant one).
        artist = self.driver.find_element_by_xpath("//div[@id='searchArtists']/ul/li[1]")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", artist)
        artist.click()

        # Turn to self.dj, so that this input is available to other methods in 
        # the class
        self.dj = dj

    def filter_page_by_songs_artist_sampled(self):

        '''
        The page for the artist contains more than just the songs they 
        sampled. It also has songs that sampled them, remixes, etc. So we need 
        to filter only for songs that they sampled.
        '''

        # This dropdown had the options: "Songs sampled by DJ", or 
        # "Songs that sampled the DJ", etc.
        dropdown = self.driver.find_element_by_xpath("//div[@class='optionMenu artistPageMenu']")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)
        dropdown.click() # Open the dropdown

        # the "Songs sampled by DJ" is always the second one.
        sampled = self.driver.find_element_by_xpath("//ul[@class = 'expanded']/li[2]")
        self.driver.execute_script("arguments[0].scrollIntoView(true);", sampled)
        sampled.click()

    def get_link_to_tracks_by_dj(self):
        '''
        Gets the links to the tracks for the DJ on that page (10 at most)
        Originally we put these directly into the MongoDB, but now the return
        from this method is being manipulated further. 
        '''
        # Links to songs the DJ sampled are called connections.
        tracks = self.driver.find_elements_by_xpath("//a[@class='connectionName playIcon']")
        track_links = [track.get_attribute('href') for track in tracks]
        return track_links
        #insert into MongoDB
        #db.coll.update({'dj': self.dj}, {'$push': {'track_links': {'$each' :track_links}}}, upsert= True)    
        #print("{} links".format(len(track_links)))

    def get_links_for_songs_with_more_than_3_samples(self, all_links, all_nums):
        
        '''
        This method is used when we are trying to make the list of producers
        exhaustive. When we find a song by a producer which sampled more than
        3 songs, we cannot get all of the links in one go. So we save those 
        links, and the number of sampled songs we missed/ producer song, in 
        order to go back to later.  

        Input: 
            all_links: The list of links to the pages for the songs with more 
            than 3 samples. This may be an empty list.
            all_nums: The number of songs that we missed. A list with same 
            length as all_links. Also can be empty.
        Returns:
            [all_links, all_nums], but with any added missed links and the 
            number missed on those pages. These may still be empty lists.

        '''

        self.driver.implicitly_wait(0)
        
        links = self.driver.find_elements_by_xpath("//a[@class='moreLink bordered-list moreConnections']")
        if len(links) > 0:
            track_links = [link.get_attribute('href') for link in links]
            number_missed =[link.get_attribute('innerHTML') for link in links]
            
            #It's a string of text, extract the number out
            number_missed = [int(number.split(" ")[1]) for number in number_missed]

            return all_links + track_links, all_nums + number_missed
        else:
            return all_links, all_nums
        self.driver.implicitly_wait(10)

    def go_to_next_who_sampled_page(self):

        '''
        Looks for elements with the class name "next". This is the link to the 
        next page. 
        If the element exists, it takes us to that next page.
        Otherwise, it stops and sets more_who_sampled_pages to False.
        '''    
        # Set implicit wait to low here, because we know it is likely not to find it
        self.driver.implicitly_wait(0)
        # Find the elements that have class name "next".
        next_page = self.driver.find_elements_by_class_name("next")
        # If the list has a length of at least 1, go to the next page.
        if len(next_page) > 0:
            next_page = next_page[0]
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            next_page.click()
        # Otherwise, there are no more pages.
        else:
            print("No more pages")    
            self.more_who_sampled_pages = False
        self.driver.implicitly_wait(60)

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

    def init_exhaustive_dbs(self):
        '''
        Creates db.exhaustive_producers and db.exhaustive_sampled_songs.
        db.exhaustive_producers has the producers which have been finished. 
        At start, it's just the 692 djs from wikipedia (assumption).  
        
        db.exhaustive_sampled_songs is all of the songs we have entirely finished.
        At beginning, it's empty.
        '''

        djs = self.get_all_wiki_djs()
        db.exhaustive_producers.insert_many([{'dj': dj} for dj in djs])    

        db.create_collection('exhaustive_sampled_songs')

    def get_to_connections_page_for_input(self, user_input):
        
        '''
        Inputs sampled_song into search bar and presses enter.
        This is part of the process of exhausting all of the sampled_song in the
        dataset.
        '''

        #Ampersands, hashtags, plusses and semicolons mess with the search function.
        user_input = re.sub('&|#|\+|;', '', user_input)
        search = self.driver.find_element_by_id('searchInput')
        self.driver.execute_script("arguments[0].scrollIntoView(true);", search)
        search.send_keys(user_input)
        search.send_keys(Keys.RETURN)
        
        # Decrease implicitly wait for Try/ Except because I know this is likely to fail
        self.driver.implicitly_wait(0)

        # Find whether there are any connections for this song (which there 
        # should be.)
        try:

            connections = self.driver.find_element_by_link_text("Connections")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", connections)
            connections.click()
            print("At {} page".format(user_input))
            self.has_connections = True
        except:
            self.has_connections = False
        
        self.driver.implicitly_wait(10)

    def get_all_tracks_from_page(self):
        
        '''
        Gets the link to all the connections on the page.
        '''
        connections = self.driver.find_elements_by_xpath("//span[@class = 'connectionTitle']/a")
        connections = [connection.get_attribute('href') for connection in connections]
        return connections
