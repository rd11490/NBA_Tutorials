import pandas as pd

# Display options for printing padas Dataframes
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)


# Change a missed 3 in the first quarter into a made 3 in the second quarter
def change_possessions(group):
    # take the team id of the first row
    team1 = group['offenseTeamId1'].values[0]
    # filter to only possessions where the chosen team is on offense
    team1_poss = group[group['offenseTeamId1'] == team1]

    # Find the index of the first 3 made by the chosen team in the first quarter
    made_ind = team1_poss[(team1_poss['threePtAttempts'] == 1) & (team1_poss['period'] == 1) & (team1_poss['threePtMade'] == 1)].head(1).index
    # Find the index of the first 3 missed by the chosen team in the second quarter
    missed_ind = team1_poss[(team1_poss['threePtAttempts'] == 1) & (team1_poss['period'] == 2) & (team1_poss['threePtMade'] == 0)].head(1).index

    # flip the adjusted points
    group.loc[made_ind, 'adjustedPoints'] = 0.0
    group.loc[missed_ind, 'adjustedPoints'] = 3.0

    return group


# Read the possession data for the 2021-22 season
data = pd.read_csv('data/luck_adjusted_one_way_possessions_2021-22.csv')

# Filter out 0 possession rows
data = data[data['possessions'] > 0]

# Create a new column for adjusted points
data['adjustedPoints'] = data['points']

# Group by gameId and apply our adjustement
data = data.groupby(by='gameId').apply(change_possessions).reset_index()

# Save the data
data.to_csv('data/adjusted_possessions_per_game_21_22.csv', index=False)









