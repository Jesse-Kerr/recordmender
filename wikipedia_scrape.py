from time import sleep
from pyvirtualdisplay import Display
from selenium import webdriver

def get_links_from_wikipage(all_artists):

    page_artists = driver.find_elements_by_xpath("//div[@class='mw-category-group']/ul/li/a")
    page_artists = [artist.get_attribute('title') for artist in page_artists]
    all_artists = all_artists + page_artists
    return all_artists

def go_to_next_page():
    try:
        next_page = driver.find_element_by_link_text('next page')
        next_page.click()
    except: 
        print("No more pages")
        more_pages = False

if __name__ == "__main__":
    all_artists = []
    more_pages = True
    driver = webdriver.Firefox()
    driver.get("https://en.wikipedia.org/wiki/Category:American_hip_hop_record_producers")
    while more_pages == True:
        all_artists = get_links_from_wikipage(all_artists)
        go_to_next_page()

print(all_artists)
print(len(all_artists))
