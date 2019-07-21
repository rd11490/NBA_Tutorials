## Calculating RAPM

If you see any issues or think there is a better way to do something,
don't hesitate to open a PR, submit an issue, or reach out to me directly

### Creating the input data:
Coming Soon [Parsing Play by Play Data](../play_by_play_parser/)

#### Required Libraries:
```
pandas      0.24.1
numpy       1.15.4
sklearn     0.20.2
```

#### Calculating RAPM

We are starting this tutorial under the assumption that we have already
parsed possessions from play by play data.
The data has been provided for you in the data folder:
 [possession data](data/rapm_possessions.csv)

The possession data contains 12 columns, 5 containing player Ids for the
5 players on offense, 5 containing player Ids
for the 5 players on defense, 1 for points scored in the possession and
1 for the number of possessions (should always be 1 or 0).


```
   Unnamed: 0  offensePlayer1Id  offensePlayer2Id  offensePlayer3Id  offensePlayer4Id  offensePlayer5Id  defensePlayer1Id  defensePlayer2Id  defensePlayer3Id  defensePlayer4Id  defensePlayer5Id  points  possessions
0           0            201142            201939            202691           1626172           1627745            202331            202335            203471            203500           1628390     0.0            1
1           1            202331            202335            203471            203500           1628390            201142            201939            202691           1626172           1627745     0.0            0
2           2            101141            202339            203089            203114           1628978            201587            202689            203077           1626195           1628370     3.0            1
3           3            201587            202689            203077           1626195           1628370            101141            202339            203089            203114           1628978     0.0            0
4           4            203915           1626156           1626203           1627747           1628386            201933            202704            203083            203922            204038     0.0            0
```


You are also provided with a csv file containing all of the player ids
and the corresponding player name. We will use this
to convert from player ids to names after we have calculated RAPM.


The first thing we need to do in order to calculate RAPM is to build our
training set. It should come out to
be a nxm sparse matrix where n is the number rows in the training set
and m is the two times the number of unique player ids in the training
set (each player is split into their offensive and defensive coefficient),
and a nx1 matrix where each value is the points per 100 possessions in
that possession (0, 100, 200, 300). The nxm matrix will be a sparse matrix
where each row represents a single possession, each player on offense in
the possession is assigned +1, each defender is assigned -1 and everyone
else is assigned a 0.

```
[0 1 0 1 1 1 1 0 -1 0 -1 0 0 -1 -1 -1] [300]

```


We will then feed this training set to a cross validated Ridge Regression model and
extract our coefficients in order to obtain RAPM.

#### The Code:

As always we start with importing the necessary libraries
```
import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV
```

Set display options for pandas for easier printing
```
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
```

Read the possessions and player name data
```
possessions = pd.read_csv('data/rapm_possessions.csv')
player_names = pd.read_csv('data/player_names.csv')
```

Filter out 0 possession possessions
```
possessions = possessions[possessions['possessions'] > 0]
```

The first function we are going to write is a function to pull out all
of the unique player ides from the possession data.
This function is pretty straight forward, it takes all of the unique
player ids from each of the 10 player id columns, concats them together,
converts it to a set in order to deduplicate, then converts it to a list
and sorts based on player Id.

```
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
```

Apply the above function to our possession data
```
player_list = build_player_list(possessions)
```

Calculate points per 100 possessions for each possession
```
possessions['PointsPerPossession'] = 100 * possessions['points'] / possessions['possessions']
```

Convert the row of player ids into a sparse row for the training matrix:  
[o_id1, o_id2, .... d_id4, d_id5] -> [0 1 1 0 0 0 1 1 1 -1 0 -1 -1 0 -1 -1 0]
In this function we are maintaining order by looking up the position in the training row
based on the position in the sorted list of players we generated above. The offensive players sit at
the same index they do in list of players. The defensive players sit at the index + the total number of players.  
i.e. if there were only 3 players in the set it would be: [o_p1, o_p2, o_p3, d_p1, d_p2, d_p3]
```
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

    rowOut = np.zeros([len(players) * 2])

    rowOut[players.index(p1)] = 1
    rowOut[players.index(p2)] = 1
    rowOut[players.index(p3)] = 1
    rowOut[players.index(p4)] = 1
    rowOut[players.index(p5)] = 1

    rowOut[players.index(p6) + len(players)] = -1
    rowOut[players.index(p7) + len(players)] = -1
    rowOut[players.index(p8) + len(players)] = -1
    rowOut[players.index(p9) + len(players)] = -1
    rowOut[players.index(p10) + len(players)] = -1

    return rowOut
```

We also need a function to break the dataframe out into the training matrices.
If we were working with stints instead of possessions we would need the possession data
to properly weigh our training data

```
# Break the dataframe into x_train (nxm matrix), y_train (nx1 matrix of target values), and weights (not necessary because all rows will have 1 possession)
def extract_training_data(possessions, name, players):
    # extract only the columns we need
    possessions_for_reg = possessions[['offensePlayer1Id', 'offensePlayer2Id',
                                            'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id',
                                            'defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id',
                                            'defensePlayer4Id', 'defensePlayer5Id', name]]

    # Convert the columns of player ids into a numpy matrix
    stints_x_base = possessions_for_reg.as_matrix(columns=['offensePlayer1Id', 'offensePlayer2Id',
                                                      'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id',
                                                      'defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id',
                                                      'defensePlayer4Id', 'defensePlayer5Id'])
    # Apply our mapping function to the numpy matrix
    stint_X_rows = np.apply_along_axis(map_players, 1, stints_x_base, players)

    # Convert the column of target values into a numpy matrix
    stint_Y_rows = possessions_for_reg.as_matrix([name])

    # extract the possessions as a pandas Series
    possessions = possessions['possessions']

    # return matricies and possessions series
    return stint_X_rows, stint_Y_rows, possessions
```

apply our extraction method from above to our input data:
```
train_x, train_y, possessions_raw = extract_training_data(possessions, 'PointsPerPossession', player_list)
```

We will need a way to convert your standard lambda parameter into the alpha parameter needed for RidgeCV
[Difference between sklearn and glmnet ridge](https://stats.stackexchange.com/questions/160096/what-are-the-differences-between-ridge-regression-using-rs-glmnet-and-pythons)
```
# Convert lambda value to alpha needed for ridge CV
def lambda_to_alpha(lambda_value, samples):
    return (lambda_value * samples) / 2.0

# Convert RidgeCV alpha back into a lambda value
def alpha_to_lambda(alpha_value, samples):
    return (alpha_value * 2.0) / samples
```

Finally we need a method to take our training data and fit our model to it:
```
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
```

generate a list of lambdas for cross validation
```
lambdas_rapm = [.01, .05, .1]
```

calculate RAPM
```
results, intercept = calculate_rapm(train_x, train_y, possessions_raw, lambdas_rapm, 'RAPM', player_list)
```
round to 2 decimal places for display
```
results = np.round(results, decimals=2)
```

sort the columns
```
results = results.reindex_axis(sorted(results.columns), axis=1)
```

join results back with player names
```
results = player_names.merge(results, how='inner', on='playerId')
```

save as CSV and print
```
results.to_csv('data/rapm.csv')
print(results)
```
