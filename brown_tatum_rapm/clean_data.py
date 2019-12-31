import pandas as pd

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

data = pd.read_csv('luck_adjusted_one_way_possessions_2019-20.csv', index_col=0)

print(data.columns)
print(data.head(10))

columns_to_care_about = ['gameId', 'offenseTeamId1', 'offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id', 'defenseTeamId2', 'defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id', 'defensePlayer4Id', 'defensePlayer5Id', 'points', 'expectedPoints', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']

clean_data = data[columns_to_care_about]

clean_data.to_csv('possessions_19_20.csv', index=False)