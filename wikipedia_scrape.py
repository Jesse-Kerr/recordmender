from time import sleep
from pyvirtualdisplay import Display
from selenium import webdriver
import re

display = Display(visible=0, size=(1024, 768))
display.start()

driver = webdriver.Firefox()

def get_links_from_wikipage():
    page_artists = driver.find_elements_by_xpath("//div[@class='mw-category-group']/ul/li/a")
    return [artist.get_attribute('title') for artist in page_artists]

def go_to_next_page():
    try:
        next_page = driver.find_element_by_link_text('next page')
        driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
        next_page.click()
        return True
    except: 
        print("Done with Wiki Section")
        return False

def get_all_artists():
    all_artists = []
    more_pages = True
    driver.get("https://en.wikipedia.org/wiki/Category:American_hip_hop_record_producers")
    while more_pages == True:
        page_artists = get_links_from_wikipage()
        all_artists += page_artists
        more_pages = go_to_next_page()
    all_artists = [re.sub("[\(\[].*?[\)\]]", "", artist) for artist in all_artists]
    return all_artists