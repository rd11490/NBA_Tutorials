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

```
     playerId           playerName  RAPM  RAPM_Rank  RAPM__Def  RAPM__Def_Rank  RAPM__Off  RAPM__Off_Rank  RAPM__intercept
0      101106         Andrew Bogut -0.10      280.0      -0.15           324.0       0.05           228.0           111.32
1      101107      Marvin Williams -0.07      269.0      -0.37           404.0       0.31           145.0           111.32
2      101108           Chris Paul  1.69       42.0       1.13            25.0       0.56            97.0           111.32
3      101109       Raymond Felton  0.03      234.0       0.74            72.0      -0.71           455.0           111.32
4      101112        Channing Frye -1.78      503.0      -1.21           514.0      -0.57           431.0           111.32
5      101123         Gerald Green  0.35      161.0      -0.87           486.0       1.22            36.0           111.32
6      101133          Ian Mahinmi -0.29      332.0       0.41           130.0      -0.70           453.0           111.32
7      101139             CJ Miles -0.60      397.0       0.09           200.0      -0.69           452.0           111.32
8      101141       Ersan Ilyasova  1.58       45.0       0.76            71.0       0.82            62.0           111.32
9      101150         Lou Williams  0.99       81.0      -0.65           457.0       1.64            18.0           111.32
10     101161         Amir Johnson -0.84      435.0      -0.51           432.0      -0.33           370.0           111.32
11     101162        Marcin Gortat -0.82      430.0      -0.26           371.0      -0.56           428.0           111.32
12     101181        Jose Calderon -2.10      516.0      -0.39           409.0      -1.71           519.0           111.32
13    1626143        Jahlil Okafor -0.90      444.0      -0.51           429.0      -0.40           383.0           111.32
14    1626144      Emmanuel Mudiay -1.60      497.0      -1.15           513.0      -0.44           400.0           111.32
15    1626145           Tyus Jones  0.37      158.0       0.22           164.0       0.16           177.0           111.32
16    1626147      Justin Anderson -0.58      393.0      -0.33           394.0      -0.24           343.0           111.32
17    1626149     Montrezl Harrell  0.26      177.0      -0.66           460.0       0.93            53.0           111.32
18    1626150      Andrew Harrison -0.12      284.0       0.03           234.0      -0.15           315.0           111.32
19    1626153         Delon Wright  0.16      199.0       0.07           209.0       0.08           208.0           111.32
20    1626154            RJ Hunter  0.44      147.0       0.22           161.0       0.22           159.0           111.32
21    1626155           Sam Dekker -0.50      372.0      -0.66           458.0       0.16           176.0           111.32
22    1626156      DAngelo Russell  0.08      215.0       0.58            93.0      -0.50           414.0           111.32
23    1626157   Karl-Anthony Towns  0.80       96.0      -0.17           334.0       0.97            47.0           111.32
24    1626158       Richaun Holmes -0.36      348.0      -0.19           344.0      -0.17           322.0           111.32
25    1626159      Justise Winslow  1.79       36.0       1.72             4.0       0.07           214.0           111.32
26    1626161  Willie Cauley-Stein  0.81       95.0       0.55           100.0       0.26           153.0           111.32
27    1626162      Kelly Oubre Jr. -1.03      459.0      -0.99           499.0      -0.04           279.0           111.32
28    1626163       Frank Kaminsky  0.52      131.0       0.12           189.0       0.40           124.0           111.32
29    1626164         Devin Booker -0.48      370.0      -1.37           518.0       0.89            57.0           111.32
..        ...                  ...   ...        ...        ...             ...        ...             ...              ...
499    203960       JaKarr Sampson -0.11      281.0      -0.07           279.0      -0.04           281.0           111.32
500    203961        Eric Moreland -0.14      294.0       0.08           204.0      -0.23           338.0           111.32
501    203967          Dario Saric -0.72      415.0      -0.76           472.0       0.04           234.0           111.32
502    203991         Clint Capela  1.29       60.0       0.72            74.0       0.57            96.0           111.32
503    203992    Bogdan Bogdanovic  0.26      179.0      -0.12           309.0       0.38           127.0           111.32
504    203994         Jusuf Nurkic  2.47       13.0       1.01            39.0       1.46            22.0           111.32
505    203998        Bruno Caboclo  0.83       93.0       0.29           155.0       0.54           103.0           111.32
506    203999         Nikola Jokic  1.59       44.0       0.55            98.0       1.04            43.0           111.32
507    204020        Tyler Johnson -1.40      489.0      -0.48           427.0      -0.92           489.0           111.32
508    204025          Tim Frazier -0.87      438.0      -0.79           478.0      -0.08           293.0           111.32
509    204038    Langston Galloway  0.44      148.0      -0.25           365.0       0.69            73.0           111.32
510    204060           Joe Ingles  2.42       14.0       1.67             5.0       0.75            67.0           111.32
511    204456       T.J. McConnell -0.93      450.0      -1.06           507.0       0.13           186.0           111.32
512      2199       Tyson Chandler -0.01      247.0       0.88            54.0      -0.89           485.0           111.32
513      2200            Pau Gasol -0.68      410.0      -0.27           375.0      -0.41           387.0           111.32
514      2225          Tony Parker -0.21      311.0       0.15           180.0      -0.36           378.0           111.32
515      2403                 Nene  1.00       78.0       0.54           102.0       0.46           116.0           111.32
516      2544         LeBron James  1.88       32.0       1.02            38.0       0.87            59.0           111.32
517      2546      Carmelo Anthony -1.02      456.0      -0.36           401.0      -0.66           444.0           111.32
518      2548          Dwyane Wade -0.86      436.0      -0.33           391.0      -0.53           422.0           111.32
519      2585        Zaza Pachulia -0.91      446.0       0.00           248.0      -0.91           488.0           111.32
520      2594          Kyle Korver  0.28      175.0       0.47           113.0      -0.19           324.0           111.32
521      2617        Udonis Haslem -0.32      339.0       0.13           186.0      -0.45           403.0           111.32
522      2730        Dwight Howard -0.65      407.0      -0.23           360.0      -0.42           393.0           111.32
523      2733     Shaun Livingston -0.09      277.0       0.12           188.0      -0.21           334.0           111.32
524      2734         Devin Harris -0.97      454.0      -0.60           452.0      -0.37           379.0           111.32
525      2736            Luol Deng  1.33       58.0       0.43           122.0       0.89            56.0           111.32
526      2738       Andre Iguodala  1.83       34.0       0.96            45.0       0.86            60.0           111.32
527      2747             JR Smith  0.26      178.0       0.55            97.0      -0.30           354.0           111.32
528      2772         Trevor Ariza -1.94      511.0      -1.27           516.0      -0.67           448.0           111.32
```
