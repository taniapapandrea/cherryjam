import datetime

import DatabaseManager

# All the pieces of data that might be used in calculations
TWITTER_FIELDS = ['id', 'date', 'twitter_life_score', 'followers', 'following']
DISCORD_FIELDS = ['id', 'date', 'discord_life_score', 'online', 'members']
OPENSEA_FIELDS = ['name', 'date', 'price', 'highest_sale', 'lowest_sale']
PROJECT_FIELDS = ['name', 'release_date', 'twitter_id', 'discord_id', 'status', 'score']


def train():
    """
    Uses post-released project data to test and improve the prediction algorithm

    Report all tests in logs
    """
    # Gather all data ??
    functions = DatabaseManager.get("ALGORITHMS", "function", "status=active")
    today = datetime.date.today()
    t_data = DatabaseManager.get("TWITTER", TWITTER_FIELDS, "release_date<today")
    d_data = DatabaseManager.get("DISCORD", DISCORD_FIELDS, "release_date<today")
    o_data = DatabaseManager.get("OPENSEA", OPENSEA_FIELDS, "release_date<today")
    p_data = DatabaseManager.get("PROJECT", PROJECT_FIELDS, "release_date<today")

    #Test each function to see how well it correlates with price
    for function in functions:
        total_accuracy = 0
        for project in projects:
            #plot date x price
            #plot date x cherry_score
            #find correlation between the two
            #rate algorithm based on correlation
            total_accuracy += score
        accuracy = total_accuracy / (len(projects))
        DatabaseManager.enter("ALGORITHMS", [function,accuracy])

def predict_future():
    """
    Uses the top prediction algorithm to identify pre-released projects with potential high price

    Report all tests in logs
    """
    # Get algorithm with top accuracy
    # Gather all data as above except release_date>today
    for project in projects:
        #plot date x cherry_score
        #score = slope of graph
        DatabaseManager.enter("PROJECTS", ["project", "score"])
    # Return the top scored projects

# accuracy of an algorithm changes every day
# score of a project changes every day
# how to record this? keep every date, overall average, or overwrite?
# probably just overwrite as these scores are fluid and can always be reproduced