"""
string = datetime_object.strftime('%Y-%m-%d')
datetime_object = datetime.datetime.strptime(string, '%Y-%m-%d')
"""

from datetime import date

from DatabaseManager import DatabaseManager

from RarityScraper import RarityScraper
from TwitterScraper import TwitterScraper
from DiscordScraper import DiscordScraper
from OpenseaScraper import OpenseaScraper

def _today():
    return date.today().strftime('%Y-%m-%d')

def scrape_rarity(dm):
    """
    Runs the rarity scraper
    Records data into database
    Args:
        dm: DatabaseManager object
    """
    today = _today()
    print('\nRarity Scrape {}'.format(today))

    rscraper = RarityScraper()
    rscraper.scrape_upcoming()
    data = rscraper.dump_data()
    
    for d in data:
        d['date'] = today
        dm.enter_rarity_record(d)
        
        master_project_keys = ['name', 'release_date', 'twitter_id', 'discord_id', 'quantity']
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
    today = _today()
    print('\nTwitter Scrape {}'.format(today))

    tscraper = TwitterScraper(user_list)
    failed_ids = tscraper.batch_scrape()
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
    today = _today()
    print('\nDiscord Scrape {}'.format(today))

    dscraper = DiscordScraper(user_list)
    failed_ids = dscraper.batch_scrape()
    data = dscraper.dump_data()

    for d in data:
        d['date'] = today
        dm.enter_discord_record(d)

    dm.remove_discord_ids(failed_ids)

def scrape_opensea(dm, project_list):
    """
    Runs the opensea scraper on a list of project names
    Records data into database
    For unfound projects, mark status as inactive
    Args:
        dm (DatabaseManager object): db handle for entering data
        project_list (list of str): NFT project names to scrape
    """
    today = _today()
    print('\nOpensea Scrape {}'.format(today))

    oscraper = OpenseaScraper(project_list)
    failed_ids = oscraper.batch_scrape()

def daily_scrape():
    """
    Runs all scrapers and records data in database
    Note: Because the entire daily scrape happens in one transaction,
        pre/post release filters are based on yesterday
    """
    today = _today()
    dm = DatabaseManager()
    dm.begin_transaction()

    # Scrape project data
    # scrape_rarity(dm)

    # twitter_ids_pre_release = dm.get_twitter_ids_pre_release(today)
    # scrape_twitter(dm, twitter_ids_pre_release)

    # discord_ids_pre_release = dm.get_discord_ids_pre_release(today)
    # scrape_discord(dm, discord_ids_pre_release)

    # Scrape prices
    projects_post_release = dm.get_projects_post_release(today)
    #TODO check why this is only returning 4
    scrape_opensea(dm, projects_post_release)

    dm.end_transaction()
