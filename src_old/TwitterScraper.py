from bs4 import BeautifulSoup

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

import re

FOLLOWERS_DIV_CLASS = "r-1w6e6rj"
PARSE_UPDATES = False

class TwitterScraper:
    """
    THIS CLASS HAS BEEN DEPRECATED AND REPLACED BY TWITTERBATCHSCRAPER
    BUT CAN STILL BE USED FOR INDIVIDUAL SCRAPES
    An object to collect data from a twitter user page
    For now, this just includes number of followers
    """
    def __init__(self, user):
        self.username = user
        self.soup = None
        self.followers_text = ''
        self.followers = -1

    def make_soup(self):
        """
        Visit the twitter webpage of self.username and gather all html
        """
        error = ''
        self.twitter_url = "https://twitter.com/{}".format(self.username)
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(self.twitter_url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, FOLLOWERS_DIV_CLASS))
            )
        except TimeoutException:
            error = 'Error: Website timed out: {}'.format(self.twitter_url)
        
        html = driver.page_source
        driver.quit()

        self.soup = BeautifulSoup(html, "html.parser")
        if not self.soup:
            error = 'Error: Could not scrape the webpage: {}'.format(self.twitter_url)
        
        if error:
            print(error)

    def str_to_int(self, s):
        """
        Convert a twitter-formatted number to an int

        Args:
            s (str): string describing a number in the format "51.9K"

        Returns:
            int: number as an integer
        """
        s = s.replace(',', '')
        if 'K' in s:
            if '.' in s:
                decimals = len(s.strip('K').split('.')[1])
                z = 3 - decimals
            else:
                z = 3
            s = s.replace('K', '0'*z)
        elif 'M' in s:
            if '.' in s:
                decimals = len(s.strip('M').split('.')[1])
                z = 6 - decimals
            else:
                z = 6
            s = s.replace('M', '0'*z)
        s = s.replace('.', '')
        return int(s)

    def parse_followers(self):
        """
        Extract number of followers from text
        """
        pattern = r"(([\d.,KM])+) Followers"
        match = re.search(pattern, self.followers_text)
        if match:
            followers = match.group(1)
            self.followers = self.str_to_int(followers)
        else:
            if PARSE_UPDATES:
                error = '\n{}\nError: Could not parse followers from string. Skipping. \n{}'.format(self.twitter_url, self.followers_text)
                print(error)

    def scrape_followers(self):
        """
        Search through html for desired text
        """
        if not self.soup:
            self.make_soup()
        if self.soup:
            divs = self.soup.find_all("div", FOLLOWERS_DIV_CLASS)
            for div in divs:
                self.followers_text += div.getText()
            if (len(self.followers_text) > 0):
                self.parse_followers()
            else:
                if PARSE_UPDATES:
                    error = '\nError: Could not find any followers text on the page. Skipping.\n{}'.format(self.twitter_url)
                    print(error)
