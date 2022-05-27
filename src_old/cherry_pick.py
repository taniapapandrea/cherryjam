import os
import datetime

import pandas as pd

from RarityScraper import RarityScraper
from TwitterBatchScraper import TwitterBatchScraper
from DiscordBatchScraper import DiscordBatchScraper


def main():
    
    ### *
    date = datetime.date.today()
    for i in range(9):
        print('\n<<*>>')
    print('\nCherry Pick {}'.format(date.strftime("%m-%d-%Y")))

    ### GET RARITY DATA

    ### allow custom rarity data input
    # input_file = str(input("\nEnter rarity data file, or press enter: "))
    # if '/rarity_data/' in input_file:
    #     rarity_csv = input_file
    # else:

    rarity_csv = '{}/rarity_data/{}_rarity.csv'.format(os.getcwd(), date)
    print('\n======>>> Rarity data saving at:\n{}'.format(rarity_csv))
    rscraper = RarityScraper()
    rscraper.scrape_upcoming(rarity_csv)

    ### *
    for i in range(3):
        print('\n*')

    ### GET TWITTER DATA
    df = pd.read_csv(rarity_csv, usecols=['twitter'])
    twitter_users = [x for x in df['twitter'].tolist() if x is not None]
    twitter_csv = '{}/twitter_data/{}_twitter.csv'.format(os.getcwd(), date)
    print('\n======>>> Twitter data saving at:\n{}'.format(twitter_csv))
    tbatchscraper = TwitterBatchScraper(twitter_users)
    tbatchscraper.run(twitter_csv)

    ### *
    for i in range(3):
        print('\n*')

    ### GET DISCORD DATA
    df = pd.read_csv(rarity_csv, usecols=['discord'])
    discord_users = [x for x in df['discord'].tolist() if x is not None]
    discord_csv = '{}/discord_data/{}_discord.csv'.format(os.getcwd(), date)
    print('\n======>>> Discord data saving at:\n{}'.format(discord_csv))
    dbatchscraper = DiscordBatchScraper(discord_users)
    dbatchscraper.run(discord_csv)

    ### *
    for i in range(1):
        print('\n*')


if __name__ == "__main__":
    main()


# LOADING BAR
# for i in range(28):
#     sys.stdout.write("\r{0}>>>".format("="*i))
#     sys.stdout.flush()
#     time.sleep(0.5)
# sys.stdout.write("\r{0}".format("="*31))
# sys.stdout.flush()