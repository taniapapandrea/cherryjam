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

MEMBERS_DIV_CLASS = "activityCount-2n5Mj9"
LOGGING = False
WAIT_TIME = 5

class DiscordScraper:
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
            WebDriverWait(self.driver, WAIT_TIME).until(
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

            # Gather member data
            online, total = self.get_members()
            if online > -1 and total > -1:
                user_data = {'discord_id': user, 'online': online, 'members':total}

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

    def batch_scrape(self, tries=3):
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