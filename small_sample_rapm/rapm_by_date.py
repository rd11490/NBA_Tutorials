# Import pandas, numpy and RidgeCV from sklearn
import datetime

import numpy as np
import pandas as pd

from small_sample_rapm.rapm_utils import build_player_list, convert_to_matricies, calculate_rapm


# Set display options for pandas for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)

# Read possessions CSV
possessions = pd.read_csv('data/luck_adjusted_one_way_possessions_2020-21.csv')

# # Read player name CSV
player_names = pd.read_csv('data/player_names.csv')

# Filter out 0 possession possessions
possessions = possessions[possessions['possessions'] > 0]

# build the list o unique player ids
player_list = build_player_list(possessions)

# Calculate pts/100 possessions for each possession
possessions['PointsPerPossession'] = 100 * possessions['points'].values / possessions['possessions'].values

def rapm_to_date(possessions, player_list, cutoff_date):
    possessions_to_date = possessions[possessions['gameDate'] <= cutoff_date]
    # extract the training data from our possession data frame
    train_x, train_y, possessions_raw = convert_to_matricies(possessions_to_date, 'PointsPerPossession', player_list)

    # a list of lambdas for cross validation
    lambdas_rapm = [.01, .05, .1]

    # calculate the RAPM
    results, intercept = calculate_rapm(train_x, train_y, possessions_raw, lambdas_rapm, 'RAPM', player_list)

    # round to 2 decimal places for display
    results = np.round(results, decimals=2)

    # sort the columns
    results = results.reindex(sorted(results.columns), axis=1)
    results['gameDate'] = cutoff_date
    return results

game_dates = sorted(list(possessions['gameDate'].unique()))
# Take every 3 days
game_dates = [d for i, d in enumerate(game_dates) if i % 3 == 0]


results = []
for date in game_dates:
    print(date)
    date_result = rapm_to_date(possessions, player_list, date)
    results.append(date_result)

frame = pd.concat(results)
frame.to_csv('results/rapm_by_date_20_21.csv', index=False)