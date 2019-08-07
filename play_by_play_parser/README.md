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


### Code

#### play_by_play_utils.py
We will use a separate file for utility functions so that we don't clutter our
main script.

We need to import math because we need to check columns for NaN
```
import math
```

The first thing we will do is define some constants. This is so that we don't have to
keep using raw strings for column names.
```
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
There is no way to tell if a shot is a make or a miss with out checking
the description. We will write a utility function to do just that.
```
def is_miss(row):
    miss = False
    if row[home_description]:
        miss = miss or 'miss' in row[home_description].lower()
    if row[away_description]:
        miss = miss or 'miss' in row[away_description].lower()
    return miss

```
We will also need some functions to determine different foul types
```

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


```
Determine team rebounds and defensive vs offensive rebounds. In order to
tell if a rebound is offensive or defensive we need to go backwards to find
the shot associated with it and check the team of the shooter and the team of the rebounder
```
"""
eventActionType Types: Rebounds

Rebound Types
0 - Player Rebound
1 - Team Rebound*
Not always labeled properly
"""
def is_team_rebound(row):
    return is_rebound(row) and (row[event_subtype] == 1 or math.isnan(row['PLAYER1_TEAM_ID']))


def is_defensive_rebound(ind, row, rows):
    if not is_rebound(row):
        return False
    shot = extract_missed_shot_for_rebound(ind, rows)
    if is_team_rebound(row):
        return shot['PLAYER1_TEAM_ID'] != row['PLAYER1_ID']
    else:
        return shot['PLAYER1_TEAM_ID'] != row['PLAYER1_TEAM_ID']

def extract_missed_shot_for_rebound(ind, rows):
    subset_of_rows = rows[max(0, ind - 10): ind]
    subset_of_rows.reverse()
    for r in subset_of_rows:
        if is_miss(r[1]) or is_missed_free_throw(r[1]):
            return r[1]
    return subset_of_rows[-1][1]
```

Some simple utility functions for checking freethrow type.
Like with rebounds, we have no way of determining if a freethrow is the
result of an And-1 with out going back and looking at the foul that
resulted in the free throw as well as the shot that occurred before the foul
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
    subset_of_rows = rows[max(0, ind - 10): ind]
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

```
Finally we need to check to see how many points a shot if worth. In order to
do this we need to check the description to see if it is a 2pt shot or a
3pt shot.
```

def is_three(row):
    three = False
    if row[home_description]:
        three = three or '3PT' in row[home_description]
    if row[away_description]:
        three = three or '3PT' in row[away_description]
    return three

def is_team_turnover(row):
    return is_turnover(row) and (is_5_second_violation(row) or is_8_second_violation(row) or is_shot_clock_violation(row) or is_too_many_players_violation(row))

def is_5_second_violation(row):
    return is_turnover(row) and row[event_subtype] == 9

def is_8_second_violation(row):
    return is_turnover(row) and row[event_subtype] == 10

def is_shot_clock_violation(row):
    return is_turnover(row) and row[event_subtype] == 11

def is_too_many_players_violation(row):
    return is_turnover(row) and row[event_subtype] == 44
```

#### parse_play_by_play.py

The play by play parser script.

We start off with importing os for relative file pathing, pandas as
always and the play_by_play_utils file we wrote above.

We will also set the pandas display options for easier viewing
```
# Import os for relative pathing to data
import os
import pandas as pd
# Import our play by play utils file
from play_by_play_parser.play_by_play_utils import *

# Set columns and width for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

```

Select the same game ID you used to download the play_by_play and
players on court data
```
# Select a game ID
game_id = '0041700404'
```

Generate the paths for the input play by play data, players on court data,
and output data
```
# determine the directory that this file resides in
dirname = os.path.dirname(__file__)

# generate file path for play by play and players on court data
input_play_by_play = os.path.join(dirname, './data/{}_pbp.csv'.format(game_id))
input_players_on_court = os.path.join(dirname, './data/{}_players_at_period.csv'.format(game_id))
output_path = os.path.join(dirname, './data/{}_possessions.csv'.format(game_id))
```

Read the play by play data into a dataframe, fill NaNs with empty strings
in the description columns
```
# Read in play by play and fill null description columsn with empty string
play_by_play = pd.read_csv(input_play_by_play, index_col=False)
play_by_play[home_description] = play_by_play[home_description].fillna("")
play_by_play[neutral_description] = play_by_play[home_description].fillna("")
play_by_play[away_description] = play_by_play[away_description].fillna("")
```

Calculate how many seconds have elapsed in the period and in the game
and add it to each event.
```
# We will need to know the game clock at each event later on. Let's take the game clock string (7:34) and convert it into seconds elapsed
def parse_time_elapsed(time_str, period):
    # Maximum minutes in a period is 12 unless overtime
    max_minutes = 12 if period < 5 else 5
    # Split string on :
    [minutes, sec] = time_str.split(':')
    # extract minutes and seconds
    minutes = int(minutes)
    sec = int(sec)

    # 7:34 (4 minutes 26 seconds have passed) -> 12 - 7 -> 5, need to subtract an extra minute.
    min_elapsed = max_minutes - minutes - 1
    sec_elapsed = 60 - sec

    return (min_elapsed * 60) + sec_elapsed

# We will also need to calculate the total time elapsed, not just the time elapsed in the period
def calculate_time_elapsed(row):
    # Caclulate time elapsed in the period
    time_in_period = calculate_time_elapsed_period(row)
    period = row[period_column]
    # Calculate total time elapsed up to the start of the current period
    if period > 4:
        return (12 * 60 * 4) + ((period - 5) * 5 * 60) + time_in_period
    else:
        return ((period - 1) * 12 * 60) + time_in_period

# method for calculating time elapsed in a period from a play by play event row
def calculate_time_elapsed_period(row):
    return parse_time_elapsed(row[game_clock], row[period_column])

# Apply the methods for calculating time to add the columns to the dataframe
play_by_play[time_elapsed] = play_by_play.apply(calculate_time_elapsed, axis=1)
play_by_play[time_elapsed_period] = play_by_play.apply(calculate_time_elapsed_period, axis=1)

```

Read in our players at the start of each period file as a dataframe
```

# Read the players at the start of each period
players_at_start_of_period = pd.read_csv(input_players_on_court)
```
This file has 5 columns: TEAM_ID_1,TEAM_1_PLAYERS,TEAM_ID_2,TEAM_2_PLAYERS,PERIOD
where TEAM_1_PLAYERS and TEAM_2_PLAYERS are strings in the form of
"[p1, p2, p3, p4, p5]".
We need to split those string columns out into arrays of player ids.
```
# Players at the start of each period are stored as an string in the dataframe column
# We need to parse out that string into an array of player Ids
def split_row(list_str):
    return [x.replace('[', '').replace(']', '').strip() for x in list_str.split(',')]
```

We need to keep track of substitutions as they happen.
To do this we will maintain a map of players on the court at a given moment
It will be structured as period -> team_id -> players array
```

sub_map = {}
# Pre-populate the map with the players at the start of each period
for row in players_at_start_of_period.iterrows():
    sub_map[row[1]['PERIOD']] = {row[1]['TEAM_ID_1']: split_row(row[1]['TEAM_1_PLAYERS']),
                                 row[1]['TEAM_ID_2']: split_row(row[1]['TEAM_2_PLAYERS'])}
```
players on the court need to be updated after every substitution
Once we have subbed the players in/out in our sub map we can add those
players to the current event row so that
Each event has all of the players involved with the event included
```
def update_subs(row):
    period = row['PERIOD']
    # If the event is a substitution we need to sub out the players on the court
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
        row['TEAM{}_ID'.format(i + 1)] = k
        row['TEAM{}_PLAYER1'.format(i + 1)] = sub_map[period][k][0]
        row['TEAM{}_PLAYER2'.format(i + 1)] = sub_map[period][k][1]
        row['TEAM{}_PLAYER3'.format(i + 1)] = sub_map[period][k][2]
        row['TEAM{}_PLAYER4'.format(i + 1)] = sub_map[period][k][3]
        row['TEAM{}_PLAYER5'.format(i + 1)] = sub_map[period][k][4]
```

We will need to define a function that tells us if an event signals the end of a possession.
as we stated above a possession is ended by:
1. A made field goal
    - Free throws after an And-1 count to the previous possession
2. A defensive rebound
3. A turnover
4. A made final free throw
```
def is_end_of_possession(ind, row, rows):
    return is_turnover(row) or (is_last_free_throw_made(ind, row, rows)) or is_defensive_rebound(ind, row, rows) or \
           is_make_and_not_and_1(ind, row, rows) or is_end_of_period(row)

```

Now we have all the pieces in place to seperate events into possessions.
We will iterate over every event row in the play by play and update substitutions,
add the event to the current possession (unless it is a sub or end of period event)
and then check if the event is an end of possession event. If it is an end of possession
event we will break the possession off and add it to our list of possessions.
```
def parse_possession(rows):
    possessions = []
    current_posession = []
    for ind, row in rows:
        # update our subs
        update_subs(row)
        # No need to include subs or end of period events in our possession list
        if not is_substitution(row) and not is_end_of_period(row):
            current_posession.append(row)
        # if the current event is the last event of a possession, add the current possession to our list of possessions
        # and start a new possession
        if is_end_of_possession(ind, row, rows):
            # No need to add empty end of period possessions
            if len(current_posession) > 0:
                possessions.append(current_posession)
            current_posession = []
    return possessions



```
Convert dataframe into a list of rows (I know there is a better way to do this,
but this is the first thing I thought of). and apply our parse possessions method to the list.
```
pbp_rows = list(play_by_play.iterrows())
possessions = parse_possession(pbp_rows)
```

We can print out the first few possession groupings to see if they look correct
```
# Print out the first couple of possessions so that you can see how the parser split them.
for possession in possessions[:4]:
    print('POSSESSION')
    for p in possession:
        print(p[home_description], p[neutral_description], p[away_description])
    print('\n')
```
Results:
```
POSSESSION

Jump Ball Thompson vs. McGee: Tip to Curry Jump Ball Thompson vs. McGee: Tip to Curry
  MISS McGee 2' Reverse Layup
  Curry REBOUND (Off:1 Def:0)
  Curry 1' Tip Layup Shot (2 PTS)


POSSESSION
MISS Love 26' 3PT Jump Shot MISS Love 26' 3PT Jump Shot
  Warriors Rebound


POSSESSION
  MISS Green 24' 3PT Jump Shot
Love REBOUND (Off:0 Def:1) Love REBOUND (Off:0 Def:1)


POSSESSION
Smith 25' 3PT Jump Shot (3 PTS) (James 1 AST) Smith 25' 3PT Jump Shot (3 PTS) (James 1 AST)
```
Now that we have our events seperated out by possessions we need to aggregate those events
and convert them into some sort of possession structure.

To do this we need a method for extracting points scored by each team from the list of events
```
# We need to count up each teams points from a possession
def count_points(possession):
    # points will be a map where the key is the team id and the value is the number of points scored in that possesion
    points = {}
    for p in possession:
        if is_made_shot(p) or (not is_miss(p) and is_free_throw(p)):
            if p['PLAYER1_TEAM_ID'] in points:
                points[p['PLAYER1_TEAM_ID']] += extract_points(p)
            else:
                points[p['PLAYER1_TEAM_ID']] = extract_points(p)
    return points

# We need to know how many points each shot is worth:
def extract_points(p):
    if is_free_throw(p) and not is_miss(p):
        return 1
    elif is_made_shot(p) and is_three(p):
        return 3
    elif is_made_shot(p) and not is_three(p):
        return 2
    else:
        return 0

```
We need to determine which team has possession of the ball based on how the possession ended

If the possession ended with a made shot or free throw then we can determine that the team of the player
who made the shot was the team with possession of the ball

If the possession ended with a rebound then we can determine that the team that did not get the rebound is
the team that had possession of the ball (ORBDs do not end possessions)

If the possession ended with a turnover then we can determine that the team that committed the turnover is
the team that had possession of the ball

If the possession ended due to the end of a period, we probably have some other random event as the last event
We can assume that the team1 id of that event is the team with the ball
improvements can be made by handling each event type individually
```
def determine_possession_team(p, team1, team2):
    if is_made_shot(p) or is_free_throw(p):
        return str(int(p['PLAYER1_TEAM_ID']))
    elif is_rebound(p):
        if is_team_rebound(p):
            if p['PLAYER1_ID'] == team1:
                return team2
            else:
                return team1
        else:
            if p['PLAYER1_TEAM_ID'] == team1:
                return team2
            else:
                return team1
    elif is_turnover(p):
        if is_team_turnover(p):
           return str(int(p['PLAYER1_ID']))
        else:
            return str(int(p['PLAYER1_TEAM_ID']))
    else:
        if math.isnan(p['PLAYER1_TEAM_ID']):
            return str(int(p['PLAYER1_ID']))
        else:
            return str(int(p['PLAYER1_TEAM_ID']))

```
Parse out the list of events in a possession into a single possession object
for this tutorial we will only include the players on the court, the game id, period, start and end time of possesion,
points scored by each team, and which team was on offense during the possession.
```
def parse_possession(possession):
    times_of_events = [p[time_elapsed] for p in possession]
    possession_start = min(times_of_events)
    possession_end = max(times_of_events)
    points = count_points(possession)
    game_id = possession[0]['GAME_ID']
    period = possession[0][period_column]

    team1_id = possession[0]['TEAM1_ID']
    team1_player1 = possession[0]['TEAM1_PLAYER1']
    team1_player2 = possession[0]['TEAM1_PLAYER2']
    team1_player3 = possession[0]['TEAM1_PLAYER3']
    team1_player4 = possession[0]['TEAM1_PLAYER4']
    team1_player5 = possession[0]['TEAM1_PLAYER5']
    team1_points = points[team1_id] if team1_id in points else 0

    team2_id = possession[0]['TEAM2_ID']
    team2_player1 = possession[0]['TEAM2_PLAYER1']
    team2_player2 = possession[0]['TEAM2_PLAYER2']
    team2_player3 = possession[0]['TEAM2_PLAYER3']
    team2_player4 = possession[0]['TEAM2_PLAYER4']
    team2_player5 = possession[0]['TEAM2_PLAYER5']
    team2_points = points[team2_id] if team2_id in points else 0

    possession_team = determine_possession_team(possession[-1], team1_id, team2_id)

    return {
        'team1_id': str(team1_id),
        'team1_player1': str(team1_player1),
        'team1_player2': str(team1_player2),
        'team1_player3': str(team1_player3),
        'team1_player4': str(team1_player4),
        'team1_player5': str(team1_player5),
        'team2_id': str(team2_id),
        'team2_player1': str(team2_player1),
        'team2_player2': str(team2_player2),
        'team2_player3': str(team2_player3),
        'team2_player4': str(team2_player4),
        'team2_player5': str(team2_player5),
        'game_id': str(game_id),
        'period': period,
        'possession_start': possession_start,
        'possession_end': possession_end,
        'team1_points': team1_points,
        'team2_points': team2_points,
        'possession_team': str(possession_team)
    }
```

Take our list of possessions and parse them all into a list of objects
then build a DataFrame out of the list of objects and write to a csv
```
# Build a list of parsed possession objects
parsed_possessions = []
for possession in possessions:
    parsed_possessions.append(parse_possession(possession))

# Build a dataframe from the list of parsed possession
df = pd.DataFrame(parsed_possessions)

print(df)
print(df.groupby(by='team1_id')['team1_points'].sum())
print(df.groupby(by='team2_id')['team2_points'].sum())
print(df.groupby(by=['possession_team'])['possession_team'].count())

df.to_csv(output_path, index=False)

      game_id  period  possession_end  possession_start possession_team    team1_id team1_player1 team1_player2 team1_player3 team1_player4 team1_player5  team1_points    team2_id team2_player1 team2_player2 team2_player3 team2_player4 team2_player5  team2_points
0    41700404       1              22                 0      1610612744  1610612744        201142        201580        201939        202691        203110             2  1610612739          2544          2747        201567        201588        202684             0
1    41700404       1              38                36      1610612739  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             0
2    41700404       1              52                48      1610612744  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             0
3    41700404       1              58                58      1610612739  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             3
4    41700404       1              83                83      1610612744  1610612744        201142        201580        201939        202691        203110             2  1610612739          2544          2747        201567        201588        202684             0
5    41700404       1             100                96      1610612739  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             0
6    41700404       1             103               103      1610612744  1610612744        201142        201580        201939        202691        203110             2  1610612739          2544          2747        201567        201588        202684             0
7    41700404       1             117               114      1610612739  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             0
8    41700404       1             127               127      1610612744  1610612744        201142        201580        201939        202691        203110             2  1610612739          2544          2747        201567        201588        202684             0
9    41700404       1             144               132      1610612739  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             0
10   41700404       1             156               156      1610612744  1610612744        201142        201580        201939        202691        203110             2  1610612739          2544          2747        201567        201588        202684             0
11   41700404       1             186               157      1610612739  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             0
12   41700404       1             193               193      1610612744  1610612744        201142        201580        201939        202691        203110             3  1610612739          2544          2747        201567        201588        202684             0
13   41700404       1             216               208      1610612739  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             2
14   41700404       1             235               232      1610612744  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             0
15   41700404       1             252               238      1610612739  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             0
16   41700404       1             266               266      1610612744  1610612744        201142        201580        201939        202691        203110             0  1610612739          2544          2747        201567        201588        202684             0
17   41700404       1             293               278      1610612739  1610612744        201142        201580        201939        203110          2738             0  1610612739          2544          2747        201567        201588        202684             3
18   41700404       1             317               314      1610612744  1610612744        201142        201580        201939        203110          2738             0  1610612739          2544          2747        201567        201588        202684             0
19   41700404       1             322               322      1610612739  1610612744        201142        201580        201939        203110          2738             0  1610612739          2544          2747        201567        201588        202684             3
20   41700404       1             323               323      1610612739  1610612744        201142        201580        201939        203110          2738             0  1610612739          2544          2747        201567        201588        202684             0
21   41700404       1             335               335      1610612744  1610612744        201142        201580        201939        203110          2738             3  1610612739          2544          2747        201567        201588        202684             0
22   41700404       1             350               350      1610612739  1610612744        201142        201580        201939        203110          2738             0  1610612739          2544          2747        201567        201588        202684             0
23   41700404       1             357               357      1610612744  1610612744        201142        201580        201939        203110          2738             3  1610612739          2544          2747        201567        201588        202684             0
24   41700404       1             369               369      1610612739  1610612744        201142        201580        201939        203110          2738             0  1610612739          2544          2747        201567        201588        202684             2
25   41700404       1             378               378      1610612744  1610612744        201142        201580        201939        203110          2738             3  1610612739          2544          2747        201567        201588        202684             0
26   41700404       1             393               390      1610612739  1610612744        201142        201580        201939        203110          2738             0  1610612739          2544          2747        201567        201588        202684             0
27   41700404       1             405               395      1610612744  1610612744        201142        201580        201939        203110          2738             0  1610612739          2544          2747        201567        201588        202684             0
28   41700404       1             413               409      1610612739  1610612744       1628395        201142        201939        203110          2738             0  1610612739          2544          2747        201567        201588        202684             0
29   41700404       1             413               413      1610612744  1610612744       1628395        201142        201939        203110          2738             2  1610612739          2544          2747        201567        201588        202684             0
..        ...     ...             ...               ...             ...         ...           ...           ...           ...           ...           ...           ...         ...           ...           ...           ...           ...           ...           ...
151  41700404       4            2402              2402      1610612744  1610612744        201142        201939        202691        203110          2738             2  1610612739       1626204        201588        203918          2544          2594             0
152  41700404       4            2429              2426      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
153  41700404       4            2437              2434      1610612744  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
154  41700404       4            2451              2439      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
155  41700404       4            2469              2453      1610612744  1610612744        201142        201939        202691        203110          2738             2  1610612739       1626204        201588        203918          2544          2594             0
156  41700404       4            2488              2484      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
157  41700404       4            2501              2495      1610612744  1610612744        201142        201939        202691        203110          2738             3  1610612739       1626204        201588        203918          2544          2594             0
158  41700404       4            2517              2508      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
159  41700404       4            2534              2532      1610612744  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
160  41700404       4            2540              2540      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             2
161  41700404       4            2570              2567      1610612744  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
162  41700404       4            2576              2574      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             1
163  41700404       4            2596              2594      1610612744  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
164  41700404       4            2599              2599      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
165  41700404       4            2617              2613      1610612744  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
166  41700404       4            2631              2625      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739       1626204        201588        203918          2544          2594             0
167  41700404       4            2651              2651      1610612744  1610612744        201142        201939        202691        203110          2738             0  1610612739        101181       1626204       1626224        203918          2594             0
168  41700404       4            2670              2670      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739        101181       1626204       1626224        203918          2594             2
169  41700404       4            2697              2697      1610612744  1610612744        201142        201939        202691        203110          2738             2  1610612739        101181       1626204       1626224        203918          2594             0
170  41700404       4            2709              2706      1610612739  1610612744        201142        201939        202691        203110          2738             0  1610612739        101181       1626204       1626224        203918          2594             0
171  41700404       4            2737              2713      1610612744  1610612744        201142        201939        202691        203110          2738             2  1610612739        101181       1626204       1626224        203918          2594             0
172  41700404       4            2746              2746      1610612739  1610612744       1626172       1627775       1628395        201156          2585             0  1610612739        101181       1626204       1626224        203918          2594             2
173  41700404       4            2760              2760      1610612744  1610612744       1626172       1627775       1628395        201156          2585             0  1610612739        101181       1626204       1626224        203918          2594             0
174  41700404       4            2770              2767      1610612739  1610612744       1626172       1627775       1628395        201156          2585             0  1610612739        101181       1626204       1626224        203918          2594             0
175  41700404       4            2780              2780      1610612744  1610612744       1626172       1627775       1628395        201156          2585             2  1610612739        101181       1626204       1626224        203918          2594             0
176  41700404       4            2795              2795      1610612739  1610612744       1626172       1627775       1628395        201156          2585             0  1610612739        101181       1626204       1626224       1627790        203918             2
177  41700404       4            2820              2813      1610612744  1610612744       1626172       1627775       1628395        201156          2585             0  1610612739        101181       1626204       1626224       1627790        203918             0
178  41700404       4            2840              2826      1610612739  1610612744       1626172       1627775       1628395        201156          2585             0  1610612739        101181       1626204       1626224       1627790        203918             2
179  41700404       4            2864              2863      1610612744  1610612744       1626172       1627775       1628395        201156          2585             0  1610612739        101181       1626204       1626224       1627790        203918             0
180  41700404       4            2877              2871      1610612739  1610612744       1626172       1627775       1628395        201156          2585             0  1610612739        101181       1626204       1626224       1627790        203918             0

[181 rows x 19 columns]
team1_id
1610612744    108
Name: team1_points, dtype: int64
team2_id
1610612739    85
Name: team2_points, dtype: int64
possession_team
1610612739    92
1610612744    89
Name: possession_team, dtype: int64


```

#### Further Work:
The parser we wrote in this tutorial does not handle the case where a
substitution happens between freethrows and then an offensive rebound
occurs after the last free-throw. It likely struggles with some other
corner cases that are not present in the sample game
(older seasons have issues with the ordering of missed shots, rebounds and putbacks).