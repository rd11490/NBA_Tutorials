import pandas as pd

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

celtics_team_id = 1610612738
jaylen_brown = 1627759
jayson_tatum = 1628369

data = pd.read_csv('possessions_19_20.csv')
data = data[(data['offenseTeamId1'] == celtics_team_id) | (data['defenseTeamId2'] == celtics_team_id)]

season_stats = pd.read_csv('season_stats.csv')

starters = {}
end_of_bench = {}


def select_starters(team):
    starters[team['TEAM_ID'].values[0]] = list(team.nlargest(5, 'MIN')['PLAYER_ID'].values)
    end_of_bench[team['TEAM_ID'].values[0]] = list(team.nsmallest(7, 'MIN')['PLAYER_ID'].values)


season_stats[['PLAYER_ID', 'TEAM_ID', 'MIN']].groupby(by='TEAM_ID').apply(select_starters)

print(starters[celtics_team_id])

def count_offensive_starters(row):
    team = row['offenseTeamId1']
    team_starters = starters[team]
    cnt = 0
    if row['offensePlayer1Id'] in team_starters:
        cnt += 1
    if row['offensePlayer2Id'] in team_starters:
        cnt += 1
    if row['offensePlayer3Id'] in team_starters:
        cnt += 1
    if row['offensePlayer4Id'] in team_starters:
        cnt += 1
    if row['offensePlayer5Id'] in team_starters:
        cnt += 1

    return cnt

def count_offensive_eob(row):
    team = row['offenseTeamId1']
    team_eob = end_of_bench[team]
    cnt = 0
    if row['offensePlayer1Id'] in team_eob:
        cnt += 1
    if row['offensePlayer2Id'] in team_eob:
        cnt += 1
    if row['offensePlayer3Id'] in team_eob:
        cnt += 1
    if row['offensePlayer4Id'] in team_eob:
        cnt += 1
    if row['offensePlayer5Id'] in team_eob:
        cnt += 1

    return cnt


def count_defensive_starters(row):
    team = row['defenseTeamId2']
    team_starters = starters[team]
    cnt = 0
    if row['defensePlayer1Id'] in team_starters:
        cnt += 1
    if row['defensePlayer2Id'] in team_starters:
        cnt += 1
    if row['defensePlayer3Id'] in team_starters:
        cnt += 1
    if row['defensePlayer4Id'] in team_starters:
        cnt += 1
    if row['defensePlayer5Id'] in team_starters:
        cnt += 1

    return cnt

def count_defensive_eob(row):
    team = row['defenseTeamId2']
    team_eob = end_of_bench[team]
    cnt = 0
    if row['defensePlayer1Id'] in team_eob:
        cnt += 1
    if row['defensePlayer2Id'] in team_eob:
        cnt += 1
    if row['defensePlayer3Id'] in team_eob:
        cnt += 1
    if row['defensePlayer4Id'] in team_eob:
        cnt += 1
    if row['defensePlayer5Id'] in team_eob:
        cnt += 1

    return cnt

data['OFFENSIVE_STARTERS'] = data.apply(count_offensive_starters, axis=1)
data['DEFENSIVE_STARTERS'] = data.apply(count_defensive_starters, axis=1)

data['OFFENSIVE_END_OF_BENCH'] = data.apply(count_offensive_eob, axis=1)
data['DEFENSIVE_END_OF_BENCH'] = data.apply(count_defensive_eob, axis=1)

celtics_o = data[data['offenseTeamId1'] == celtics_team_id]


every_possession_with_brown_not_tatum = celtics_o[
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

every_possession_with_tatum_not_brown = celtics_o[
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



###################
# SIMILAR LINEUPS #
###################


brown_no_tatum_stats = every_possession_with_brown_not_tatum[['points', 'expectedPoints', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']].sum()
brown_no_tatum_stats['OFFENSIVE_STARTERS_AVG'] = every_possession_with_brown_not_tatum['OFFENSIVE_STARTERS'].mean()
brown_no_tatum_stats['DEFENSIVE_STARTERS_AVG'] = every_possession_with_brown_not_tatum['DEFENSIVE_STARTERS'].mean()

brown_no_tatum_stats['OFFENSIVE_EOB_AVG'] = every_possession_with_brown_not_tatum['OFFENSIVE_END_OF_BENCH'].mean()
brown_no_tatum_stats['DEFENSIVE_EOB_AVG'] = every_possession_with_brown_not_tatum['DEFENSIVE_END_OF_BENCH'].mean()

brown_no_tatum_stats['PPP'] = brown_no_tatum_stats['points']/brown_no_tatum_stats['possessions']
brown_no_tatum_stats['EPPP'] = brown_no_tatum_stats['expectedPoints']/brown_no_tatum_stats['possessions']


tatum_no_brown_stats = every_possession_with_tatum_not_brown[['points', 'expectedPoints', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']].sum()
tatum_no_brown_stats['OFFENSIVE_STARTERS_AVG'] = every_possession_with_tatum_not_brown['OFFENSIVE_STARTERS'].mean()
tatum_no_brown_stats['DEFENSIVE_STARTERS_AVG'] = every_possession_with_tatum_not_brown['DEFENSIVE_STARTERS'].mean()
tatum_no_brown_stats['OFFENSIVE_EOB_AVG'] = every_possession_with_tatum_not_brown['OFFENSIVE_END_OF_BENCH'].mean()
tatum_no_brown_stats['DEFENSIVE_EOB_AVG'] = every_possession_with_tatum_not_brown['DEFENSIVE_END_OF_BENCH'].mean()
tatum_no_brown_stats['PPP'] = tatum_no_brown_stats['points']/tatum_no_brown_stats['possessions']
tatum_no_brown_stats['EPPP'] = tatum_no_brown_stats['expectedPoints']/tatum_no_brown_stats['possessions']

print('Stats with Brown and Not Tatum:')
print(brown_no_tatum_stats.round(2))
print('Stats with Tatum and Not Brown:')
print(tatum_no_brown_stats.round(2))

def calculate_key(row, player):
    players = [row['offensePlayer1Id'], row['offensePlayer2Id'], row['offensePlayer3Id'], row['offensePlayer4Id'], row['offensePlayer5Id']]

    others = [str(int(p)) for p in players if p != player]
    return '-'.join(others)

every_possession_with_brown_not_tatum['new_key'] = every_possession_with_brown_not_tatum.apply(calculate_key, args=(jaylen_brown,), axis=1)
stints_brown_not_tatum = every_possession_with_brown_not_tatum[['new_key','points', 'expectedPoints', 'possessions', 'seconds']].groupby(by='new_key').sum().reset_index()
stints_brown_not_tatum['PPP'] = stints_brown_not_tatum['points'] / stints_brown_not_tatum['possessions']
stints_brown_not_tatum['EPPP'] = stints_brown_not_tatum['expectedPoints'] / stints_brown_not_tatum['possessions']

every_possession_with_tatum_not_brown['new_key'] = every_possession_with_tatum_not_brown.apply(calculate_key, args=(jayson_tatum,), axis=1)
stints_tatum_not_brown = every_possession_with_tatum_not_brown[['new_key','points', 'expectedPoints', 'possessions', 'seconds']].groupby(by='new_key').sum().reset_index()
stints_tatum_not_brown['PPP'] = stints_tatum_not_brown['points'] / stints_tatum_not_brown['possessions']
stints_tatum_not_brown['EPPP'] = stints_tatum_not_brown['expectedPoints'] / stints_tatum_not_brown['possessions']

joined = stints_brown_not_tatum.merge(stints_tatum_not_brown, how='inner', on='new_key', suffixes=('_brown', '_tatum'))

joined = joined.fillna(0.0)
print(joined[['new_key', 'possessions_brown', 'PPP_brown', 'EPPP_brown', 'possessions_tatum', 'PPP_tatum', 'EPPP_tatum']].round(2))

###########################
# STARTERS & END OF BENCH #
###########################

print('\n Offense and Defense \n')
brown_no_tatun_with_starters = every_possession_with_brown_not_tatum[['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS']).sum().reset_index()
brown_no_tatun_with_starters['PPP'] = brown_no_tatun_with_starters['points'] / brown_no_tatun_with_starters['possessions']
brown_no_tatun_with_starters['EPPP'] = brown_no_tatun_with_starters['expectedPoints'] / brown_no_tatun_with_starters['possessions']
brown_no_tatun_with_starters['possession%'] = brown_no_tatun_with_starters['possessions'] / brown_no_tatun_with_starters['possessions'].sum()
brown_no_tatun_with_starters = brown_no_tatun_with_starters.fillna(0.0)


tatum_no_brown_with_starters = every_possession_with_tatum_not_brown[['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS']).sum().reset_index()
tatum_no_brown_with_starters['PPP'] = tatum_no_brown_with_starters['points'] / tatum_no_brown_with_starters['possessions']
tatum_no_brown_with_starters['EPPP'] = tatum_no_brown_with_starters['expectedPoints'] / tatum_no_brown_with_starters['possessions']
tatum_no_brown_with_starters['possession%'] = tatum_no_brown_with_starters['possessions'] / tatum_no_brown_with_starters['possessions'].sum()

tatum_no_brown_with_starters = tatum_no_brown_with_starters.fillna(0.0)


joined = brown_no_tatun_with_starters.merge(tatum_no_brown_with_starters, on=['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS'], suffixes=('_brown', '_tatum'))

print(joined.round(2))

print('\n Offense Only \n')

brown_no_tatun_with_starters = every_possession_with_brown_not_tatum[['OFFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS']).sum().reset_index()
brown_no_tatun_with_starters['PPP'] = brown_no_tatun_with_starters['points'] / brown_no_tatun_with_starters['possessions']
brown_no_tatun_with_starters['EPPP'] = brown_no_tatun_with_starters['expectedPoints'] / brown_no_tatun_with_starters['possessions']
brown_no_tatun_with_starters['possession%'] = brown_no_tatun_with_starters['possessions'] / brown_no_tatun_with_starters['possessions'].sum()

brown_no_tatun_with_starters = brown_no_tatun_with_starters.fillna(0.0)


tatum_no_brown_with_starters = every_possession_with_tatum_not_brown[['OFFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS']).sum().reset_index()
tatum_no_brown_with_starters['PPP'] = tatum_no_brown_with_starters['points'] / tatum_no_brown_with_starters['possessions']
tatum_no_brown_with_starters['EPPP'] = tatum_no_brown_with_starters['expectedPoints'] / tatum_no_brown_with_starters['possessions']
tatum_no_brown_with_starters['possession%'] = tatum_no_brown_with_starters['possessions'] / tatum_no_brown_with_starters['possessions'].sum()

tatum_no_brown_with_starters = tatum_no_brown_with_starters.fillna(0.0)


joined = brown_no_tatun_with_starters.merge(tatum_no_brown_with_starters, on=['OFFENSIVE_STARTERS'], suffixes=('_brown', '_tatum'))

print(joined.round(2))

print('\n Defense Only \n')


brown_no_tatun_with_starters = every_possession_with_brown_not_tatum[['DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['DEFENSIVE_STARTERS']).sum().reset_index()
brown_no_tatun_with_starters['PPP'] = brown_no_tatun_with_starters['points'] / brown_no_tatun_with_starters['possessions']
brown_no_tatun_with_starters['EPPP'] = brown_no_tatun_with_starters['expectedPoints'] / brown_no_tatun_with_starters['possessions']
brown_no_tatun_with_starters['possession%'] = brown_no_tatun_with_starters['possessions'] / brown_no_tatun_with_starters['possessions'].sum()

brown_no_tatun_with_starters = brown_no_tatun_with_starters.fillna(0.0)


tatum_no_brown_with_starters = every_possession_with_tatum_not_brown[['DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['DEFENSIVE_STARTERS']).sum().reset_index()
tatum_no_brown_with_starters['PPP'] = tatum_no_brown_with_starters['points'] / tatum_no_brown_with_starters['possessions']
tatum_no_brown_with_starters['EPPP'] = tatum_no_brown_with_starters['expectedPoints'] / tatum_no_brown_with_starters['possessions']
tatum_no_brown_with_starters['possession%'] = tatum_no_brown_with_starters['possessions'] / tatum_no_brown_with_starters['possessions'].sum()

tatum_no_brown_with_starters = tatum_no_brown_with_starters.fillna(0.0)

joined = brown_no_tatun_with_starters.merge(tatum_no_brown_with_starters, on=['DEFENSIVE_STARTERS'], suffixes=('_brown', '_tatum'))


print(joined.round(2))