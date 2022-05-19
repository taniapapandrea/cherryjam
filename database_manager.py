DB_PATHS = {
    'PROJECTS': '/db/master_project_list.db',
    'RARITY' : '/db/rarity_scraped_data.db',
    'TWITTER' : '/db/twitter_scraped_data.db',
    'DISCORD' : '/db/discord_scraped_data.db',
    'OPENSEA' : '/db/opensea_scraped_data.db'}


def get(database, data, condition):
    """
    Get something from a database

    Returns:
        requested data
    """
    pass

def enter(database, data):
    """
    Enters new data into a database
    In case of conflicts, keep the newer data but log all overwritten data

    Args:
        database (str): name of a database
        data (dict): data to enter
    """
    file = DB_PATHS[database]
    pass

def remove(database, data):
    """
    Removes data from a database (e.g. usernames that have caused failures)

    Args:
        database (str): name of a database
        data (dict): data to remove
    """
    file = DB_PATHS[database]
    pass