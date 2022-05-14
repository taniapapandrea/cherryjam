import os
import datetime
import re
import sys
import math
import shutil
from numpy import nan

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates

from constants import TWITTER_COLUMNS as t_cols
from constants import DISCORD_COLUMNS as d_cols
from constants import COMPILED_COLUMNS as c_cols


def has_values(d):
    """
    Checks if a dictionary has any values besides null or empty strings

    Args:
        d(dict): dictionary to verify
    """
    valid = False
    for v in d.values():
        if isinstance(v, str):
            if len(v)>0:
                valid = True
        elif isinstance(v, float):
            if not math.isnan(v):
                valid = True
    return valid

def compile_data(start_date, end_date, save_dir):
    """
    For each date between start_date and end_date, gather a snapshot of data for each NFT
    Create a compiled csv for each NFT.

    Args:
        start_date(datetime object): first date to include
        end_date(datetime object): last date to include
        save_dir(str): where to save the csv files (there will be several hundred)

    """
    ### Process input dates
    start_str = start_date.strftime("%m-%d-%y")
    end_str = end_date.strftime("%m-%d-%y")
    print('\nCompiling data between {} and {}'.format(start_str, end_str))
    if start_date > end_date:
        raise ValueError('Start date {} is after end date {}'.format(start_date, end_date))

    ### Compile data into a dictionary of lists of dictionaries
    nft_data = {}
    date = start_date

    # For each date
    while (date <= end_date):

        # Check for rarity data
        rarity_csv = '{}/rarity_data/{}_rarity.csv'.format(os.getcwd(), date.strftime("%Y-%m-%d"))
        if os.path.exists(rarity_csv):
            df = pd.read_csv(rarity_csv, usecols=['presale_price', 'presale_date', 'starting_price', 'release_date', 'name', 'twitter', 'discord', 'website'])
            rarity_data = df.to_dict('records')

            # Check for twitter data
            t_df = pd.DataFrame(columns = t_cols)
            t_csv = '{}/twitter_data/{}_twitter.csv'.format(os.getcwd(), date.strftime("%Y-%m-%d"))
            if os.path.exists(t_csv):
                t_df = pd.read_csv(t_csv, usecols = t_cols)

            # Check for discord data
            d_df = pd.DataFrame(columns = d_cols)
            d_csv = '{}/discord_data/{}_discord.csv'.format(os.getcwd(), date.strftime("%Y-%m-%d"))
            if os.path.exists(d_csv):
                d_df = pd.read_csv(d_csv, usecols = d_cols)

            for record in rarity_data:
                # Start data snapshot
                nft_name = record['name']
                t_key = record['twitter']
                d_key = record['discord']
                data_snapshot = {}

                # Copy data from rarity
                data_snapshot['presale_price'] = record['presale_price']
                data_snapshot['presale_date'] = record['presale_date']
                data_snapshot['starting_price'] = record['starting_price']
                data_snapshot['release_date'] = record['release_date']

                # Read data from twitter
                t_df_row = t_df.loc[t_df.twitter == t_key]
                rows = len(t_df_row.index)
                if rows == 1:
                    data_snapshot['twitter_total'] = t_df_row.iloc[0]['followers']
                elif rows == 0:
                    data_snapshot['twitter_total'] = nan
                elif rows > 1:
                    raise ValueError('More than one row of data for {} in {}'.format(t_key, t_csv))

                # Read data from discord
                d_df_row = d_df.loc[d_df.discord == d_key]
                rows = len(d_df_row.index)
                if rows == 1:
                    r = d_df_row.iloc[0]
                    data_snapshot['discord_total'] = r['total_members']
                    data_snapshot['discord_online'] = r['online_members']
                elif rows == 0:
                    data_snapshot['discord_total'] = nan
                    data_snapshot['discord_online'] = nan
                elif rows > 1:
                    raise ValueError('More than one row of data for {} in {}'.format(d_key, d_csv))

                # Add dictionary to list
                if (has_values(data_snapshot)):
                    data_snapshot['date'] = str(date)
                    if nft_name in nft_data:
                        nft_data[nft_name].append(data_snapshot)
                    else:
                        nft_data[nft_name] = [data_snapshot]

        date += datetime.timedelta(days=1)

    ### Add data for each NFT to a separate csv
    for nft_name in nft_data:
        data = nft_data[nft_name]
        clean_name = re.sub(r'\W+', '', nft_name)
        datafile = '{}/{}_compiled.csv'.format(save_dir, clean_name)
        df = pd.DataFrame(data)
        df.to_csv(datafile)


def create_graph():
    """
    Creates an empty matplotlib plot and sets proper formatting

    Returns:
        ax: matplotlib.axes.Axes object
    """
    # Create the graph
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Format the graph
    ax.set(xlabel='Date', ylabel='Twitter Total', title='Twitter Trends')
    ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
    # Mark by week (for day, use DayLocator and for week use WeekdayLocator)
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    # Rotate the dates
    fig.autofmt_xdate()

    return ax


def main():
    """
    Runs through every compiled file
    If there is enough data, display in a plot
    """
    
    ### *
    today = datetime.date.today()
    for i in range(9):
        print('\n<<*>>')
    print('\nCherry Report {}'.format(today.strftime("%m-%d-%Y")))

    # Get date range
    start_year = 2022
    start_month = int(input("\nStart month (1-12):  "))
    start_day = int(input("\nStart day (1-31):  "))
    start_date = datetime.datetime(start_year, start_month, start_day)
    start_date_str = start_date.strftime("%m-%d")

    end_year = 2022
    end_month = int(input("\nEnd month (1-12):  "))
    end_day = int(input("\nEnd day (1-31):  "))
    end_date = datetime.datetime(end_year, end_month, end_day)
    end_date_str = end_date.strftime("%m-%d")

    # Determine save location
    save_dir = "reports/{}_{}/compiled/".format(start_date_str, end_date_str)
    if os.path.exists(save_dir):
        if len(os.listdir(save_dir))>0:
            choice = str(input("\nData already exists in {}. Would you like to remove it and overwrite? (Y/N)".format(save_dir)))
            if choice.lower() == 'y':
                shutil.rmtree(save_dir)
                os.makedirs(save_dir)
            elif choice.lower() == "n": 
                sys.exit()
    else:
        os.makedirs(save_dir)

    # Get compile files
    full_save_dir = "{}/{}".format(os.getcwd(), save_dir)
    compile_data(start_date, end_date, full_save_dir)
    compiled_files = os.listdir(full_save_dir)
    compiled_files.sort()

    # Graph files that have useful information
    for file in compiled_files:
        filepath = '{}/{}'.format(full_save_dir, file)
        df = pd.read_csv(filepath, parse_dates=['date'], index_col=['date'])

        has_discord_data = (df.count()['discord_total'] > 2)
        has_twitter_data = (df.count()['twitter_total'] > 2)

        if has_twitter_data:
            print('has twitter data')
            ax = create_graph()
            ax.plot(df.index.values, df['twitter_total'], color='purple')
            plt.show()

        if has_discord_data:
            print('has discord data')
            ax = create_graph()
            ax.plot(df.index.values, df['discord_total'], color='green')
            ax.plot(df.index.values, df['discord_online'], color='blue')
            plt.show()



if __name__ == "__main__":
    main()