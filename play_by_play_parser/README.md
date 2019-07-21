## Parsing Play by Play:

### Notes
We will use the data we gathered in the [Players on Court Tutorial](../players_on_court) to determine which players
are on the court for any given event.

We will also use what we learned in the [Analyze Play By Play Data Tutorial](../analyze_play_by_play) to help seperate out possessions.

### What Constitutes a Possession?
A possessions ends every time one of the follow events happen:

1. A made field goal
    - Free throws after an And-1 count to the previous possession
2. A defensive rebound
3. A turnover
4. A made final free throw
    - If a substitution occurs during the free throws, I count the points towards the the players on the court when the freethrows started
    - If a substitution occurs during the free throws and then an offensive rebound occurs I start a new possession



### Code

#### play_by_play_utils.py
We will use a separate file for utility functions so that we don't clutter our
main script.

The first thing we will do is define some constants. This is so that we don't have to
keep using raw strings for column names.

```
event_type = 'EVENTMSGTYPE'
event_subtype = 'EVENTMSGACTIONTYPE'
home_description = 'HOMEDESCRIPTION'
neutral_description = 'NEUTRALDESCRIPTION'
away_description = 'VISITORDESCRIPTION'
period_column = 'PERIOD'
game_clock = 'PCTIMESTRING'
time_elapsed = 'TIME_ELAPSED'
time_elapsed_period = 'TIME_ELAPSED_PERIOD'
```


We will also define some basic functions for determining play type.
```
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
```

We will also define some methods for working with freethrows

```

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
```