"""
_scraped_data databases are meant to be historical records;
no data should be removed

master_ databases are meant to be an accurate upkept record;
incorrect data should be removed or updated

CREATE TABLE master_project_list(
name TEXT NOT NULL PRIMARY KEY,
release_date TEXT DEFAULT '',
twitter_id TEXT DEFAULT '',
discord_id TEXT DEFAULT '',
quantity INTEGER,
status TEXT,
rank INTEGER);

CREATE TABLE rarity_scraped_data(
name TEXT NOT NULL,
date TEXT NOT NULL,
release_date TEXT,
release_price REAL,
presale_date TEXT,
presale_price REAL,
quantity INTEGER,
currency TEXT,
twitter_id TEXT,
discord_id TEXT,
website TEXT,
PRIMARY KEY(name, date)
);

CREATE TABLE twitter_scraped_data(
twitter_id TEXT NOT NULL,
date TEXT NOT NULL,
followers INTEGER,
following INTEGER,
activity INTEGER,
PRIMARY KEY(twitter_id, date)
);

CREATE TABLE discord_scraped_data(
discord_id TEXT NOT NULL,
date TEXT NOT NULL,
online INTEGER,
members INTEGER,
activity INTEGER,
PRIMARY KEY(discord_id, date)
);

CREATE TABLE opensea_scraped_data(
name TEXT NOT NULL,
date TEXT NOT NULL,
price REAL NOT NULL,
highest_last_sale REAL,
lowest_price REAL,
);

CREATE TABLE master_prediction_algorithms(

);
"""

import sqlite3
from sqlite3 import Error
from datetime import date
from dateutil.relativedelta import relativedelta

DB_FILE = 'cherry.db'

class DatabaseManager:
    """
    A handle to access and modify the cherry SQLite3 database
    """
    def __init__(self):
        """
        Creates a database connection to the cherry.db SQLite database
        """
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
        except Error as e:
            print(e)
        self.connection = conn
        self.cursor = self.connection.cursor()

    def begin_transaction(self):
        """
        Opens the database connection
        """
        self.cursor.execute('BEGIN TRANSACTION;')

    def end_transaction(self):
        """
        Commits and closes the databsae
        """
        self.cursor.execute('COMMIT;')
        self.connection.close()

    def enter_project(self, data):
        """
        Adds new data to a project in the master_project_list database
        If data already exists on the project, it will be overwritten
        
        Args:
            data (dict): information to enter
                required fields:
                    -name
                optional fields:
                    -release_date
                    -twitter_id
                    -discord_id
                    -quantity
                    -status
                    -rank
        """
        data = {k:v for k,v in data.items() if v}   # Remove empty values
        columns = str(list(data.keys())).replace("'", "")[1:-1]
        values = str(list(data.values()))[1:-1]

        sql_replace = """REPLACE INTO master_project_list ({})
                VALUES ({})
                ;""".format(columns, values)
        self.cursor.execute(sql_replace)
        "COUNT"

    def enter_rarity_record(self, data):
        """
        Adds new data into the rarity_scraped_data database
        If data already exists on the date/name, it will be overwritten

        Args:
            data (dict): information to enter
                required fields: 
                    -date
                    -name
                optional fields: 
                    -release_date
                    -release_price
                    -presale_date
                    -presale_price
                    -quantity
                    -currency
                    -twitter_id
                    -discord_id
                    -website
        """
        data = {k:v for k,v in data.items() if v}   # Remove empty values
        columns = str(list(data.keys())).replace("'", "")[1:-1]
        values = str(list(data.values()))[1:-1]

        sql_replace = """REPLACE INTO rarity_scraped_data ({})
                VALUES ({})
                ;""".format(columns, values)
        self.cursor.execute(sql_replace)

    def enter_twitter_record(self, data):
        """
        Adds new data into the twitter_scraped_data database
        If data already exists on the date/twitter_id, it will be overwritten

        Args:
            data (dict): information to enter
                required fields: 
                    -date
                    -twitter_id
                optional fields: 
                    -followers
                    -following
                    -activity
        """
        data = {k:v for k,v in data.items() if v}   # Remove empty values
        columns = str(list(data.keys())).replace("'", "")[1:-1]
        values = str(list(data.values()))[1:-1]

        sql_replace = """REPLACE INTO twitter_scraped_data ({})
                VALUES ({})
                ;""".format(columns, values)
        self.cursor.execute(sql_replace)

    def enter_discord_record(self, data):
        """
        Adds new data into the discord_scraped_data database
        If data already exists on the date/twitter_id, it will be overwritten

        Args:
            data (dict): information to enter
                required fields: 
                    -date
                    -discord_id
                optional fields: 
                    -online
                    -members
                    -activity
        """
        data = {k:v for k,v in data.items() if v}   # Remove empty values
        columns = str(list(data.keys())).replace("'", "")[1:-1]
        values = str(list(data.values()))[1:-1]

        sql_replace = """REPLACE INTO discord_scraped_data ({})
                VALUES ({})
                ;""".format(columns, values)
        self.cursor.execute(sql_replace)

    def enter_opensea_record(self, data):
        """
        Adds new data into the opensea_scraped_data database
        If data already exists on the date/name, it will be overwritten

        Args:
            data (dict): information to enter
                required fields: 
                    -date
                    -name
                optional fields: 
                    -online
                    -members
                    -activity
        """
        data = {k:v for k,v in data.items() if v}   # Remove empty values
        columns = str(list(data.keys())).replace("'", "")[1:-1]
        values = str(list(data.values()))[1:-1]

        sql_replace = """REPLACE INTO discord_scraped_data ({})
                VALUES ({})
                ;""".format(columns, values)
        self.cursor.execute(sql_replace)

    def get_twitter_ids_pre_release(self, date):
        """
        Finds the twitter_id for projects that have not been released yet
        
        Args:
            date (str): cutoff date (probably today)

        Returns:
            list (str): all twitter_ids that meet search criteria
        """
        sql_filter = """SELECT twitter_id from master_project_list
                WHERE release_date > date('{}')
                ;""".format(date)
        self.cursor.execute(sql_filter)
        ids = [x[0] for x in self.cursor.fetchall()]
        return ids

    def get_discord_ids_pre_release(self, date):
        """
        Finds the discord_id for projects that have not been released yet
        
        Args:
            date (str): cutoff date (probably today)

        Returns:
            list (str): all discord_ids that meet search criteria
        """
        sql_filter = """SELECT discord_id from master_project_list
                WHERE release_date > date('{}')
                ;""".format(date)
        self.cursor.execute(sql_filter)
        ids = [x[0] for x in self.cursor.fetchall()]
        return ids

    def get_projects_post_release(self, end_date):
        """
        Finds projects that have already been released
        
        Args:
            date (str): cutoff date (probably today)

        Returns:
            list (str): all project names that meet search criteria
        """
        MONTH_RANGE = 3
        start_date = date.today() - relativedelta(months =+ MONTH_RANGE)
        sql_filter = """SELECT name from master_project_list
                WHERE release_date > date('{}') AND release_date < date('{}')
                ;""".format(start_date, end_date)
        self.cursor.execute(sql_filter)
        names = [x[0] for x in self.cursor.fetchall()]
        return names

    def remove_twitter_ids(self, ids):
        """
        Removes a list of twitter_ids from the master_project_list
        This is intended to be used for failed/incorrect data

        Args:
            ids (list of str): twitter_ids to delete
        """
        values = str(ids)[1:-1]
        sql_update = """UPDATE master_project_list
                SET twitter_id = ''
                WHERE twitter_id in ({})
                ;""".format(values)
        self.cursor.execute(sql_update)

    def remove_discord_ids(self, ids):
        """
        Removes a list of discord_ids from the master_project_list
        This is intended to be used for failed/incorrect data

        Args:
            ids (list of str): discord_ids to delete
        """
        values = str(ids)[1:-1]
        sql_update = """UPDATE master_project_list
                SET discord_id = ''
                WHERE discord_id in ({})
                ;""".format(values)
        self.cursor.execute(sql_update)

    def lookup_quantity(self, project):
        """
        Looks up the quantity value for a given project

        Args:
            project (str): project name to filter by

        Returns:
            quantity (str): number of NFTs in the project
        """
        sql_lookup = """SELECT quantity FROM master_project_list WHERE name = '{}'
                ;""".format(project)

        self.cursor.execute(sql_lookup)
        quantity = self.cursor.fetchall()[0][0]

        return quantity
