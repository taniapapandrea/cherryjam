from bs4.element import Tag


class Rarity_PageElement:
    """
    An object representing a <tr></tr> element on https://rarity.tools/upcoming/
    containing information about an upcoming NFT project. This object is meant to
    read the page and gather necessary text. Heavier processing is reserved for
    the Rarity_NFTData class.
    """

    def __init__(self, html):
        """
        When HTML is passed in, process all information

        Args:
            html (bs4.elementTag): object containing a <tr></tr> html tree
        """
        self.html = html

        self.name = None
        self.description = None
        #self.image_urls = []
        self.quantity = None

        self.price_text = ''
        self.release_text = ''

        self.discordurl = None
        self.twitterurl = None
        self.website = None

        self.process_html()

    def display_pretty(self):
        """
        Displays all useful attributes
        """
        print("--------------------------------------------")
        print("Name: {}".format(self.name))
        print("Description: {}".format(self.description))
        # print("Images:")
        # for image in self.image_urls:
        #     print(image)
        print("Discord: {}".format(self.discordurl))
        print("Twitter: {}".format(self.twitterurl))
        print("Website: {}".format(self.website))
        print("Quantity: {}".format(self.quantity))
        print("Price Info: {}".format(self.price_text))
        print("Release Info: {}".format(self.release_text))
        print("--------------------------------------------")

    def to_string(self, s):	
        """
        Safe method to use instead of (str)
        This prevents UnicodeEncodeError which was caused by some unknown characters on this page

        Args:
            s (str): text scraped from a website, presumably a string but maybe with weird characters
        """
        try:
            string = str(s)
        except UnicodeEncodeError as e:
            # clean string of unknown characters
            s = ('').join([i for i in s if ord(i) in range(128)])
            string = str(s)
        return string

    def read_title_cell(self, td):
        """
        Reads the title section of the listing and sets name, description, image_urls

        Args:
            td (bs4.elementTag): object containing a <td></td> html tree
        """
        divs = [x for x in td.contents if isinstance(x, Tag)]
        title_div = divs[0]
        tagline_div = divs[1]
        #images_div = divs[2]

        # Name
        self.name = self.to_string(title_div.getText().strip())
        # Description
        self.description = str(tagline_div.getText().strip())
        # Image paths
        # paths = [str(img.get("src")) for img in images_div.find_all("img")]
        # self.image_urls = paths

    def read_links_cell(self, td):
        """
        Extracts links urls and sets discordurl, twitterurl, website

        Args:
            td (bs4.elementTag): object containing a <td></td> html tree
        """
        links = [x for x in td.contents if isinstance(x, Tag)]
        if len(links) == 3:
            discord_link = links[0]
            twitter_link = links[1]
            website_link = links[2]
            # Discord
            self.discordurl = self.to_string(discord_link.get("href"))
            # Twitter
            self.twitterurl = self.to_string(twitter_link.get("href"))
            # Website
            self.website = self.to_string(website_link.get("href"))
        else:
            # Sometimes one link is missing
            # In this case, we can't determine the order, so leave unassigned
            self.discordurl = None
            self.twitterurl = None
            self.website = None

    def read_data_cell(self, td):
        """
        Reads the data section and sets price_text, quantity

        Args:
            td (bs4.elementTag): object containing a <td></td> html tree
        """
        data = [x for x in td.contents if isinstance(x, Tag)]
        price = data[0]
        count = data[1]
        # Price
        price_text = str(price.getText().strip())
        self.price_text = price_text
        # Quantity
        total_text = str(count.getText().strip())
        if " Total" in total_text:
            number_text = total_text.split(" Total")[0].replace(",", "")
            if number_text:
                self.quantity = int(number_text)

    def read_release_cell(self, td):
        """
        Reads the release section and sets release_text

        Args:
            td (bs4.elementTag): object containing a <td></td> html tree
        """
        divs = [x for x in td.contents if isinstance(x, Tag)]
        text = ""
        for div in divs:
            text += str(div.getText())
            text += "\n"
        self.release_text = text

    def process_html(self):
        """
        Break the main chunk of html into smaller pieces
        """
        tds = [x for x in self.html.contents if isinstance(x, Tag)]
        title_cell = tds[0]
        links_cell = tds[1]
        data_cell = tds[2]
        release_cell = tds[3]
        self.read_title_cell(title_cell)
        self.read_links_cell(links_cell)
        self.read_data_cell(data_cell)
        self.read_release_cell(release_cell)
