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

djs = ['4th Disciple',
 '9th Wonder',
 'The 45 King',
 '50 Cent',
 '88-Keys',
 '808 Mafia',
 'DJ A-Tron',
 'Aalias',
 'DJ Abilities',
 'MC ADE',
 'Cisco Adler',
 'Aesop Rock',
 'Afrika Islam',
 'Agallah',
 'Akon',
 'The Alchemist (musician)',
 'Alias (musician)',
 'AmpLive',
 'Ant (producer)',
 'Antimc',
 'Aone Beats',
 'AraabMuzik',
 'Arabian Knight (record producer)',
 'Arkatech Beatz',
 "Reuben 'Bonyx' Armstrong",
 'Ashanti (singer)',
 'Andre Afram Asmar',
 'Astronautalis',
 'Astronautica',
 'The Audible Doctor',
 'The Audibles',
 'Dallas Austin',
 'Cities Aviv',
 'Awon',
 'Ayatollah (record producer)',
 'B-U',
 'B.o.B',
 'Baauer',
 'Babel Fishh',
 'DJ Babu',
 'Cosmo Baker',
 'C. Ballin',
 'Bangladesh (record producer)',
 'Kirko Bangz',
 'Ant Banks',
 'David Banner',
 'Nick Barat',
 'ASAP Bari',
 'Baron Zen',
 'Jean-Michel Basquiat',
 'Bass Brothers',
 'Count Bass D',
 'Batsauce',
 'Mark Batson',
 'Battlecat (record producer)',
 'The Beat Bully',
 'Da Beatminerz',
 'The Beatnuts',
 'Jahlil Beats',
 'Joe Beats',
 'Kane Beatz',
 'Mike Beatz',
 'Thavius Beck',
 'Brandon Bell (record producer)',
 'Anthony Ian Berkeley',
 'Beyoncé',
 'Jeff Bhasker',
 'Big Boi',
 'Big Cats (producer)',
 'Big Daddy Kane',
 'Big K.R.I.T.',
 'Bigg D',
 'Bighead (producer)',
 'Birdman (rapper)',
 'Tha Bizness',
 'Bizzle',
 'Bkorn',
 'Blac Elvis',
 'Black Milk',
 'Blackout (musician)',
 'Blaqstarr',
 'Shady Blaze',
 'Blockhead (music producer)',
 'Blue Sky Black Death',
 'Blueprint (rapper)',
 'Maga Bo',
 'DJ Bobcat',
 'Bomarr',
 'The Bomb Squad',
 'Miles Bonny',
 'Dionté Boom',
 'Metro Boomin',
 'Toni Braxton',
 'Craig Brockman',
 'Brother Ali',
 'Kerry Brothers Jr.',
 'Kev Brown',
 'Sleepy Brown',
 'Tommy Brown (record producer)',
 'Ron Browz',
 'Freddie Bruno',
 'Buckwild',
 "Bud'da",
 'Budo (musician)',
 'DJ Burn One',
 'Rheji Burrell',
 'Kandi Burruss',
 'Busdriver',
 'C-Bo',
 'Cadillac Muzik',
 'Cage (rapper)',
 'Crystal Caines',
 'DJ Candlestick',
 'Don Cannon',
 'Nick Cannon',
 'Cardiak',
 'Cardo (record producer)',
 'Mariah Carey',
 'DJ Cash Money',
 'The Cataracs',
 'Celestaphone',
 'Cellski',
 'Celph Titled',
 'Rogét Chahayed',
 'Chamillionaire',
 'DJ Cocoa Chanelle',
 'Jeff Chang (journalist)',
 'Matt Chang',
 'Chef Tone',
 'Traedonya Chequelle',
 'Travis Cherry',
 'Chilly Chill',
 'Choice37',
 'Chosen Effect',
 'Chyskillz',
 'Cipha Sounds',
 'Don Cisco',
 'Ckay1',
 'Clams Casino (musician)',
 'Mike E. Clark',
 'DJ Clay',
 'DJ Clue?',
 'Cold 187um',
 'J. Cole',
 'Charles Coleman (artist)',
 'Mr. Collipark',
 'Sean Combs',
 'Controller 7',
 'Cool & Dre',
 'The Cool Kids',
 'Drew Correa',
 'Bryan-Michael Cox',
 'Crazy Toones',
 'CunninLynguists',
 'D-Shot',
 'Tony D',
 'Da Internz',
 "Da'unda'dogg",
 'Daddy Kev',
 'Daddy-O (musician)',
 'Daedelus (musician)',
 'DJ Dahi',
 'Damu the Fudgemunk',
 'Dan the Automator',
 'Danger Mouse (musician)',
 'Danja (record producer)',
 'Dash (rapper)',
 'Damon Dash',
 'J. Dash',
 'Tony Dawsey',
 'Dday One',
 'Jae Deal',
 'Mike Dean (record producer)',
 'Decap (producer)',
 'Mr. Del',
 'Brandun DeShay',
 'Detail (record producer)',
 'Scoop DeVille',
 'Diamond D',
 'Diaz Brothers',
 'Dibiase',
 'Digi+Phonics',
 'Daz Dillinger',
 'Diplo',
 'DJ Nasty & LVM',
 'Djemba Djemba',
 'Snoop Dogg',
 'D. A. Doman',
 'Domingo (producer)',
 'Doseone',
 'Dot da Genius',
 'Dot N Pro',
 'Chase N Dough',
 'Doughboy (record producer)',
 'The Dramatikz',
 'Dr. Dre',
 'Droop-E',
 'Drumma Boy',
 'Dub-L']

class whoSampledScraper():

    def __init__(self):

        '''
        Initializes scraper and goes to who_sampled.com
        '''
        self.driver = webdriver.Firefox()
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
        search.send_keys(self.dj)
        sleep(2)
        artist = self.driver.find_element_by_id('searchArtists')
        artist.click()
        sleep(2)
    
    def filter_page_by_songs_artist_sampled(self):
        dropdown = self.driver.find_element_by_xpath("//div[@class='optionMenu artistPageMenu']")
        dropdown.click()
        #sleep(2)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", dropdown)

        # the tracks sampled is always the second one
        sampled = self.driver.find_element_by_xpath("//ul[@class = 'expanded']/li[2]")
        sampled.click()
        sleep(2)
        
    def get_num_samples_insert_mongo(self):
        num_samples = self.driver.find_elements_by_xpath("//span[@class='section-header-title']")[0].get_attribute('innerHTML')
        dj_meta_info.insert_one({"dj" : self.dj, "num_samples" : num_samples})

    def get_link_to_tracks_by_dj(self):
        '''
        Gets the links to the tracks for the DJ on that page (10 at most)
        '''
        tracks = self.driver.find_elements_by_xpath("//h3[@class='trackName']/a")
        track_links = [track.get_attribute('href') for track in tracks]

        #insert into MongoDB
        links_to_tracks_per_dj.update({'dj': self.dj}, {'$push': {'track_links': {'$each' :track_links}}})    
            
    def go_to_next_page(self):
        try:
            next_page = self.driver.find_element_by_class_name("next")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", next_page)
            next_page.click()
            sleep(1)
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
    scraper = whoSampledScraper()
    for dj in djs: 
        scraper.go_to_dj_page("Kanye West")
        scraper.filter_page_by_songs_artist_sampled()
        scraper.get_num_samples_insert_mongo()
        while scraper.more_pages == True:
            scraper.get_link_to_tracks_by_dj()
            scraper.go_to_next_page()
    scraper.driver.quit()