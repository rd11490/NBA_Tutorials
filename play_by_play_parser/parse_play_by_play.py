import pandas as pd
import os
from play_by_play_parser.play_by_play_utils import *
import datetime

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

play_by_play = play_by_play[play_by_play[period_column] == 1]


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
    period = row['PERIOD']
    if is_substitution(row):
        team_id = row['PLAYER1_TEAM_ID']
        player_in = str(row['PLAYER2_ID'])
        player_out = str(row['PLAYER1_ID'])
        players = sub_map[period][team_id]
        players_index = players.index(player_out)
        players[players_index] = player_in
        players.sort()
        sub_map[period][team_id] = players
    for i, k in enumerate(sub_map[period].keys()):
        row['TEAM{}_ID'.format(i+1)] =  k
        row['TEAM{}_PLAYER1'.format(i+1)] = sub_map[period][k][0]
        row['TEAM{}_PLAYER2'.format(i+1)] = sub_map[period][k][1]
        row['TEAM{}_PLAYER3'.format(i+1)] = sub_map[period][k][2]
        row['TEAM{}_PLAYER4'.format(i+1)] = sub_map[period][k][3]
        row['TEAM{}_PLAYER5'.format(i+1)] = sub_map[period][k][4]


def parse_possession(rows):
    possessions = []
    current_posession = []
    for ind, row in rows:
        update_subs(row)
        if not is_substitution(row):
            current_posession.append(row)
        if isEndOfPossession(ind, row, rows):
            possessions.append(current_posession)
            current_posession = []
    return possessions


"""
What ends a possession?


1. Made Shot (Need to account for And-1s)
2. Defensive Rebound
3. Turnover
4. Last made free throw  (Ignore FT 1 of 1 on away from play fouls with no made shot)
"""
def isEndOfPossession(ind, row, rows):
    return is_turnover(row) or (is_last_free_throw_made(ind, row, rows)) or is_defensive_rebound(ind, row, rows) or is_make_and_not_and_1(ind, row, rows)

start = datetime.datetime.now()
pbp_rows = list(play_by_play.iterrows())
possessions = parse_possession(pbp_rows)
end = datetime.datetime.now()
print(end-start)

for possession in possessions:
    print('\n\n')
    print("POSSESSION:")
    for p in possession:
        print(p[time_elapsed], p[home_description], p[neutral_description], p[away_description])




