import data_collection
import prediction_algorithm

def prompt_human_input():
    """
    Runs a UI to prompt the user to review and rate a subset of projects
    Records collected data into database
    """
    pass

def main():
    """
    This is the main data collection function that runs daily, ideally automatically
    Gathers a large snapshot of objective data,
    As well as subjective human-entered data for a few selected projects
    """
    data_collection.daily_scrape()
    # prediction_algorithm.train()
    # prediction_algorithm.predict_future()
    # prompt_human_input()

if __name__ == "__main__":
    main()