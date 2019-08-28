import math
# Constants
event_type = 'EVENTMSGTYPE'
event_subtype = 'EVENTMSGACTIONTYPE'
home_description = 'HOMEDESCRIPTION'
neutral_description = 'NEUTRALDESCRIPTION'
away_description = 'VISITORDESCRIPTION'
period_column = 'PERIOD'
game_clock = 'PCTIMESTRING'
time_elapsed = 'TIME_ELAPSED'
time_elapsed_period = 'TIME_ELAPSED_PERIOD'
player1_id = 'PLAYER1_ID'
player1_team_id = 'PLAYER1_TEAM_ID'
player2_id = 'PLAYER2_ID'


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
    return row[event_type] == 1


def is_missed_shot(row):
    return row[event_type] == 2


def is_free_throw(row):
    return row[event_type] == 3


def is_rebound(row):
    return row[event_type] == 4


def is_turnover(row):
    return row[event_type] == 5


def is_foul(row):
    return row[event_type] == 6


def is_violation(row):
    return row[event_type] == 7


def is_substitution(row):
    return row[event_type] == 8


def is_timeout(row):
    return row[event_type] == 9


def is_jump_ball(row):
    return row[event_type] == 10


def is_ejection(row):
    return row[event_type] == 11


def is_start_of_period(row):
    return row[event_type] == 12


def is_end_of_period(row):
    return row[event_type] == 13


def is_miss(row):
    miss = False
    if row[home_description]:
        miss = miss or 'miss' in row[home_description].lower()
    if row[away_description]:
        miss = miss or 'miss' in row[away_description].lower()
    return miss


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


def is_shooting_foul(row):
    return is_foul(row) and row[event_subtype] == 2


def is_away_from_play_foul(row):
    return is_foul(row) and row[event_subtype] == 6


def is_inbound_foul(row):
    return is_foul(row) and row[event_subtype] == 5


def is_loose_ball_foul(row):
    return is_foul(row) and row[event_subtype] == 3

"""
eventActionType Types: Rebounds

Rebound Types
0 - Player Rebound
1 - Team Rebound*
Not always labeled properly
"""
def is_team_rebound(row):
    return is_rebound(row) and (row[event_subtype] == 1 or math.isnan(row[player1_team_id]))


def is_defensive_rebound(ind, row, rows):
    if not is_rebound(row):
        return False
    shot = extract_missed_shot_for_rebound(ind, rows)
    if is_team_rebound(row):
        return shot[player1_team_id] != row[player1_id]
    else:
        return shot[player1_team_id] != row[player1_team_id]

def extract_missed_shot_for_rebound(ind, rows):
    subset_of_rows = rows[max(0, ind - 10): ind]
    subset_of_rows.reverse()
    for r in subset_of_rows:
        if is_miss(r[1]) or is_missed_free_throw(r[1]):
            return r[1]
    return subset_of_rows[-1][1]

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


def is_missed_free_throw(row):
    return is_free_throw(row) and is_miss(row)


def is_1_of_1(row):
    return is_free_throw(row) and row[event_subtype] == 10


def is_2_of_2(row):
    return is_free_throw(row) and row[event_subtype] == 12


def is_3_of_3(row):
    return is_free_throw(row) and row[event_subtype] == 15


def is_technical(row):
    return is_free_throw(row) and row[event_subtype] == 13


def is_last_free_throw(row):
    return is_1_of_1(row) or is_last_multi_free_throw(row)


def is_last_multi_free_throw(row):
    return is_2_of_2(row) or is_3_of_3(row)


def is_last_free_throw_made(ind, row, rows):
    if not is_free_throw(row):
        return False
    foul = extract_foul_for_last_freethrow(ind, row, rows)
    return (is_last_multi_free_throw(row) or (
        is_1_of_1(row) and not is_away_from_play_foul(foul) and not is_loose_ball_foul(foul) and not is_inbound_foul(
            foul))) and not is_miss(row)


def extract_foul_for_last_freethrow(ind, row, rows):
    # Check the last 20 events to find the last foul before the free-throw
    subset_of_rows = rows[max(0, ind - 20): ind]
    subset_of_rows.reverse()
    for r in subset_of_rows:
        if is_foul(r[1]):
            return r[1]
    print(ind)
    print(row)
    return subset_of_rows[0][1]


def is_and_1(ind, row, rows):
    if not is_made_shot(row):
        return False
    # check next 20 events after the make
    subset_of_rows = rows[ind + 1: min(ind + 20, len(rows))]
    cnt = 0

    for sub_ind, r in subset_of_rows:
        # We are looking for fouls or 1 of 1 free throws that happen within 10 seconds of the made shot.
        # We also need to make sure those 1 of 1s are the result of a different type of foul that results in 1 FT.
        # If we have both a foul and a 1 of 1 ft that meet these conditions we can safely assume this shot resulted in
        # an And-1
        if (is_foul(r) or is_1_of_1(r)) and row[time_elapsed] <= r[time_elapsed] <= row[time_elapsed] + 10:
            if is_foul(r) and not is_technical(r) and not is_loose_ball_foul(r) and not is_inbound_foul(r) and r[
                player2_id] == row[player1_id]:
                cnt += 1
            elif is_1_of_1(r) and r[player1_id] == row[player1_id]:
                cnt += 1
    return cnt == 2


def is_make_and_not_and_1(ind, row, rows):
    return is_made_shot(row) and not is_and_1(ind, row, rows)

def is_three(row):
    three = False
    if row[home_description]:
        three = three or '3PT' in row[home_description]
    if row[away_description]:
        three = three or '3PT' in row[away_description]
    return three

def is_team_turnover(row):
    return is_turnover(row) and (is_5_second_violation(row) or is_8_second_violation(row) or is_shot_clock_violation(row) or is_too_many_players_violation(row) or no_player_listed(row))

def is_5_second_violation(row):
    return is_turnover(row) and row[event_subtype] == 9

def is_8_second_violation(row):
    return is_turnover(row) and row[event_subtype] == 10

def is_shot_clock_violation(row):
    return is_turnover(row) and row[event_subtype] == 11

def no_player_listed(row):
    return math.isnan(row[player1_team_id])

def is_too_many_players_violation(row):
    return is_turnover(row) and row[event_subtype] == 44
