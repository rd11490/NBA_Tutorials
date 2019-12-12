import pandas as pd

frame = pd.read_csv('poss.csv', index_col=0)[['offenseTeamId1',
       'offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id',
       'offensePlayer4Id', 'offensePlayer5Id', 'defenseTeamId2',
       'defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id',
       'defensePlayer4Id', 'defensePlayer5Id', 'points', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts',
       'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions',
       'seconds']]

frame.to_csv('possession_18_19.csv', index=False)