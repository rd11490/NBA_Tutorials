# Import pandas, numpy and RidgeCV from sklearn
import datetime

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV

# Set display options for pandas for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Read possessions CSV
possessions = pd.read_csv('data/rapm_possessions.csv')

# Read player name CSV
player_names = pd.read_csv('data/player_names.csv')

# Filter out 0 possession possessions
possessions = possessions[possessions['possessions'] > 0]


# Build list of unique player ids in the possessions data
def build_player_list(posessions):
    players = list(
        set(list(posessions['offensePlayer1Id'].unique()) + list(posessions['offensePlayer2Id'].unique()) + list(
            posessions['offensePlayer3Id']) + \
            list(posessions['offensePlayer4Id'].unique()) + list(posessions['offensePlayer5Id'].unique()) + list(
            posessions['defensePlayer1Id'].unique()) + \
            list(posessions['defensePlayer2Id'].unique()) + list(posessions['defensePlayer3Id'].unique()) + list(
            posessions['defensePlayer4Id'].unique()) + \
            list(posessions['defensePlayer5Id'].unique())))
    players.sort()
    return players


# build the list o unique player ids
player_list = build_player_list(possessions)

# Calculate pts/100 possessions for each possession
start_df = datetime.datetime.now()
possessions['PointsPerPossession'] = 100 * possessions['points'].values / possessions['possessions'].values
end_df = datetime.datetime.now()
print('Time to run as Dataframe operation', end_df-start_df)

start_np = datetime.datetime.now()
possessions['PointsPerPossessionVec'] = 100 * possessions['points'].values / possessions['possessions'].values
end_np = datetime.datetime.now()
print('Time to run as Numpy operation', end_np-start_np)

print('Speedup: {0:.2f}x'.format((end_df-start_df).microseconds / (end_np-start_np).microseconds))


# Convert the row of player ids into a sparse row for the training matrix:
# [o_id1, o_id2, .... d_id4, d_id5] -> [0 1 1 0 0 0 1 1 1 -1 0 -1 -1 0 -1 -1 0]
def map_players(row_in, players):
    p1 = row_in[0]
    p2 = row_in[1]
    p3 = row_in[2]
    p4 = row_in[3]
    p5 = row_in[4]
    p6 = row_in[5]
    p7 = row_in[6]
    p8 = row_in[7]
    p9 = row_in[8]
    p10 = row_in[9]

    row_out = np.zeros([len(players) * 2])

    row_out[players.index(p1)] = 1
    row_out[players.index(p2)] = 1
    row_out[players.index(p3)] = 1
    row_out[players.index(p4)] = 1
    row_out[players.index(p5)] = 1

    row_out[players.index(p6) + len(players)] = -1
    row_out[players.index(p7) + len(players)] = -1
    row_out[players.index(p8) + len(players)] = -1
    row_out[players.index(p9) + len(players)] = -1
    row_out[players.index(p10) + len(players)] = -1

    return row_out


# Break the dataframe into x_train (nxm matrix), y_train (nx1 matrix of target values), and weights (not necessary because all rows will have 1 possession)
def convert_to_matricies(possessions, name, players):
    # extract only the columns we need

    # Convert the columns of player ids into a numpy matrix
    stints_x_base = possessions.as_matrix(columns=['offensePlayer1Id', 'offensePlayer2Id',
                                                   'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id',
                                                   'defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id',
                                                   'defensePlayer4Id', 'defensePlayer5Id'])

    # Apply our mapping function to the numpy matrix
    stint_X_rows = np.apply_along_axis(map_players, 1, stints_x_base, players)

    # Convert the column of target values into a numpy matrix
    stint_Y_rows = possessions.as_matrix([name])

    # extract the possessions as a pandas Series
    possessions = possessions['possessions']

    # return matricies and possessions series
    return stint_X_rows, stint_Y_rows, possessions


# extract the training data from our possession data frame
train_x, train_y, possessions_raw = convert_to_matricies(possessions, 'PointsPerPossession', player_list)


# Convert lambda value to alpha needed for ridge CV
def lambda_to_alpha(lambda_value, samples):
    return (lambda_value * samples) / 2.0


# Convert RidgeCV alpha back into a lambda value
def alpha_to_lambda(alpha_value, samples):
    return (alpha_value * 2.0) / samples


# Take in our nxm training matrix, our nx1 target matrix, a list of lambdas, the name we want to give to the value
# we are getting from the coefficients, and the list of players.
def calculate_rapm(train_x, train_y, possessions, lambdas, name, players):
    # convert our lambdas to alphas
    alphas = [lambda_to_alpha(l, train_x.shape[0]) for l in lambdas]

    # create a 5 fold CV ridgeCV model. Our target data is not centered at 0, so we want to fit to an intercept.
    clf = RidgeCV(alphas=alphas, cv=5, fit_intercept=True, normalize=False)

    # fit our training data
    model = clf.fit(train_x, train_y, sample_weight=possessions)

    # convert our list of players into a mx1 matrix
    player_arr = np.transpose(np.array(players).reshape(1, len(players)))

    # extract our coefficients into the offensive and defensive parts
    coef_offensive_array = np.transpose(model.coef_[:, 0:len(players)])
    coef_defensive_array = np.transpose(model.coef_[:, len(players):])

    # concatenate the offensive and defensive values with the playey ids into a mx3 matrix
    player_id_with_coef = np.concatenate([player_arr, coef_offensive_array, coef_defensive_array], axis=1)
    # build a dataframe from our matrix
    players_coef = pd.DataFrame(player_id_with_coef)
    intercept = model.intercept_

    # apply new column names
    players_coef.columns = ['playerId', '{0}__Off'.format(name), '{0}__Def'.format(name)]

    # Add the offesnive and defensive components together (we should really be weighing this to the number of offensive and defensive possession played as they are often not equal).
    players_coef[name] = players_coef['{0}__Off'.format(name)] + players_coef['{0}__Def'.format(name)]

    # rank the values
    players_coef['{0}_Rank'.format(name)] = players_coef[name].rank(ascending=False)
    players_coef['{0}__Off_Rank'.format(name)] = players_coef['{0}__Off'.format(name)].rank(ascending=False)
    players_coef['{0}__Def_Rank'.format(name)] = players_coef['{0}__Def'.format(name)].rank(ascending=False)

    # add the intercept for reference
    players_coef['{0}__intercept'.format(name)] = intercept[0]

    return players_coef, intercept


# a list of lambdas for cross validation
lambdas_rapm = [.01, .05, .1]

# calculate the RAPM
results, intercept = calculate_rapm(train_x, train_y, possessions_raw, lambdas_rapm, 'RAPM', player_list)

# round to 2 decimal places for display
results = np.round(results, decimals=2)

# sort the columns
results = results.reindex_axis(sorted(results.columns), axis=1)

# join back with player names
results = player_names.merge(results, how='inner', on='playerId')

# save as CSV
results.to_csv('data/rapm.csv')

# print first 30 players
print(results)
