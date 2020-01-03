import pandas as pd

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

celtics_team_id = 1610612738
jaylen_brown = 1627759
jayson_tatum = 1628369


for i in range(1, 20):
    data = pd.read_csv('data/possessions_19_20.csv')

    celtics_o = data[data['offenseTeamId1'] == celtics_team_id]

    every_possession_with_brown_not_tatum_o = celtics_o[
        ((celtics_o['offensePlayer1Id'] == jaylen_brown) |
         (celtics_o['offensePlayer2Id'] == jaylen_brown) |
         (celtics_o['offensePlayer3Id'] == jaylen_brown) |
         (celtics_o['offensePlayer4Id'] == jaylen_brown) |
         (celtics_o['offensePlayer5Id'] == jaylen_brown)) &
        ((celtics_o['offensePlayer1Id'] != jayson_tatum) &
         (celtics_o['offensePlayer2Id'] != jayson_tatum) &
         (celtics_o['offensePlayer3Id'] != jayson_tatum) &
         (celtics_o['offensePlayer4Id'] != jayson_tatum) &
         (celtics_o['offensePlayer5Id'] != jayson_tatum))
        ]

    every_possession_with_tatum_not_brown_o = celtics_o[
        ((celtics_o['offensePlayer1Id'] == jayson_tatum) |
         (celtics_o['offensePlayer2Id'] == jayson_tatum) |
         (celtics_o['offensePlayer3Id'] == jayson_tatum) |
         (celtics_o['offensePlayer4Id'] == jayson_tatum) |
         (celtics_o['offensePlayer5Id'] == jayson_tatum)) &
        ((celtics_o['offensePlayer1Id'] != jaylen_brown) &
         (celtics_o['offensePlayer2Id'] != jaylen_brown) &
         (celtics_o['offensePlayer3Id'] != jaylen_brown) &
         (celtics_o['offensePlayer4Id'] != jaylen_brown) &
         (celtics_o['offensePlayer5Id'] != jaylen_brown))
        ]

    brown_not_tatum_o = every_possession_with_brown_not_tatum_o[(every_possession_with_brown_not_tatum_o['points'] == 0) & (every_possession_with_brown_not_tatum_o['threePtAttempts'] == 1)].sample(i)
    data.loc[brown_not_tatum_o.index, 'points'] = 3

    tatum_not_brown_o = every_possession_with_tatum_not_brown_o[(every_possession_with_tatum_not_brown_o['points'] == 3) & (every_possession_with_tatum_not_brown_o['threePtAttempts'] == 1)].sample(i)
    data.loc[tatum_not_brown_o.index, 'points'] = 0

    ###########
    # DEFENSE #
    ###########

    celtics_d = data[data['defenseTeamId2'] == celtics_team_id]

    every_possession_with_brown_not_tatum_d = celtics_d[
        ((celtics_d['defensePlayer1Id'] == jaylen_brown) |
         (celtics_d['defensePlayer2Id'] == jaylen_brown) |
         (celtics_d['defensePlayer3Id'] == jaylen_brown) |
         (celtics_d['defensePlayer4Id'] == jaylen_brown) |
         (celtics_d['defensePlayer5Id'] == jaylen_brown)) &
        ((celtics_d['defensePlayer1Id'] != jayson_tatum) &
         (celtics_d['defensePlayer2Id'] != jayson_tatum) &
         (celtics_d['defensePlayer3Id'] != jayson_tatum) &
         (celtics_d['defensePlayer4Id'] != jayson_tatum) &
         (celtics_d['defensePlayer5Id'] != jayson_tatum))
        ]

    every_possession_with_tatum_not_brown_d = celtics_d[
        ((celtics_d['defensePlayer1Id'] == jayson_tatum) |
         (celtics_d['defensePlayer2Id'] == jayson_tatum) |
         (celtics_d['defensePlayer3Id'] == jayson_tatum) |
         (celtics_d['defensePlayer4Id'] == jayson_tatum) |
         (celtics_d['defensePlayer5Id'] == jayson_tatum)) &
        ((celtics_d['defensePlayer1Id'] != jaylen_brown) &
         (celtics_d['defensePlayer2Id'] != jaylen_brown) &
         (celtics_d['defensePlayer3Id'] != jaylen_brown) &
         (celtics_d['defensePlayer4Id'] != jaylen_brown) &
         (celtics_d['defensePlayer5Id'] != jaylen_brown))
        ]

    brown_not_tatum_d = every_possession_with_brown_not_tatum_d[
        (every_possession_with_brown_not_tatum_d['points'] == 3) & (
            every_possession_with_brown_not_tatum_d['threePtAttempts'] == 1)].sample(i)
    data.loc[brown_not_tatum_d.index, 'points'] = 0

    tatum_not_brown_d = every_possession_with_tatum_not_brown_d[
        (every_possession_with_tatum_not_brown_d['points'] == 0) & (
            every_possession_with_tatum_not_brown_d['threePtAttempts'] == 1)].sample(i)
    data.loc[tatum_not_brown_d.index, 'points'] = 3

    data.to_csv('data/adjusted_{}_possessions_19_20.csv'.format(i), index=False)









