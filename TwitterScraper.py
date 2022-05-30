import sys
import re
import os

from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

FOLLOWERS_DIV_CLASS = "r-1w6e6rj"
LOGGING = False
ATTEMPTS = 2

class TwitterScraper:
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

    def retrieve_url(self, user):
        """
        Open a url on the virtual Chrome browser
        """
        url =  "https://twitter.com/{}".format(user)
        try:
            self.driver.get(url)
        except:
            error = '\n{}\nError: Could not retrieve the url: {}'.format(self.current_user, url)
            if LOGGING: 
                print(error)

    def load_wait(self):
        """
        Wait for the page to load
        """
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, FOLLOWERS_DIV_CLASS))
            )
        except TimeoutException:
            error = '\n{}\nError: Website timed out'.format(self.current_user)
            if LOGGING:
                print(error)

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

    def calculate_activity_score(self):
        """
        Attempts to quantify the activity / community / life displayed on the profile

        Returns:
            int: rating between 0-100
                0 = bot suspected
                100 = engaged human community
        """
        score = -1
        if self.soup:
            pass
        return score

    def traverse_batch(self, batch):
        """
        Iterates through a list of users: loads each webpage, gathers html, and records followers data

        Args:
            batch (list[str]): usernames to run

        Returns:
            list[str]: usernames that failed
        """
        failures = []

        for i, user in enumerate(batch):
            # Load the webpage
            i += 1
            self.current_user = user
            self.retrieve_url(self.current_user)
            self.load_wait()
            self.make_soup()

            # Gather follower data
            followers, following = self.get_followers()
            if followers > -1 and following > -1:
                user_data = {'twitter_id': user, 'followers': followers, 'following': following}

                # Gather activity data
                activity = self.calculate_activity_score()
                if activity > -1:
                    user_data['activity'] = activity

                self.data.append(user_data)
            else:
                failures.append(user)

            sys.stdout.write('\r[{}/{}]'.format(i, len(batch)))
            sys.stdout.flush()

        print('\nThis batch had {} successes and {} failures. Failure list:'.format( len(batch)-len(failures) , len(failures) ))
        for f in failures:
            print(f)
        return failures

    def batch_scrape(self, tries=2):
        """
        Runs a new batch of data collection

        Args:
            tries (int): number of times to load each user in case of failure

        Returns:
            list (str): users that failed after all tries
        """
        self.open_chrome()

        todo = self.users
        for i in range(tries):
            print('\nATTEMPT #{}'.format(i+1))
            todo = self.traverse_batch(todo)

        self.driver.quit()
        failures = todo
        return failures

    def dump_data(self):
        """
        Returns:
            list of dicts: all scraped data

        """
        return self.data