import re
import datetime
import os

from Rarity_PageElement import Rarity_PageElement

PARSE_UPDATES = False

class Rarity_NFTData:
    """
    An object to represent an NFT project and all known data associated with it.
    This object expects scraped text from the Rarity_PageElement class. Its goal 
    is to process raw text into usable pieces of data.
    """

    def __init__(self, name):
        self.name = name
        self.description = None
        #self.image_urls = []
        self.quantity = None
        
        self.currency = None
        self.has_presale = False
        self.presale_price = None
        self.starting_price = None
        self.presale_date = None
        self.release_date = None

        self.discord = None
        self.twitter = None
        self.website = None

    def display_pretty(self):
        """
        Displays all useful attributes
        """
        print("--------------------------------------------")
        print("Name: {}".format(self.name))
        # print("Description: {}".format(self.description))
        # print("Images:")
        # for image in self.image_urls:
        #     print(image)
        # print("Quantity: {}".format(self.quantity))
        # print("\n")
        # print("Currency: {}".format(self.currency))
        if self.has_presale:
            print("Presale Date: {}".format(self.presale_date))
            # print("Presale Price: {}".format(self.presale_price))
        print("Release Date: {}".format(self.release_date))
        # print("Starting Price: {}".format(self.starting_price))
        # print("\n")
        # print("Discord: {}".format(self.discord))
        # print("Twitter: {}".format(self.twitter))
        # print("Website: {}".format(self.website))
        print("--------------------------------------------")

    def asDict(self):
        """
        Returns a dictionary representation of data
        """
        d = {}
        d['name'] = self.name
        #_urls'] = self.image_urls
        d['quantity'] = self.quantity
        d['currency'] = self.currency
        d['has_presale'] = self.has_presale
        d['presale_price'] = self.presale_price
        d['presale_date'] = self.presale_date
        d['starting_price'] = self.presale_price
        d['release_date'] = self.presale_date
        d['discord'] = self.discord
        d['twitter'] = self.twitter
        d['website'] = self.website
        return d

    def discord_user_from_url(self, url):
        #TODO check if this page exists
        user = url.split("/")[-1]
        return user

    def twitter_user_from_url(self, url):
        #TODO check if this page exists
        user = url.split("/")[-1]
        return user

    def parse_price(self, s):
        """
        Converts a description of price into value and currency
        
        Args:
            s (str): non empty raw text, e.g. '1.0 SOL'

        Returns:
            tuple (float, str): value, currency
        """
        error = ''
        if ('tbd' in s.lower()) or ('tba' in s.lower()):
            result = None, None
        elif 'free' in s.lower():
            result = 0, None
        else:
            pattern = r"([\d\.]+)([\s]*)([A-Z]{3,})"
            match = re.search(pattern, s)
            if match:
                try:
                    price = float(match.group(1))
                    currency = match.group(3)
                    result = price, currency
                except:
                    error = '\n{}\nError: Could not parse price from string:\n{}'.format(self.name, s)
                    result = None, None
            else:
                error = '\n{}\nError: Could not parse price from string:\n{}'.format(self.name, s)
                result = None, None
        if error and PARSE_UPDATES:
            print(error)
        return result

    def extract_price_info(self, text):
        """
        Extract price information from raw text.
        This could include has_presale, currency, starting_price, presale_price
        This does not handle multiple presales; will only take first and last

        Args:
            text (str): raw text
        """
        error = ''
        lines = [x for x in text.split("\n") if x!='']
        if len(lines)==1:
            self.starting_price, self.currency = self.parse_price(lines[0])
            self.presale_price = None
        elif len(lines)>1:
            if len(lines)>2:
                error = '\n{}\nWarning: Some price data was not extracted:\n{}'.format(self.name, text)
            price1, currency1 = self.parse_price(lines[0])
            price2, currency2 = self.parse_price(lines[1])
            # If first sale is free, currencies might not match
            if (price1 == 0) or (currency1 == currency2):
                self.has_presale = True
                self.presale_price = price1
                self.starting_price = price2
                self.currency = currency2
        if error and PARSE_UPDATES:
            print(error)

    def month_to_int(self, s):
        months = {"january":1, "february":2, "march":3, "april":4, "may":5, "june":6, 
        "july":7, "august":8, "september":9, "october":10, "november":11, "december":12}
        if s.lower() in months:
            return months[s]
        else:
            return -1

    def parse_release_date(self, s):
        """
        Converts a description of a date / time into a datetime object
        
        Args:
            s (str): raw text, e.g. '8:00 am (America/Vancouver) Friday, January 28th 2022'

        Returns:
            Datetime: object describing the date / time in this string
        """
        error = ''
        s = s.strip().lower()
        if ('tbd' in s) or ('tba' in s) or s=='':
            return None
        
        if 'today' in s:
            date_object = datetime.date.today()
        elif 'tomorrow' in s:
            date_object = datetime.date.today() + datetime.timedelta(days=1)
        elif 'yesterday' in s:
            date_object = datetime.date.today() - datetime.timedelta(days=1)
        else:
            # parse "friday, january 28th 2022"
            date_pattern = r"([a-z]+), ([a-z]+) (\d{1,2}[a-z]{2}) (\d{4})"
            match = re.search(date_pattern, s)
            if match:
                month = self.month_to_int(match.group(2))
                day = int(match.group(3).strip('stndrth'))
                year = int(match.group(4))
                date_object = datetime.date(year, month, day)
            else:
                if PARSE_UPDATES:
                    error = '\n{}\nError: Could not parse date from string:\n{}'.format(self.name, s)
                    print(error)
                return None

        # parse "8:00 am (america/vancouver)"
        pattern = r"([\d\:]{4,5})\s+(am|pm)\s+(\([\w|/]+\))\s*"
        match = re.search(pattern, s)
        if match:
            time = match.group(1)
            ampm = match.group(2)
            timezone = match.group(3)
            hour, minute = time.split(':')
            if ampm == 'pm':
                hour = int(hour) + 12
                if hour == 24:
                    hour = 0
            time_object = datetime.time(int(hour), int(minute))
        else:
            time_object = datetime.time(0, 0)
        result = datetime.datetime.combine(date_object, time_object)
        return result

    def extract_release_info(self, text):
        """
        Extract release date information from raw text.
        This could include has_presale, release_date, presale_date

        args:
            text (str): raw text
        """
        error = ''
        releases = text.lower().split('sale')
        if len(releases)==1:
            # Expected for single sale
            self.release_date = self.parse_release_date(releases[0])
        elif len(releases)==3:
            # Expected for presale and regular sale
            self.has_presale = True
            self.presale_date = self.parse_release_date(releases[1])
            self.release_date = self.parse_release_date(releases[2])
        elif len(releases)==2:
            if 'pre' in releases[0]:
                self.has_presale = True
                self.presale_date = self.parse_release_date(releases[1])
            else:
                error = '\n{}\nError: Could not extract release info from text:\n{}'.format(self.name, text)
        else:
            error = '\n{}\nError: Could not extract release info from text:\n{}'.format(self.name, text)
        if error and PARSE_UPDATES:
            print(error)
            
    def import_from_rarity_page_element(self, listing):
        """
        Import data from a RarityUpcomingListing object

        Args:
            listing: RarityUpcomingListing() object
        """
        self.description = listing.description
        #self.image_urls = listing.image_urls
        self.quantity = listing.quantity
        self.website = listing.website
        if listing.discordurl:
            self.discord = self.discord_user_from_url(listing.discordurl)
        if listing.twitterurl:
            self.twitter = self.twitter_user_from_url(listing.twitterurl)
        self.extract_price_info(listing.price_text)
        self.extract_release_info(listing.release_text)
