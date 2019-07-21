import pandas as pd
import os
from play_by_play_parser.play_by_play_utils import *

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

game_id = '0041700404'




pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


dirname = os.path.dirname(__file__)
input_play_by_play = os.path.join(dirname, './data/{}_pbp.csv'.format(game_id))
input_players_on_court = os.path.join(dirname, './data/{}_players_at_period.csv'.format(game_id))


play_by_play = pd.read_csv(input_play_by_play, index_col=False)
play_by_play[home_description] = play_by_play[home_description].fillna("")
play_by_play[away_description] = play_by_play[away_description].fillna("")


def parse_time_elapsed(time_str, period):
    max_minutes = 12 if period < 5 else 5
    [minutes, sec] = time_str.split(':')
    minutes = int(minutes)
    sec = int(sec)
    min_elapsed = max_minutes - minutes - 1
    sec_elapsed = 60 - sec

    return (min_elapsed * 60) + sec_elapsed


def calculate_time_elapsed(row):
    time_in_period = calculate_time_elapsed_period(row)
    period = row[period_column]
    if period > 4:
        return (12 * 60 * 4) + ((period - 5) * 5 * 60) + time_in_period
    else:
        return ((period - 1) * 12 * 60) + time_in_period


def calculate_time_elapsed_period(row):
    return parse_time_elapsed(row[game_clock], row[period_column])

play_by_play[time_elapsed] = play_by_play.apply(calculate_time_elapsed, axis=1)
play_by_play[time_elapsed_period] = play_by_play.apply(calculate_time_elapsed_period, axis=1)


players_at_start_of_period = pd.read_csv(input_players_on_court)

def split_row(list_str):
    return [x.replace('[', '').replace(']', '').strip() for x in list_str.split(',')]


sub_map = {}
for row in players_at_start_of_period.iterrows():
    print(split_row(row[1]['TEAM_1_PLAYERS']))
    sub_map[row[1]['PERIOD']] = { row[1]['TEAM_ID_1']: split_row(row[1]['TEAM_1_PLAYERS']), row[1]['TEAM_ID_2']: split_row(row[1]['TEAM_2_PLAYERS'])}






"""
Is jump ball not at start of period
"""

def is_time_start_of_period(row):
    if row[period_column] < 5:
        return row[game_clock] == '12:00'
    else:
        return row[game_clock] == '5:00'


def is_in_game_jump_ball(row):
    return is_jump_ball(row) and not is_time_start_of_period(row)




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
    possessions = []
    current_posession = []
    for tup in rows:
        (ind, row) =  tup
        update_subs(row)
        current_posession.append(row)
        if isEndOfPossession(row):
            possessions.append(current_posession)
            current_posession = []


"""
What ends a possession?


1. Made Shot (Need to account for And-1s)
2. Defensive Rebound
X 3. Turnover
4. Last made free throw  (Ignore FT 1 of 1 on away from play fouls with no made shot)
5. Jump Ball (ignore start of game, half, etc)
"""
def isEndOfPossession(row):
    # Is turnover?
    return is_turnover(row) or is_last_free_throw_made(row)


possessions = []

pbp_list =  list(play_by_play.iterrows())
parse_possession(pbp_list)





