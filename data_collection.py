"""
string = datetime_object.strftime('%Y-%m-%d')
datetime_object = datetime.datetime.strptime(string, '%Y-%m-%d')
"""

import datetime

from DatabaseManager import DatabaseManager

from RarityScraper import RarityScraper
from TwitterScraper import TwitterScraper
# from DiscordScraper import DiscordScraper
# from OpenseaScraper import OpenseaScraper

def scrape_rarity(dm):
    """
    Runs the rarity scraper
    Records data into database

    Args:
        dm: DatabaseManager object
    """
    today = datetime.date.today().strftime('%Y-%m-%d')
    print('\nRarity Scrape {}'.format(today))

    rscraper = RarityScraper()
    rscraper.scrape_upcoming()
    data = rscraper.dump_data()
    
    for d in data:
        d['date'] = today
        dm.enter_rarity_record(d)
        
        master_project_keys = ['name', 'release_date', 'twitter_id', 'discord_id']
        master_project_data = {k:d[k] for k in master_project_keys}
        dm.enter_project(master_project_data)

def scrape_twitter(dm, user_list):
    """
    Runs the twitter scraper on a list of usernames
    Records data into database
    Corrects any incorrect usernames found along the way

    Args:
        dm (DatabaseManager object): db handle for entering data
        user_list (list of str): Twitter usernames to scrape
    """
    today = datetime.date.today().strftime('%Y-%m-%d')
    print('\nTwitter Scrape {}'.format(today))

    tscraper = TwitterScraper(user_list)
    failed_ids = tscraper.batch_scrape(tries=3)
    data = tscraper.dump_data()

    for d in data:
        d['date'] = today
        dm.enter_twitter_record(d)

    dm.remove_twitter_ids(failed_ids)

def scrape_discord(dm, user_list):
    """
    Runs the discord scraper on a list of usernames
    Records data into database
    Corrects any incorrect usernames found along the way

    Args:
        dm (DatabaseManager object): db handle for entering data
        user_list (list of str): Discord usernames to scrape
    """
    today = datetime.date.today().strftime('%Y-%m-%d')
    print('\nDiscord Scrape {}'.format(today))

def scrape_opensea(dm, project_list):
    """
    Runs the opensea scraper on a list of project names
    Records data into database
    For unfound projects, mark status as inactive

    Args:
        dm (DatabaseManager object): db handle for entering data
        project_list (list of str): NFT project names to scrape
    """
    today = datetime.date.today().strftime('%Y-%m-%d')
    print('\nOpensea Scrape {}'.format(today))

def daily_scrape():
    """
    Runs all scrapers and records data in database
    """
    today = datetime.date.today().strftime('%Y-%m-%d')

    dm = DatabaseManager()
    dm.begin_transaction()

    scrape_rarity(dm)

    twitter_ids_pre_release = dm.get_twitter_ids_pre_release(today)
    scrape_twitter(dm, twitter_ids_pre_release)

    # discord_ids_pre_release = dm.get_discord_ids_pre_release(today)
    # scrape_discord(dm, discord_ids_pre_release)

    # projects_post_release = dm.get_projects_post_release(today)
    # scrape_opensea(dm, projects_post_release)

    dm.end_transaction()