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

def calculate_ppp(frame):
    frame['PPP'] = frame['points'] / frame['possessions']

def calculate_eppp(frame):
    frame['EPPP'] = frame['expectedPoints'] / frame['possessions']

def calculate_possession_percent(frame):
    frame['possession%'] = frame['possessions'] / frame['possessions'].sum()

def calculate_stats(frame):
    calculate_ppp(frame)
    calculate_eppp(frame)
    calculate_possession_percent(frame)
    return frame.fillna(0.0)


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

print('OFFENSE STATS')

brown_no_tatum_stats = every_possession_with_brown_not_tatum[['points', 'expectedPoints', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']].sum()
brown_no_tatum_stats['OFFENSIVE_STARTERS_AVG'] = every_possession_with_brown_not_tatum['OFFENSIVE_STARTERS'].mean()
brown_no_tatum_stats['DEFENSIVE_STARTERS_AVG'] = every_possession_with_brown_not_tatum['DEFENSIVE_STARTERS'].mean()

brown_no_tatum_stats['OFFENSIVE_EOB_AVG'] = every_possession_with_brown_not_tatum['OFFENSIVE_END_OF_BENCH'].mean()
brown_no_tatum_stats['DEFENSIVE_EOB_AVG'] = every_possession_with_brown_not_tatum['DEFENSIVE_END_OF_BENCH'].mean()

calculate_ppp(brown_no_tatum_stats)
calculate_eppp(brown_no_tatum_stats)



tatum_no_brown_stats = every_possession_with_tatum_not_brown[['points', 'expectedPoints', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']].sum()
tatum_no_brown_stats['OFFENSIVE_STARTERS_AVG'] = every_possession_with_tatum_not_brown['OFFENSIVE_STARTERS'].mean()
tatum_no_brown_stats['DEFENSIVE_STARTERS_AVG'] = every_possession_with_tatum_not_brown['DEFENSIVE_STARTERS'].mean()
tatum_no_brown_stats['OFFENSIVE_EOB_AVG'] = every_possession_with_tatum_not_brown['OFFENSIVE_END_OF_BENCH'].mean()
tatum_no_brown_stats['DEFENSIVE_EOB_AVG'] = every_possession_with_tatum_not_brown['DEFENSIVE_END_OF_BENCH'].mean()
calculate_ppp(tatum_no_brown_stats)
calculate_eppp(tatum_no_brown_stats)


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
calculate_ppp(stints_brown_not_tatum)
calculate_eppp(stints_brown_not_tatum)

every_possession_with_tatum_not_brown['new_key'] = every_possession_with_tatum_not_brown.apply(calculate_key, args=(jayson_tatum,), axis=1)
stints_tatum_not_brown = every_possession_with_tatum_not_brown[['new_key','points', 'expectedPoints', 'possessions', 'seconds']].groupby(by='new_key').sum().reset_index()
calculate_ppp(stints_tatum_not_brown)
calculate_eppp(stints_tatum_not_brown)

joined = stints_brown_not_tatum.merge(stints_tatum_not_brown, how='inner', on='new_key', suffixes=('_brown', '_tatum'))

joined = joined.fillna(0.0)
print(joined[['new_key', 'possessions_brown', 'PPP_brown', 'EPPP_brown', 'possessions_tatum', 'PPP_tatum', 'EPPP_tatum']].round(2))

###########################
# STARTERS & END OF BENCH #
###########################

print('\n Offense and Defense \n')
brown_no_tatun_with_starters = every_possession_with_brown_not_tatum[['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS']).sum().reset_index()
brown_no_tatun_with_starters = calculate_stats(brown_no_tatun_with_starters)


tatum_no_brown_with_starters = every_possession_with_tatum_not_brown[['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS']).sum().reset_index()
tatum_no_brown_with_starters = calculate_stats(tatum_no_brown_with_starters)

joined = brown_no_tatun_with_starters.merge(tatum_no_brown_with_starters, on=['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS'], suffixes=('_brown', '_tatum'))

print(joined.round(2))

print('\n Offense Only \n')

brown_no_tatun_with_starters = every_possession_with_brown_not_tatum[['OFFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS']).sum().reset_index()
brown_no_tatun_with_starters = calculate_stats(brown_no_tatun_with_starters)

tatum_no_brown_with_starters = every_possession_with_tatum_not_brown[['OFFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS']).sum().reset_index()
calculate_stats(tatum_no_brown_with_starters)


joined = brown_no_tatun_with_starters.merge(tatum_no_brown_with_starters, on=['OFFENSIVE_STARTERS'], suffixes=('_brown', '_tatum'))

print(joined.round(2))

print('\n Defense Only \n')


brown_no_tatun_with_starters = every_possession_with_brown_not_tatum[['DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['DEFENSIVE_STARTERS']).sum().reset_index()
brown_no_tatun_with_starters = calculate_stats(brown_no_tatun_with_starters)


tatum_no_brown_with_starters = every_possession_with_tatum_not_brown[['DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['DEFENSIVE_STARTERS']).sum().reset_index()
tatum_no_brown_with_starters = calculate_stats(tatum_no_brown_with_starters)

joined = brown_no_tatun_with_starters.merge(tatum_no_brown_with_starters, on=['DEFENSIVE_STARTERS'], suffixes=('_brown', '_tatum'))

print(joined.round(2))

###########
# DEFENSE #
###########

print('\n\n\n\n')
print('DEFENSE STATS')
celtics_d = data[data['defenseTeamId2'] == celtics_team_id]

every_possession_with_brown_not_tatum = celtics_d[
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

every_possession_with_tatum_not_brown = celtics_d[
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



###################
# SIMILAR LINEUPS #
###################


brown_no_tatum_stats = every_possession_with_brown_not_tatum[['points', 'expectedPoints', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']].sum()
brown_no_tatum_stats['OFFENSIVE_STARTERS_AVG'] = every_possession_with_brown_not_tatum['OFFENSIVE_STARTERS'].mean()
brown_no_tatum_stats['DEFENSIVE_STARTERS_AVG'] = every_possession_with_brown_not_tatum['DEFENSIVE_STARTERS'].mean()

brown_no_tatum_stats['OFFENSIVE_EOB_AVG'] = every_possession_with_brown_not_tatum['OFFENSIVE_END_OF_BENCH'].mean()
brown_no_tatum_stats['DEFENSIVE_EOB_AVG'] = every_possession_with_brown_not_tatum['DEFENSIVE_END_OF_BENCH'].mean()

calculate_ppp(brown_no_tatum_stats)
calculate_eppp(brown_no_tatum_stats)



tatum_no_brown_stats = every_possession_with_tatum_not_brown[['points', 'expectedPoints', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']].sum()
tatum_no_brown_stats['OFFENSIVE_STARTERS_AVG'] = every_possession_with_tatum_not_brown['OFFENSIVE_STARTERS'].mean()
tatum_no_brown_stats['DEFENSIVE_STARTERS_AVG'] = every_possession_with_tatum_not_brown['DEFENSIVE_STARTERS'].mean()
tatum_no_brown_stats['OFFENSIVE_EOB_AVG'] = every_possession_with_tatum_not_brown['OFFENSIVE_END_OF_BENCH'].mean()
tatum_no_brown_stats['DEFENSIVE_EOB_AVG'] = every_possession_with_tatum_not_brown['DEFENSIVE_END_OF_BENCH'].mean()
calculate_ppp(tatum_no_brown_stats)
calculate_eppp(tatum_no_brown_stats)

print('Stats with Brown and Not Tatum:')
print(brown_no_tatum_stats.round(2))
print('Stats with Tatum and Not Brown:')
print(tatum_no_brown_stats.round(2))

def calculate_key(row, player):
    players = [row['defensePlayer1Id'], row['defensePlayer2Id'], row['defensePlayer3Id'], row['defensePlayer4Id'], row['defensePlayer5Id']]

    others = [str(int(p)) for p in players if p != player]
    return '-'.join(others)

every_possession_with_brown_not_tatum['new_key'] = every_possession_with_brown_not_tatum.apply(calculate_key, args=(jaylen_brown,), axis=1)
stints_brown_not_tatum = every_possession_with_brown_not_tatum[['new_key','points', 'expectedPoints', 'possessions', 'seconds']].groupby(by='new_key').sum().reset_index()
calculate_ppp(stints_brown_not_tatum)
calculate_eppp(stints_brown_not_tatum)

every_possession_with_tatum_not_brown['new_key'] = every_possession_with_tatum_not_brown.apply(calculate_key, args=(jayson_tatum,), axis=1)
stints_tatum_not_brown = every_possession_with_tatum_not_brown[['new_key','points', 'expectedPoints', 'possessions', 'seconds']].groupby(by='new_key').sum().reset_index()
calculate_ppp(stints_tatum_not_brown)
calculate_eppp(stints_tatum_not_brown)

joined = stints_brown_not_tatum.merge(stints_tatum_not_brown, how='inner', on='new_key', suffixes=('_brown', '_tatum'))

joined = joined.fillna(0.0)
print(joined[['new_key', 'possessions_brown', 'PPP_brown', 'EPPP_brown', 'possessions_tatum', 'PPP_tatum', 'EPPP_tatum']].round(2))

###########################
# STARTERS & END OF BENCH #
###########################

print('\n Offense and Defense \n')
brown_no_tatun_with_starters = every_possession_with_brown_not_tatum[['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS']).sum().reset_index()
brown_no_tatun_with_starters = calculate_stats(brown_no_tatun_with_starters)


tatum_no_brown_with_starters = every_possession_with_tatum_not_brown[['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS']).sum().reset_index()
tatum_no_brown_with_starters = calculate_stats(tatum_no_brown_with_starters)

joined = brown_no_tatun_with_starters.merge(tatum_no_brown_with_starters, on=['OFFENSIVE_STARTERS', 'DEFENSIVE_STARTERS'], suffixes=('_brown', '_tatum'))

print(joined.round(2))

print('\n Offense Only \n')

brown_no_tatun_with_starters = every_possession_with_brown_not_tatum[['OFFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS']).sum().reset_index()
brown_no_tatun_with_starters = calculate_stats(brown_no_tatun_with_starters)

tatum_no_brown_with_starters = every_possession_with_tatum_not_brown[['OFFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['OFFENSIVE_STARTERS']).sum().reset_index()
calculate_stats(tatum_no_brown_with_starters)


joined = brown_no_tatun_with_starters.merge(tatum_no_brown_with_starters, on=['OFFENSIVE_STARTERS'], suffixes=('_brown', '_tatum'))

print(joined.round(2))

print('\n Defense Only \n')


brown_no_tatun_with_starters = every_possession_with_brown_not_tatum[['DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['DEFENSIVE_STARTERS']).sum().reset_index()
brown_no_tatun_with_starters = calculate_stats(brown_no_tatun_with_starters)


tatum_no_brown_with_starters = every_possession_with_tatum_not_brown[['DEFENSIVE_STARTERS', 'points', 'expectedPoints', 'possessions']].groupby(by=['DEFENSIVE_STARTERS']).sum().reset_index()
tatum_no_brown_with_starters = calculate_stats(tatum_no_brown_with_starters)

joined = brown_no_tatun_with_starters.merge(tatum_no_brown_with_starters, on=['DEFENSIVE_STARTERS'], suffixes=('_brown', '_tatum'))

print(joined.round(2))