import os
import pandas as pd

from constants import TWITTER_COLUMNS as t_cols
from constants import DISCORD_COLUMNS as d_cols

def main():
    input_file = str(input("\nEnter file to clean: "))
    clean = ''
    if os.path.exists(input_file):

        if '/discord_data/' in input_file:
            df = pd.read_csv(input_file, usecols=d_cols)
            clean = df.drop_duplicates(subset='discord', ignore_index=True)

        elif '/twitter_data/' in input_file:
            df = pd.read_csv(input_file, usecols=t_cols)
            clean = df.drop_duplicates(subset='twitter',  ignore_index=True)

    if len(clean) > 0:
        savepath = input_file.split(os.getcwd()+'/')[1]
        clean.to_csv(savepath)
        print('Cleaned!')


if __name__ == "__main__":
    main()