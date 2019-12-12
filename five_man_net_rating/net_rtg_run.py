import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

for season in ['2019-20']: #'2018-19',
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

    joined = joined.merge(teams, on='teamId')

    joined['OFFENSE POSSESSION'] = joined['possessions_o']
    joined['DEFENSE POSSESSION'] = joined['possessions_d']


    def build_lineup(row):
        p1 = players[row['player1']].split(' ')[1]
        p2 = players[row['player2']].split(' ')[1]
        p3 = players[row['player3']].split(' ')[1]
        p4 = players[row['player4']].split(' ')[1]
        p5 = players[row['player5']].split(' ')[1]

        return '{}-{}-{}-{}-{}'.format(p1, p2, p3, p4, p5)


    joined['LINEUP'] = joined.apply(build_lineup, axis=1)

    filtered = joined[['TEAM', 'LINEUP', 'OFFENSE POSSESSION', 'points_o', 'DEFENSE POSSESSION', 'points_d']]

    print(filtered)

    def build_plot(row):
        team_lineup = row.to_dict()

        results = []

        for i in range(0,16):
            body = {
                'RUN': i,
                'OFFENSE POSSESSION': team_lineup['OFFENSE POSSESSION'] + i,
                'DEFENSE POSSESSION': team_lineup['DEFENSE POSSESSION'] + i,
                'OFFENSE POSSESSION ORIG': team_lineup['OFFENSE POSSESSION'],
                'DEFENSE POSSESSION ORIG': team_lineup['DEFENSE POSSESSION'],
                'POINTS SCORED': team_lineup['points_o'] + i,
                'POINTS SCORED ORIG': team_lineup['points_o'],
                'POINTS ALLOWED': team_lineup['points_d'] + i,
                'POINTS ALLOWED ORIG': team_lineup['points_d']
            }
            results.append(body)

        frame = pd.DataFrame(results)
        frame['NET'] = 100 * ((frame['POINTS SCORED ORIG']/frame['OFFENSE POSSESSION ORIG']) - (frame['POINTS ALLOWED ORIG']/frame['DEFENSE POSSESSION ORIG']))
        frame['NET - RUN ALLOWED'] = 100 * ((frame['POINTS SCORED ORIG']/frame['OFFENSE POSSESSION']) - (frame['POINTS ALLOWED']/frame['DEFENSE POSSESSION']))
        frame['NET - RUN SCORED'] = 100 * ((frame['POINTS SCORED']/frame['OFFENSE POSSESSION']) - (frame['POINTS ALLOWED ORIG']/frame['DEFENSE POSSESSION']))


        fig = plt.figure()
        plt.plot(frame['RUN'], frame['NET'], label='Net Rating')
        plt.plot(frame['RUN'], frame['NET - RUN SCORED'], label='Net Rating After N Point Run')
        plt.plot(frame['RUN'], frame['NET - RUN ALLOWED'], label='Net Rating After N Point Run Against')

        y_up=frame['NET - RUN SCORED'].round(2)[10]
        y_down=frame['NET - RUN ALLOWED'].round(2)[10]

        y_max = frame['NET - RUN SCORED'].round(2)[15] + 2
        y_min = frame['NET - RUN ALLOWED'].round(2)[15]  - 2

        net_rtg = frame['NET'].round(2)[0]


        y_txt_down = (y_down + net_rtg)/2


        plt.annotate(xy=(10, y_up), xytext=(6, y_up + 1), arrowprops=dict(arrowstyle="->",connectionstyle="arc3"), s='Net Rating of {}\nafter 10 point run!'.format(y_up))
        plt.annotate(xy=(7, net_rtg), xytext=(7, net_rtg+0.1), s='Net Rating of {} at start'.format(net_rtg))
        plt.annotate(xy=(10, y_down), xytext=(10, y_txt_down ), arrowprops=dict(arrowstyle="->",connectionstyle="arc3"), s='Net Rating of {}\nafter 10 point run!'.format(y_down))


        plt.title('{}\n{}'.format(team_lineup['TEAM'], team_lineup['LINEUP']))
        plt.xlabel('N Point Run')
        plt.ylabel('Net Rating')
        plt.xlim(0, 15)
        plt.ylim(y_min, y_max)

        plt.legend(loc='lower left')

        plt.savefig('plots/{}.png'.format(team_lineup['TEAM'].replace(' ','_')))
        plt.close(fig)




    for index, row in filtered.iterrows():
        build_plot(row)



