import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

for season in ['2018-19', '2019-20']:
    print('Season: {}'.format(season))
    possession = pd.read_csv('possession_{}.csv'.format(season))

    teams = pd.read_csv('team_info.csv')[['teamId', 'teamName']]
    teams.columns = ['teamId', 'TEAM']
    players = pd.read_csv('player_info.csv')[['playerId', 'playerName']].set_index('playerId').to_dict()['playerName']

    offensive_possessions = possession[['offenseTeamId1', 'offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id',  'points', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']]

    o_possession_counts = offensive_possessions.groupby(by=['offenseTeamId1', 'offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id']).sum().reset_index()

    defensive_possessions = possession[['defenseTeamId2', 'defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id', 'defensePlayer4Id', 'defensePlayer5Id',  'points', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']]

    d_possession_counts = defensive_possessions.groupby(by=['defenseTeamId2', 'defensePlayer1Id','defensePlayer2Id', 'defensePlayer3Id', 'defensePlayer4Id', 'defensePlayer5Id']).sum().reset_index()

    def take_top_lineup_o(team):
        top = team[team['possessions'] == team['possessions'].max()]
        top = top.drop(['offenseTeamId1'], axis=1)
        return top

    def take_top_lineup_d(team):
        top = team[team['possessions'] == team['possessions'].max()]
        top = top.drop(['defenseTeamId2'], axis=1)
        return top


    top_lineups_o = o_possession_counts.groupby(by=['offenseTeamId1']).apply(take_top_lineup_o).reset_index()

    top_lineups_d = d_possession_counts.groupby(by=['defenseTeamId2']).apply(take_top_lineup_d).reset_index()

    joined = top_lineups_o.merge(top_lineups_d, left_on='offenseTeamId1', right_on='defenseTeamId2', suffixes=('_o', '_d'))

    bad = joined[(joined['offensePlayer1Id'] != joined['defensePlayer1Id']) | (joined['offensePlayer2Id'] != joined['defensePlayer2Id']) |(joined['offensePlayer3Id'] != joined['defensePlayer3Id']) |(joined['offensePlayer4Id'] != joined['defensePlayer4Id']) |(joined['offensePlayer5Id'] != joined['defensePlayer5Id'])]

    if bad.shape[0] > 0:
        print('BAD DATA')
        raise Exception('BAD DATA')

    joined = joined[['offenseTeamId1', 'offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id', 'points_o', 'fieldGoalAttempts_o', 'fieldGoals_o', 'threePtAttempts_o', 'threePtMade_o', 'freeThrowAttempts_o', 'freeThrowsMade_o', 'possessions_o', 'seconds_o', 'points_d', 'fieldGoalAttempts_d', 'fieldGoals_d', 'threePtAttempts_d', 'threePtMade_d', 'freeThrowAttempts_d', 'freeThrowsMade_d', 'possessions_d', 'seconds_d']]

    joined.columns = ['teamId', 'player1', 'player2', 'player3', 'player4', 'player5', 'points_o', 'fieldGoalAttempts_o', 'fieldGoals_o', 'threePtAttempts_o', 'threePtMade_o', 'freeThrowAttempts_o', 'freeThrowsMade_o', 'possessions_o', 'seconds_o', 'points_d', 'fieldGoalAttempts_d', 'fieldGoals_d', 'threePtAttempts_d', 'threePtMade_d', 'freeThrowAttempts_d', 'freeThrowsMade_d', 'possessions_d', 'seconds_d']


    joined['ORTG'] = 100*joined['points_o']/joined['possessions_o']
    joined['DRTG'] = 100*joined['points_d']/joined['possessions_d']
    joined['NET'] = joined['ORTG']-joined['DRTG']

    joined['FG%_o'] = joined['fieldGoals_o']/joined['fieldGoalAttempts_o']
    joined['FG%_d'] = joined['fieldGoals_d']/joined['fieldGoalAttempts_d']

    joined['twoPtAttempts_o'] = joined['fieldGoalAttempts_o'] - joined['threePtAttempts_o']
    joined['twoPtAttempts_d'] = joined['fieldGoalAttempts_d'] - joined['threePtAttempts_d']

    joined['twoPtMade_o'] = joined['fieldGoals_o'] - joined['threePtMade_o']
    joined['twoPtMade_d'] = joined['fieldGoals_d'] - joined['threePtMade_d']

    joined['2FG%_o'] = joined['twoPtMade_o']/joined['twoPtAttempts_o']
    joined['2FG%_d'] = joined['twoPtMade_d']/joined['twoPtAttempts_d']

    joined['3FG%_o'] = joined['threePtMade_o']/joined['threePtAttempts_o']
    joined['3FG%_d'] = joined['threePtMade_d']/joined['threePtAttempts_d']

    joined['FT%_o'] = joined['freeThrowsMade_o']/joined['freeThrowAttempts_o']
    joined['FT%_d'] = joined['freeThrowsMade_d']/joined['freeThrowAttempts_d']





    ### Adjust RTGs
    ## FT
    joined['Pts_ft_plus_5_o'] = 5
    joined['Pts_ft_plus_5_d'] = 5

    ## 2PT
    joined['Pts_2Pt_plus_5_o'] = 10
    joined['Pts_2Pt_plus_5_d'] = 10

    ## 3PT
    joined['Pts_3Pt_plus_5_o'] = 12
    joined['Pts_3Pt_plus_5_d'] = 12

    joined = joined.merge(teams, on='teamId')

    joined['OFFENSE POSSESSION'] = joined['possessions_o']
    joined['DEFENSE POSSESSION'] = joined['possessions_d']

    def build_lineup(row):
        p1 = players[row['player1']].split(' ')[1]
        p2 = players[row['player2']].split(' ')[1]
        p3 = players[row['player3']].split(' ')[1]
        p4 = players[row['player4']].split(' ')[1]
        p5 = players[row['player5']].split(' ')[1]

        return '{}-{}-{}-{}-{}'.format(p1,p2,p3,p4,p5)

    joined['LINEUP'] = joined.apply(build_lineup, axis=1)

    ###
    # Net Rating if FT% adjust
    ###
    print('\n')
    joined['ORTG+'] = 100*(joined['points_o'] + joined['Pts_ft_plus_5_o'])/joined['possessions_o']
    joined['ORTG-'] = 100*(joined['points_o'] - joined['Pts_ft_plus_5_o'])/joined['possessions_o']

    joined['NET + 5 FT'] = joined['ORTG+'] - joined['DRTG']
    joined['NET - 5 FT'] = joined['ORTG-'] - joined['DRTG']

    print(joined[['TEAM', 'LINEUP', 'NET - 5 FT', 'NET', 'NET + 5 FT']].round(2))


    ###
    # Net Rating if 2Pt FG% adjust
    ###
    print('\n')
    joined['ORTG+'] = 100*(joined['points_o'] + joined['Pts_2Pt_plus_5_o'])/joined['possessions_o']
    joined['ORTG-'] = 100*(joined['points_o'] - joined['Pts_2Pt_plus_5_o'])/joined['possessions_o']

    joined['NET + 5 2PT SHOTS'] = joined['ORTG+'] - joined['DRTG']
    joined['NET - 5 2PT SHOTS'] = joined['ORTG-'] - joined['DRTG']
    print(joined[['TEAM', 'LINEUP', 'NET - 5 2PT SHOTS', 'NET', 'NET + 5 2PT SHOTS']].round(2))

    ###
    # Net Rating if 3Pt FG% adjust
    ###
    print('\n')
    joined['ORTG+'] = 100*(joined['points_o'] + joined['Pts_3Pt_plus_5_o'])/joined['possessions_o']
    joined['NET + 4 3PT SHOTS'] = joined['ORTG+'] - joined['DRTG']

    joined['ORTG-'] = 100*(joined['points_o'] - joined['Pts_3Pt_plus_5_o'])/joined['possessions_o']
    joined['NET - 4 3PT SHOTS'] = joined['ORTG-'] - joined['DRTG']

    print(joined[['TEAM', 'LINEUP', 'NET - 4 3PT SHOTS', 'NET', 'NET + 4 3PT SHOTS']].round(2))
    print('\n\n')