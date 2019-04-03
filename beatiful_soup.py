import requests
from time import sleep
from pymongo import MongoClient
client = MongoClient()
db = client.whosampled
from lxml import html


def insert_song_sample_info_into_db_main(song_sample_page):
    page = requests.get(song_sample_page)
    tree = html.fromstring(page.content)
    sleep(5)

    try:
        new_producer_list = tree.xpath(
        "(//div[@class = 'sampleEntryBox'])[1]\
            /div[@class = 'sampleAdditionalInfo sample-layout-row']\
            /div[@class = 'sampleAdditionalInfoContainer sample-layout-row-right']\
            /div[@class = 'track-metainfo-wrapper']\
            /div[@class='track-metainfo']\
        /span[@itemprop='producer']/a/span/innerHTML")
        # new_producer_list = [producer.get_attribute() for producer in new_producer_list]
    except:
        new_producer_list = ["None Listed"]

    try:
        old_producer_list = tree.xpath(
    "(//div[@class = 'sampleEntryBox'])[2]\
        /div[@class = 'sampleAdditionalInfo sample-layout-row']\
        /div[@class = 'sampleAdditionalInfoContainer sample-layout-row-right']\
        /div[@class = 'track-metainfo-wrapper']\
        /div[@class='track-metainfo']\
        /span[@itemprop='producer']/a/span/innerHTML")
        # old_producer_list = [producer.get_attribute('innerHTML') for producer in old_producer_list]
    except:
        old_producer_list = "None Listed"        

    try:
        new_song_artist = tree.xpath(
        "(//div[@class = 'sampleTrackMetadata'])[1]\
        /div[@class = 'sampleTrackInfo']/h3\
        /div[@class = 'sampleTrackArtists']\
        /a/text")
    except:
        new_song_artist = "None Listed"

    try:    
        new_song_name = tree.xpath(
        "(//div[@class = 'sampleTrackMetadata'])[1]\
        /div[@class = 'sampleTrackInfo']\
        /h3/a/text")
    except:
        new_song_name = "None Listed"

    try:
        new_song_year = int(tree.xpath(
        "(//div[@class = 'sampleTrackMetadata'])[1]\
        /div[@class = 'sampleReleaseDetails']\
        /div[@class = 'trackLabel']\
        /p[@class = 'label-details']\
        /a[@itemprop = 'datePublished']\
        /text"))
    except:
        new_song_year ="None Listed"

    try:
        new_song_album = tree.xpath(
        "(//div[@class = 'sampleTrackMetadata'])[1]\
        /div[@class = 'sampleReleaseDetails']\
        /p[@class = 'release-name']\
        /a/text")
    except:
        new_song_album ="None Listed"

    try:
        sampled_song_name = tree.xpath(
        "(//div[@class = 'sampleTrackMetadata'])[2]\
        /div[@class = 'sampleTrackInfo']\
        /h3/a[@class = 'trackName']/text")
    except:
        sampled_song_name ="None Listed"

    try:    
        sampled_song_artist = tree.xpath(
        "(//div[@class = 'sampleTrackMetadata'])[2]\
        /div[@class = 'sampleTrackInfo']/h3\
        /div[@class = 'sampleTrackArtists']\
        /a/text")

    except: 
        sampled_song_artist = "None Listed"

    try:
        sampled_song_year = int(tree.xpath(
        "(//div[@class = 'sampleTrackMetadata'])[2]\
        /div[@class = 'sampleReleaseDetails']\
        /div[@class = 'trackLabel']\
        /p[@class = 'label-details']\
        /a[@itemprop = 'datePublished']\
        /text"))
    except:
        sampled_song_year = "None Listed"

    try:
        sampled_album = tree.xpath(
        "(//div[@class = 'sampleTrackMetadata'])[2]\
        /div[@class = 'sampleReleaseDetails']\
        /p[@class = 'release-name']\
        /a/text")
    except:
        sampled_album = "None Listed"

    try:
        elements = tree.xpath(
        "//div[@class = 'section-header']/h2/innerHTML")
    except:
        elements = "None Listed"

    try:
        time_in_sampled_song_where_sample_appears = tree.xpath(
        "//strong[@id = 'sample-source-timing']/span/innerHTML")
    except:
        time_in_sampled_song_where_sample_appears = "None Listed"

    try:   
        contributor = tree.xpath(
        "//div[@class='sampleContributed sample-layout-row-right']/p/a/innerHTML")
    except:
        contributor = "None Listed"

    try:    
        contributor_votes = tree.xpath(
        "//div[@class='sampleContributed sample-layout-row-right']/p/text")
    except:
        contributor_votes = "None Listed"

    try:
        presence_of_and_throughout = tree.xpath(
        "(//div[@class='timing-wrapper'])[1]/text")
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
