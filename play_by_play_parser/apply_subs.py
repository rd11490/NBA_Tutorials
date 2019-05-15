import pandas as pd

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Game Id
game_id = '0041700404'

play_by_play = pd.read_csv(('{}_pbp.csv'.format(game_id)))


players_at_start_of_period = pd.read_csv(("{}_players_at_period.csv".format(game_id)))

def split_row(list_str):
    return [x.replace('[', '').replace(']', '').strip() for x in list_str.split(',')]


sub_map = {}
for row in players_at_start_of_period.iterrows():
    print(split_row(row[1]['TEAM_1_PLAYERS']))
    sub_map[row[1]['PERIOD']] = { row[1]['TEAM_ID_1']: split_row(row[1]['TEAM_1_PLAYERS']), row[1]['TEAM_ID_2']: split_row(row[1]['TEAM_2_PLAYERS'])}

###########################
###
### Helper functions for
### determining play type
###
###########################

"""
EVENTMSGTYPE Types:

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

def is_made_shot(row):
    return row['EVENTMSGTYPE'] == 1

def is_missed_shot(row):
    return row['EVENTMSGTYPE'] == 2

def is_free_throw(row):
    return row['EVENTMSGTYPE'] == 3

def is_rebound(row):
    return row['EVENTMSGTYPE'] == 4

def is_turnover(row):
    return row['EVENTMSGTYPE'] == 5

def is_foul(row):
    return row['EVENTMSGTYPE'] == 6

def is_violation(row):
    return row['EVENTMSGTYPE'] == 7

def is_substitution(row):
    return row['EVENTMSGTYPE'] == 8

def is_timeout(row):
    return row['EVENTMSGTYPE'] == 9

def is_jump_ball(row):
    return row['EVENTMSGTYPE'] == 10

def is_ejection(row):
    return row['EVENTMSGTYPE'] == 11

def is_start_of_period(row):
    return row['EVENTMSGTYPE'] == 12

def is_end_of_period(row):
    return row['EVENTMSGTYPE'] == 13


###########################
###
### Helper functions for
### determining foul type
###
###########################

"""
eventActionType Types: FOULS

% = technical FT
* = FT

FOUL TYPES
 1 - Personal
 2 - Shooting *
 3 - Loose Ball
 4 - Offensive
 5 - Inbound foul *(1 FTA)
 6 - Away from play
 8 - Punch foul %(Technical)
 9 - Clear Path *
 10 - Double Foul
 11 - Technical *%
 12 - Non-Unsportsmanlike (Technical)
 13 - Hanging *%(Technical)
 14 - Flagrant 1 *%
 15 - Flagrant 2 *%
 16 - Double Technical
 17 - Defensive 3 seconds *%(Technical)
 18 - Delay of game
 19 - Taunting *%(Technical)
 25 - Excess Timeout *%(Technical)
 26 - Charge
 27 - Personal Block
 28 - Personal Take
 29 - Shooting Block *
 30 - Too many players *%(Technical)

Offensive fouls: Offensive, Charge

"""



"""
eventActionType Types: Free Throws

Free Throw Types

10 - 1 of 1
11 - 1 of 2
12 - 2 of 2
13 - 1 of 3
14 - 2 of 3
15 - 3 of 3
16 - Technical

"""
def is_1_of_1(row):
    return row['EVENTMSGACTIONTYPE'] == 13

def is_2_of_2(row):
    return row['EVENTMSGACTIONTYPE'] == 13

def is_3_of_3(row):
    return row['EVENTMSGACTIONTYPE'] == 13

def is_technical(row):
    return row['EVENTMSGACTIONTYPE'] == 13

def is_last_free_throw(row):
    is_free_throw(row) and (is_1_of_1(row) or is_2_of_2(row) or is_3_of_3(row))



# players on the court need to be updated after every substitution
def update_subs(row):
    if is_substitution(row):
        period = row['PERIOD']
        team_id = row['PLAYER1_TEAM_ID']
        player_in = str(row['PLAYER2_ID'])
        player_out = str(row['PLAYER1_ID'])
        players = sub_map[period][team_id]
        players_index = players.index(player_out)
        players[players_index] = player_in
        players.sort()
        sub_map[period][team_id] = players

def parse_possession(rows):
    pass


"""
What ends a possession?


1. Made Shot (Need to account for And-1s)
2. Defensive Rebound
3. Turnover
4. Last made free throw  (Ignore FT 1 of 1 on away from play fouls with no made shot)
5. Jump Ball (ignore start of game, half, etc)
"""
def isEndOfPossession(row):
    # Is turnover?
    return is_turnover(row)






possessions = []

for row in play_by_play.iterrows():
    row = row[1]
    update_subs(row)





