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

from constants import DISCORD_COLUMNS as d_cols
MEMBERS_DIV_CLASS = "activityCount-2n5Mj9"
SAVE_FREQUENCY = 5
LOGGING = False
ATTEMPTS = 2

class DiscordBatchScraper:
    """
    An object to collect data from a discord user page
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
        url =  "https://discord.com/invite/{}".format(user)
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
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, MEMBERS_DIV_CLASS))
            )
        except TimeoutException:
            error = '\n{}\nError: Website not loaded or account not found'.format(self.current_user)
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
        Convert a discord-formatted number to an int

        Args:
            s (str): string describing a number in the format "123,456"

        Returns:
            int: number as an integer
        """
        s = s.replace(',', '')
        return int(s)

    def get_members(self):
        """
        Finds members information on a discord invite page

        Returns
            tuple(int): online members, total members
        """
        online, total = -1, -1
        error = ''
        if self.soup:
            div = self.soup.find("div", MEMBERS_DIV_CLASS)
            text = div.getText() if div else ''
            if (len(text) > 0):
                # parse 123,456 Online98,000 Members
                pattern = r"((?:\d{1,3},)?\d{1,3}) Online((?:\d{1,3},)?\d{1,3}) Members"
                match = re.search(pattern, text)
                if match:
                    online = self.str_to_int(match.group(1))
                    total = self.str_to_int(match.group(2))
                else:
                    error = '\n{}\nError: Could not parse int from string: {}\n'.format(self.current_user, text)
            else:
                error = '\n{}\nError: Could not find any members text on the page\n'.format(self.current_user)
        if error and LOGGING:
            print(error)
        return online, total

    def record_followers(self, user, online, total):
        """
        Updates data with given user and members (online and total)
        """
        self.data.append({'discord': user, 'online_members': online, 'total_members': total})

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
            online, total = self.get_members()

            if online > -1 and total > -1:
                self.record_followers(user, online, total)
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
            df = pd.read_csv(savefile, usecols=d_cols)
            self.data = df.to_dict('records')
            finished = [x['discord'] for x in self.data]
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