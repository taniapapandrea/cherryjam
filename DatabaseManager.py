"""
database .schemas:

CREATE TABLE master_project_list(
name TEXT PRIMARY KEY,
release_date TEXT,
twitter_id TEXT,
discord_id TEXT,
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

);

CREATE TABLE prediction_algorithms(

);
"""

import sqlite3
from sqlite3 import Error

DB_FILE = 'cherry.db'

class DatabaseManager:
    """
    A handle to access and modify the cherry SQLite3 database
    """
    def __init__(self):
        self.connection = None
        self.cursor = None

    def create_connection(self):
        """
        Creates a database connection to the cherry.db SQLite database
        """
        conn = None
        try:
            conn = sqlite3.connect(DB_FILE)
        except Error as e:
            print(e)
        self.connection = conn

    def begin_transaction(self):
        """
        Opens the database connection
        """
        self.create_connection()
        self.cursor = self.connection.cursor()
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

    def get_projects_post_release(self, date):
        """
        Finds projects that have already been released
        
        Args:
            date (str): cutoff date (probably today)

        Returns:
            list (str): all project names that meet search criteria
        """
        sql_filter = """SELECT name from master_project_list
                WHERE release_date < date('{}')
                ;""".format(date)
        self.cursor.execute(sql_filter)
        names = [x[0] for x in self.cursor.fetchall()]
        return names