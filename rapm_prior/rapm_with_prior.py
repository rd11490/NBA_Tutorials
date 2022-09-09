# Import pandas, numpy and RidgeCV from sklearn
import datetime

import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV

# Set display options for pandas for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Convert lambda value to alpha needed for ridge CV
def lambda_to_alpha(lambda_value, samples):
    return (lambda_value * samples) / 2.0


# Convert RidgeCV alpha back into a lambda value
def alpha_to_lambda(alpha_value, samples):
    return (alpha_value * 2.0) / samples

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

    row_out = np.zeros([len(players)])

    row_out[players.index(p1)] = 1
    row_out[players.index(p2)] = 1
    row_out[players.index(p3)] = 1
    row_out[players.index(p4)] = 1
    row_out[players.index(p5)] = 1

    row_out[players.index(p6)] = -1
    row_out[players.index(p7)] = -1
    row_out[players.index(p8)] = -1
    row_out[players.index(p9)] = -1
    row_out[players.index(p10)] = -1

    return row_out


# Break the dataframe into x_train (nxm matrix), y_train (nx1 matrix of target values), and weights (not necessary because all rows will have 1 possession)
def convert_to_matricies(possessions_df, name, players, prior):
    # extract only the columns we need

    # Convert the columns of player ids into a numpy matrix
    stints_x_base = possessions_df[['offensePlayer1Id', 'offensePlayer2Id',
                                                      'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id',
                                                      'defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id',
                                                      'defensePlayer4Id', 'defensePlayer5Id']].to_numpy()

    # Apply our mapping function to the numpy matrix
    stint_X_rows = np.apply_along_axis(map_players, 1, stints_x_base, players)

    # Convert the column of target values into a numpy matrix
    stint_Y_rows = possessions_df[[name]].to_numpy()

    # Subtract out the prior
    # print('Y')
    # print(stint_Y_rows)
    # print(stint_Y_rows.shape)
    #
    # print('X')
    # print(stint_X_rows)
    # print(stint_X_rows.shape)

    prior = np.array(prior).reshape(len(prior), 1)

    # print('PRIOR')
    # print(prior)
    # print(prior.shape)

    Y_prior = stint_X_rows.dot(prior)
    # print('Y_prior')
    # print(Y_prior)
    # print(Y_prior.shape)
    #
    # print('stint_Y_rows')
    # print(stint_Y_rows)
    # print(stint_Y_rows.shape)

    stint_Y_row_adj = stint_Y_rows - Y_prior
    # print('stint_Y_row_adj')
    # print(stint_Y_row_adj)
    # print(stint_Y_row_adj.shape)

    # print('ADJ Y')
    # print(stint_Y_row_adj)
    # print(stint_Y_row_adj.shape)

    # extract the possessions as a pandas Series
    possessions_vector = possessions_df['possessions']

    # return matricies and possessions series
    return stint_X_rows, stint_Y_row_adj, possessions_vector

# Build list of unique player ids in the possessions data
def build_player_list(posessions_df):
    players = list(
        set(list(posessions_df['offensePlayer1Id'].unique()) + list(posessions_df['offensePlayer2Id'].unique()) + list(
            posessions_df['offensePlayer3Id']) + \
            list(posessions_df['offensePlayer4Id'].unique()) + list(posessions_df['offensePlayer5Id'].unique()) + list(
            posessions_df['defensePlayer1Id'].unique()) + \
            list(posessions_df['defensePlayer2Id'].unique()) + list(posessions_df['defensePlayer3Id'].unique()) + list(
            posessions_df['defensePlayer4Id'].unique()) + \
            list(posessions_df['defensePlayer5Id'].unique())))
    players.sort()
    return players

# Take in our nxm training matrix, our nx1 target matrix, a list of lambdas, the name we want to give to the value
# we are getting from the coefficients, and the list of players.
def calculate_rapm(train_x, train_y, possessions, lambdas, name, players, prior):
    # convert our lambdas to alphas
    alphas = [lambda_to_alpha(l, train_x.shape[0]) for l in lambdas]

    # create a 5 fold CV ridgeCV model. Our target data is not centered at 0, so we want to fit to an intercept.
    clf = RidgeCV(alphas=alphas, cv=5, fit_intercept=True, normalize=False)

    # fit our training data
    model = clf.fit(train_x, train_y, sample_weight=possessions)

    # convert our list of players into a mx1 matrix
    player_arr = np.transpose(np.array(players).reshape(1, len(players)))

    # extract our coefficients into the offensive and defensive parts
    coef_array = np.transpose(model.coef_)

    prior_arr = np.array(prior).reshape(len(prior), 1)

    coef_array_plus_prior = coef_array + prior_arr

    # concatenate the offensive and defensive values with the playey ids into a mx3 matrix
    player_id_with_coef = np.concatenate([player_arr, coef_array, prior_arr, coef_array_plus_prior], axis=1)
    # build a dataframe from our matrix
    players_coef = pd.DataFrame(player_id_with_coef)
    intercept = model.intercept_

    print("Model Lambda: {0} -> {1}".format(model.alpha_, alpha_to_lambda(model.alpha_, train_x.shape[0])))

    # apply new column names
    players_coef.columns = ['PLAYER_ID', '{}_PRE_PRIOR'.format(name), 'PRIOR', name]

    # rank the values
    players_coef['{0}_Rank'.format(name)] = players_coef[name].rank(ascending=False)

    return players_coef, intercept




possessions = pd.read_csv('data/possessions_19_20.csv')

# Read player name CSV
player_names = pd.read_csv('data/player_names.csv')

# Read Prior
prior = pd.read_csv('data/prior.csv')

# Filter out 0 possession possessions
possessions = possessions[possessions['possessions'] > 0]



# build the list o unique player ids
player_list = build_player_list(possessions)

prior_frame = pd.DataFrame()
prior_frame['PLAYER_ID'] = player_list
prior_frame=prior_frame.merge(prior, on='PLAYER_ID', how='left')
print(len(player_list))
print(prior.shape)
print(prior_frame.shape)
prior_frame=prior_frame.fillna(0.0)
prior_frame['Raw'] = 0.0
prior = prior_frame['Stable SPR']
prior_raw = prior_frame['Raw']

prior_frame.to_csv('data/stable_prior.csv')
# Calculate pts/100 possessions for each possession
possessions['PointsPerPossession'] = 100 * (possessions['points'].values / possessions['possessions'].values)

# extract the training data from our possession data frame
train_x, train_y, possessions_raw = convert_to_matricies(possessions, 'PointsPerPossession', player_list, prior)

# a list of lambdas for cross validation
lambdas_rapm = [.01, .05]

# calculate the RAPM
results, intercept = calculate_rapm(train_x, train_y, possessions_raw, lambdas_rapm, 'Stable RAPM', player_list, prior)

# extract the training data from our possession data frame
train_x, train_y, possessions_raw = convert_to_matricies(possessions, 'PointsPerPossession', player_list, prior)


# a list of lambdas for cross validation
lambdas_rapm = [.01, .05]

# calculate the RAPM

#
train_x_raw, train_y_raw, possessions_raw = convert_to_matricies(possessions, 'PointsPerPossession', player_list, prior_raw)
results_raw, intercept = calculate_rapm(train_x_raw, train_y_raw, possessions_raw, lambdas_rapm, 'RAPM', player_list, prior_raw)
#
results = results.merge(results_raw, on='PLAYER_ID')

# sort the columns
results = results.reindex(sorted(results.columns), axis=1)

# join back with player names
results = results.merge(player_names, how='left', on='PLAYER_ID')

# save as CSV
results=results.merge(prior_frame[['PLAYER_ID', 'Stable SPR']], on='PLAYER_ID')
print(results)

results.to_csv('data/rapm_with_prior.csv')


