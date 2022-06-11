from datetime import datetime
import os
import shutil

from DatabaseManager import DB_FILE
import data_collection
import prediction_algorithm


def prompt_human_input():
    """
    Runs a UI to prompt the user to review and rate a subset of projects
    Records collected data into database
    """
    pass

def backup_db():
    parts = DB_FILE.split('.')
    a = '.'.join(parts[:-1])
    b = parts[-1]
    now = datetime.now().strftime('%Y%m%d')
    backup_dir = f'./backup'

    if not os.path.isdir(backup_dir):
        os.mkdir(backup_dir)
    backup_file = f'{backup_dir}/{a}_{now}.{b}'
    shutil.copy(DB_FILE, backup_file)

def main():
    """
    This is the main data collection function that runs daily, ideally automatically
    Gathers a large snapshot of objective data,
    As well as subjective human-entered data for a few selected projects
    """
    backup_db()
    data_collection.daily_scrape()
    # prediction_algorithm.train()
    # prediction_algorithm.predict_future()
    # prompt_human_input()


if __name__ == '__main__':
    main()
