import sys
import re

from bs4 import BeautifulSoup
from bs4.element import Tag

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from DatabaseManager import DatabaseManager

SEARCHBAR_DIV_CLASS = 'sc-3dr67n-0'
PREVIEW_RESULTS_ID = "NavSearch--results"
LOGGING = True
WAIT_TIME = 5

class OpenseaScraper:
    """
    An object to collect data from opensea marketplace
    """
    def __init__(self, projects):
        self.projects = projects
        self.current_project = None
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

    def search_find_match(self, project, quantity):
        """
        Searches for a Collection match in the preview search results

        Args:
            project(str): Project name to match
            quantity(int): Number of items to match

        Returns:
            bs4.Element.Tag: object containing a <a> html element
        """
        print(project)
        self.load_wait_results()
        self.make_soup()
        ul = self.soup.find("ul", id=PREVIEW_RESULTS_ID)
        lis = [x for x in ul if isinstance(x, Tag)]
        for li in lis:
            text = li.getText()
            if text == 'COLLECTIONS':
                pass
            elif text == 'ITEMS':
                break
            else:
                text_div = li.contents[0].contents[1]
                name_text = text_div.contents[0].contents[0].getText()
                items_text = text_div.contents[0].contents[1].getText()

                found_name = name_text.lower()
                found_items = int(items_text[:-6].replace(',',''))

                if (found_name == project) and (found_items == quantity):
                    # Found a match!
                    link = li.find('a')
                    return link
                else:
                    if LOGGING:
                        msg = "\nCould not find a search result for {}, {}".format(project, quantity)
                        print(msg)
                    return None

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
            self.load_wait_results()
            self.make_soup()

            # Lookup quantity from db
            dm = DatabaseManager()
            quantity = dm.lookup_quantity(project)
            match = self.search_find_match(project, quantity)

            if match:
                self.click_result(match)
                # self.load_wait_projectpage()
                self.make_soup()
                name = self.soup.find('h1').getText()
                print(name)

                # Gather data
                # price = self.get_price()
                # if price:
                #     hls = self.get_highest_last_price()
                #     lp = self.get_lowest_price()
                #     project_data = {'name': project, 'price': price, 'highest_last_sale': hls, 'lowest_price': lp}
                #     self.data.append(project)
                # else:
                #     failures.append(project)
                
            else:
                failures.append(project)

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