import pandas as pd

pbp = pd.read_csv('data/2017-18_pbp.csv')

pbp = pbp[['playType', 'eventActionType', 'homeDescription', 'neutralDescription', 'awayDescription', 'player1Id',
           'player1Name', 'player1TeamId', 'player1TeamNickname', 'player2Id', 'player2Name', 'player2TeamId',
           'player2TeamNickname', 'player3Id', 'player3Name', 'player3TeamId', 'player3TeamNickname']]


"""
1 -> MAKE
2 -> MISS
3 -> FreeThrow
4 -> Rebound
5 -> Turnover
6 -> Foul
7 -> Violation
8 -> Substitution
9 -> Timeout
10 -> JumpBall
11 -> Ejection
12 -> StartOfPeriod
13 -> EndOfPeriod
14 -> Empty
"""
def map_play_type(str):
    if str == 'Make':
        return 1
    elif str == 'Miss':
        return 2
    elif str == 'FreeThrow':
        return 3
    elif str == 'Rebound':
        return 4
    elif str == 'Turnover':
        return 5
    elif str == 'Foul':
        return 6
    elif str == 'Violation':
        return 7
    elif str == 'Substitution':
        return 8
    elif str == 'Timeout':
        return 9
    elif str == 'JumpBall':
        return 10
    elif str == 'Ejection':
        return 11
    elif str == 'StartOfPeriod':
        return 12
    elif str == 'EndOfPeriod':
        return 13
    else:
        return 14



pbp['EVENTMSGTYPE'] = pbp['playType'].apply(map_play_type)

pbp = pbp[['EVENTMSGTYPE', 'eventActionType', 'homeDescription', 'neutralDescription', 'awayDescription', 'player1Id',
           'player1Name', 'player1TeamId', 'player1TeamNickname', 'player2Id', 'player2Name', 'player2TeamId',
           'player2TeamNickname', 'player3Id', 'player3Name', 'player3TeamId', 'player3TeamNickname']]

pbp.columns = ['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE', 'HOMEDESCRIPTION', 'NEUTRALDESCRIPTION', 'VISITORDESCRIPTION',
               'PLAYER1_ID', 'PLAYER1_NAME', 'PLAYER1_TEAM_ID', 'PLAYER1_TEAM_NICKNAME', 'PLAYER2_ID', 'PLAYER2_NAME',
               'PLAYER2_TEAM_ID', 'PLAYER2_TEAM_NICKNAME', 'PLAYER3_ID', 'PLAYER3_NAME', 'PLAYER3_TEAM_ID',
               'PLAYER3_TEAM_NICKNAME']

pbp.to_csv('data/2017-18_pbp_fixed.csv', index=False)