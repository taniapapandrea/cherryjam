import data_collection

def train_prediction_algorithm():
    """
    Uses post-released project data to test and improve the prediction algorithm
    """
    pass

def predict_future():
    """
    Uses the current prediction algorithm to identify high profile pre-released projects
    """
    pass

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
    train_prediction_algorithm()
    predict_future()
    prompt_human_input()

if __name__ == "__main__":
    main()