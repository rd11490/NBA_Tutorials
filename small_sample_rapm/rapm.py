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
possessions = pd.read_csv('data/adjusted_possessions_per_game_21_22.csv')

# # Read player name CSV
# player_names = pd.read_csv('data/player_names.csv')

# Filter out 0 possession possessions
possessions = possessions[possessions['possessions'] > 0]

# build the list o unique player ids
player_list = build_player_list(possessions)

# Calculate pts/100 possessions for each possession
possessions['PointsPerPossession'] = 100 * possessions['points'].values / possessions['possessions'].values
possessions['AdjustedPointsPerPossession'] = 100 * possessions['adjustedPoints'].values / possessions['possessions'].values



# extract the training data from our possession data frame
train_x, train_y, possessions_raw = convert_to_matricies(possessions, 'PointsPerPossession', player_list)
train_x_adjusted, train_y_adjusted, possessions_raw = convert_to_matricies(possessions, 'AdjustedPointsPerPossession', player_list)

# a list of lambdas for cross validation
lambdas_rapm = [.01, .05, .1]

# calculate the RAPM
results, intercept = calculate_rapm(train_x, train_y, possessions_raw, lambdas_rapm, 'RAPM', player_list)
results_adjusted, intercept_adjusted = calculate_rapm(train_x_adjusted, train_y_adjusted, possessions_raw, lambdas_rapm, 'Adjusted_RAPM', player_list)


# round to 2 decimal places for display
results = np.round(results, decimals=2)
results_adjusted = np.round(results_adjusted, decimals=2)


# sort the columns
results = results.reindex(sorted(results.columns), axis=1)
results_adjusted = results_adjusted.reindex(sorted(results_adjusted.columns), axis=1)


merged = results.merge(results_adjusted, on='playerId').sort_values(by='RAPM', ascending=False)

merged_results = merged[['playerId', 'RAPM', 'RAPM_Rank', 'Adjusted_RAPM', 'Adjusted_RAPM_Rank']].copy()

merged_results['RAPM_Difference'] = merged_results['RAPM'] - merged_results['Adjusted_RAPM']
merged_results['RAPM_Rank_Difference'] = merged_results['RAPM_Rank'] - merged_results['Adjusted_RAPM_Rank']

print('Top 20 players by RAPN')
print(merged_results.head(20))

merged_results['RAPM_Difference_abs'] = abs(merged_results['RAPM_Difference'])
merged_results['RAPM_Rank_Difference_abs'] = abs(merged_results['RAPM_Rank_Difference'])

print('\n\n')
print('Stats on absolute difference in RAPM and RAPM Rank')
print(merged_results[['RAPM_Difference_abs', 'RAPM_Rank_Difference_abs']].describe().round(3))

