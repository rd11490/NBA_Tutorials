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

def is_miss(row):
    miss = False
    if row[home_description]:
        miss = miss or 'miss' in row[home_description].lower()
    if row[away_description]:
        miss = miss or 'miss' in row[away_description].lower()
    return miss




def is_missed_free_throw(row):
    return is_free_throw(row) and ()

def is_1_of_1(row):
    return is_free_throw(row) and row[event_subtype] == 13


def is_2_of_2(row):
    return is_free_throw(row) and row[event_subtype] == 13


def is_3_of_3(row):
    return is_free_throw(row) and row[event_subtype] == 13


def is_technical(row):
    return is_free_throw(row) and row[event_subtype] == 13


def is_last_free_throw(row):
    return is_1_of_1(row) or is_2_of_2(row) or is_3_of_3(row)


def is_last_free_throw_made(row):
    return is_last_free_throw(row) and 'MISS' not in row[home_description] and 'MISS' not in row[away_description]