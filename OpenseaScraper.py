import sys
import re

from bs4 import BeautifulSoup

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from DatabaseManager import DatabaseManager

SEARCHBAR_DIV_CLASS = 'sc-3dr67n-0'
PREVIEW_RESULTS_ID = "tippy-471"
LOGGING = False
WAIT_TIME = 5

class OpenseaScraper:
    """
    An object to collect data from twitter user pages
    """
    def __init__(self, users):
        self.users = users
        self.current_user = None
        self.soup = None
        self.data = []

    def open_chrome(self):
        """
        Open up a virtual Chrome browser
        """
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        print('====== CherryJam driving ======')

    def retrieve_opensea_url(self):
        """
        Open a url on the virtual Chrome browser
        """
        url =  "https://opensea.io/"
        try:
            self.driver.get(url)
        except:
            error = '\nError: Could not retrieve the url: {}'.format(url)
            if LOGGING: 
                print(error)

    def load_wait_homepage(self):
        """
        Wait for the page to load
        """
        try:
            WebDriverWait(self.driver, WAIT_TIME).until(
                EC.presence_of_element_located((By.CLASS_NAME, SEARCHBAR_DIV_CLASS))
            )
        except TimeoutException:
            error = '\nError: Homepage timed out'
            if LOGGING:
                print(error)

    def load_wait_results(self):
        """
        Wait for the search results to load
        In the results preview (after typing but not pressing enter)
        """
        try:
            WebDriverWait(self.driver, WAIT_TIME).until(
                EC.presence_of_element_located((By.ID, PREVIEW_RESULTS_ID))
            )
        except TimeoutException:
            error = '\nError: Preview results timed out'
            if LOGGING:
                print(error)

    # def load_wait_projectpage(self):
    #     """
    #     Wait for the page to load
    #     """
    #     try:
    #         WebDriverWait(self.driver, WAIT_TIME).until(
    #             EC.presence_of_element_located((By.CLASS_NAME, SEARCHBAR_DIV_CLASS))
    #         )
    #     except TimeoutException:
    #         error = '\n{}\nError: Project page timed out'.format(self.current_project)
    #         if LOGGING:
    #             print(error)

    def make_soup(self):
        """
        Get the current html                        
        """
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        if soup:
            self.soup = soup
        else:
            error = '\n{}\nError: Could not get current html'.format(self.current_user)
            if LOGGING:
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

    def get_followers(self):
        """
        Retrieves follower data from the twitter profile

        Returns:
            tuple (int): followers, following
        """
        followers = -1
        following = -1
        error = ''

        if self.soup:
            divs = self.soup.find_all("div", FOLLOWERS_DIV_CLASS)
            text = ''
            for div in divs:
                text += div.getText()
            if (len(text) > 0):

                # Followers
                pattern = r"(([\d.,KM])+) Followers"
                match = re.search(pattern, text)
                if match:
                    followers = self.str_to_int(match.group(1))
                else:
                    error = '\n{}\nError: Could not parse followers from string: {}\n'.format(self.current_user, text)

                # Following
                pattern = r"(([\d.,KM])+) Following"
                match = re.search(pattern, text)
                if match:
                    following = self.str_to_int(match.group(1))
                else:
                    error = '\n{}\nError: Could not parse following from string: {}\n'.format(self.current_user, text)
            
            else:
                error = '\n{}\nError: Could not find any followers text on the page\n'.format(self.current_user)
        if error and LOGGING:
            print(error)
        return followers, following

    def batch_scrape(self):
        """
        Runs a new batch of data collection

        Returns:
            list (str): projects that were not found
        """
        self.open_chrome()
        self.retrieve_opensea_url()
        self.load_wait_homepage()

        failures = []

        for i, project in enumerate(self.projects):
            i += 1
            self.current_project = project

            # Type name into search bar
            input = self.driver.find_element(By.XPATH, "//input")
            input.send_keys(project)

            # Lookup quantity from db
            dm = DatabaseManager()
            quantity = dm.lookup_quantity(project)

            # Look for a match
            self.load_wait_results()
            self.make_soup()

            # If match found
                # Click on option

                # Load wait
                # self.make_soup()

                # Gather data
                # price = self.get_price()
                # if price:
                #     hls = self.get_highest_last_price()
                #     lp = self.get_lowest_price()
                #     project_data = {'name': project, 'price': price, 'highest_last_sale': hls, 'lowest_price': lp}
                #     self.data.append(project)
                # else:
                #     failures.append([project])
                
            # Else
                # add to failures

            sys.stdout.write('\r[{}/{}]'.format(i, len(self.projects)))
            sys.stdout.flush()

        self.driver.quit()
        return failures

    def dump_data(self):
        """
        Returns:
            list of dicts: all scraped data

        """
        return self.data