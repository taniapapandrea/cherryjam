import datetime
import os
import sys

from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from Rarity_PageElement import Rarity_PageElement
from Rarity_NFTData import Rarity_NFTData

RARITY_URL = "https://rarity.tools/upcoming"

class RarityScraper:
    """
    An object to collect data from the website: rarity.tools
    """
    def __init__(self):
        self.soup = None
        self.NFTs = []

    def make_soup(self):  
        """
        Visit the webpage at self.rarity_tools_utl and gather all html
        """
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(RARITY_URL)
        print('====== CherryJam driving ======')

        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dataTable"))
        )

        html = driver.page_source
        driver.quit()

        self.soup = BeautifulSoup(html, "html.parser")
        if not self.soup:
            print('Error: Could not scrape the webpage {}'.format(RARITY_URL))

    def scrape_upcoming(self):
        """
        Runs a new batch of data collection from the 'Upcoming' page
        Populates self.NFTs with the data found
        """
        self.make_soup()
        if self.soup:

            content_trs = self.soup.find_all("tr", "text-left", "text-gray-800")
            for tr in content_trs:
                # Gather html data
                listing = Rarity_PageElement(tr)

                if len(listing.name) > 0:
                    
                    # Process html data
                    dataobject = Rarity_NFTData(listing.name)
                    dataobject.import_from_rarity_page_element(listing)
                    
                    # Record data
                    self.NFTs.append(dataobject.asDict())

    def dump_data(self):
        """
        Returns:
            list of dicts: self.NFTs containing all scraped data
        """
        return self.NFTs