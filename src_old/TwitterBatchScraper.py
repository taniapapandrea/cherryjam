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
SAVE_FREQUENCY = 5
LOGGING = False
ATTEMPTS = 2

class TwitterBatchScraper:
    """
    An object to collect data from a twitter user page
    For now, this just includes number of followers
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
        #TODO hide logging
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
        Returns the number of followers on the current page
        """
        followers = -1
        error = ''
        if self.soup:
            divs = self.soup.find_all("div", FOLLOWERS_DIV_CLASS)
            text = ''
            for div in divs:
                text += div.getText()
            if (len(text) > 0):
                pattern = r"(([\d.,KM])+) Followers"
                match = re.search(pattern, text)
                if match:
                    followers = self.str_to_int(match.group(1))
                else:
                    error = '\n{}\nError: Could not parse followers from string: {}\n'.format(self.current_user, text)
            else:
                error = '\n{}\nError: Could not find any followers text on the page\n'.format(self.current_user)
        if error and LOGGING:
            print(error)
        return followers

    def record_followers(self, user, followers):
        """
        Updates data with given user and followers
        """
        self.data.append({'twitter': user, 'followers': followers})

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
            i += 1
            self.current_user = user
            self.retrieve_url(self.current_user)
            self.load_wait()
            self.make_soup()
            followers = self.get_followers()

            if followers > -1:
                self.record_followers(user, followers)
            else:
                failures.append(user)

            # Save and update
            if (i%SAVE_FREQUENCY==0) or i==len(batch):
                df = pd.DataFrame(self.data)
                df.to_csv(self.csv)
            sys.stdout.write('\r[{}/{}]'.format(i, len(batch)))
            sys.stdout.flush()

        print('\nThis batch had {} successes and {} failures. Failure list:'.format( len(batch)-len(failures) , len(failures) ))
        for f in failures:
            print(f)
        return failures

    def run(self, savefile):
        """
        Runs a new batch of data collection
        If the savefile already contains data, those usernames will be skipped and not overwritten

        Args:
            savefile (str): csv file where data will be written (or added to)
        """
        # Update with any existing data
        if os.path.exists(savefile):
            df = pd.read_csv(savefile, usecols=['twitter', 'followers'])
            self.data = df.to_dict('records')
            finished = [x['twitter'] for x in self.data]
            self.users = [user for user in self.users if user not in finished]
        self.csv = savefile.split(os.getcwd()+'/')[1]

        # Open a browser
        self.open_chrome()

        # Run for all users, then again for failures
        i = 0
        todo = self.users
        while i < ATTEMPTS and len(todo) > 0:
            print('\nATTEMPT #{}'.format(i+1))
            todo = self.traverse_batch(todo)
            i += 1

        # Close browser
        self.driver.quit()