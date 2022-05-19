import datetime

import database_manager

from RarityScraper import RarityScraper
from TwitterScraper import TwitterScraper
from DiscordScraper import DiscordScraper
from OpenseaScraper import OpenseaScraper


def scrape_rarity():
    """
    Runs the rarity scraper
    Records data into database
    """
    rscraper = RarityScraper()
    rscraper.scrape_upcoming()
    data = rscraper.dump_data()
    database_manager.enter("RARITY", data)
    project_data = [data['names'], data['twitter_id'], data['discord_id'], data['release_date'], data['currency']]
    database_manager.enter("PROJECTS", project_data)

def scrape_twitter(user_list):
    """
    Runs the twitter scraper on a list of usernames
    Records data into database
    Corrects any incorrect usernames found along the way

    Args:
        user_list (list of str): Twitter usernames to scrape
    """
    tscraper = TwitterScraper(user_list)
    failure_data = tscraper.batch_scrape()
    data = tscraper.dump_data()
    database_manager.enter("TWITTER", data)
    database_manager.remove("PROJECTS", failure_data)

def scrape_discord(user_list):
    """
    Runs the discord scraper on a list of usernames
    Records data into database
    Corrects any incorrect usernames found along the way

    Args:
        user_list (list of str): Discord usernames to scrape
    """
    dscraper = DiscordScraper(user_list)
    failure_data = dscraper.batch_scrape()
    data = dscraper.dump_data()
    database_manager.enter("DISCORD", data)
    database_manager.remove("PROJECTS", failure_data)

def scrape_opensea():
    """
    Runs the opensea scraper on a list of project names
    Records data into database
    For unfound projects, mark status as inactive
    """
    pass

def daily_scrape():
    """
    Runs available scrapers
    """
    today = datetime.date.today()
    print('Daily Scrape {}'.format(today))
    scrape_rarity()

    pre_release_twitter_users = database_manager.get("PROJECTS", "twitter_id", "release_date<{}".format(today))
    scrape_twitter(pre_release_twitter_users)

    pre_release_discord_users = database_manager.get("PROJECTS", "discord_id", "release_date<{}".format(today))
    scrape_discord(pre_release_discord_users)

    post_release_projects = database_manager.get("PROJECTS", "name", ["release_date>{}".format(today), "status=active"])
    scrape_opensea(post_release_projects)
    