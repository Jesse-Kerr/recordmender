from time import sleep
from pyvirtualdisplay import Display

from bs4 import BeautifulSoup
display = Display(visible=0, size=(1024, 768))
display.start()

from pymongo import MongoClient
client = MongoClient()
soup = BeautifulSoup(features="html.parser")

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

#Change to Chrome for AWS
# options = Options()
# options.headless = True
# driver = webdriver.Chrome(options=options)
driver = webdriver.Firefox()

def get_links_to_tracks_by_dj(dj):
    
    '''
    Inserts URLS for all songs a DJ has sampled into Mongo. 
    Input: DJ (string)
    Returns: None
    '''
    
    driver.get("http://www.whosampled.com")

    # Inputs the DJ you're working on into the search box. Gets you to his/her home page.
    search = driver.find_element_by_id('searchInput')
    search.send_keys(dj)
    sleep(2)
    artist = driver.find_element_by_id('searchArtists')
    artist.click()
    sleep(2)
    
    # Gets the links to the tracks for the DJ on that page (10 at most)
    tracks = driver.find_elements_by_xpath("//h3[@class='trackName']/a")
    for track in tracks:
        print(track.get_attribute('href'))
    #insert into MongoDB

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

get_links_to_tracks_by_dj("Kanye West")
driver.quit()


