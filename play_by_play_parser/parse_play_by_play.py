# Import os for relative pathing to data
import os
import pandas as pd
# Import our play by play utils file
from play_by_play_parser.play_by_play_utils import *

# Set columns and width for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Select a game ID
game_id = '0011300115'

# determine the directory that this file resides in
dirname = os.path.dirname(__file__)

# generate file path for play by play and players on court data
input_play_by_play = os.path.join(dirname, './data/{}_pbp.csv'.format(game_id))
input_players_on_court = os.path.join(dirname, './data/{}_players_at_period.csv'.format(game_id))
output_path = os.path.join(dirname, './data/{}_possessions.csv'.format(game_id))


# Read in play by play and fill null description columsn with empty string
play_by_play = pd.read_csv(input_play_by_play, index_col=False)
play_by_play[home_description] = play_by_play[home_description].fillna("")
play_by_play[neutral_description] = play_by_play[home_description].fillna("")
play_by_play[away_description] = play_by_play[away_description].fillna("")


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


# Read the players at the start of each period
players_at_start_of_period = pd.read_csv(input_players_on_court)

# Players at the start of each period are stored as an string in the dataframe column
# We need to parse out that string into an array of player Ids
def split_row(list_str):
    return [x.replace('[', '').replace(']', '').strip() for x in list_str.split(',')]

# We need to keep track of substitutions as they happen. To do this we will maintain a map of players on the court at a given moment
# It will be structured as period -> team_id -> players array
sub_map = {}
# Pre-populate the map with the players at the start of each period
for row in players_at_start_of_period.iterrows():
    sub_map[row[1][period_column]] = {row[1]['TEAM_ID_1']: split_row(row[1]['TEAM_1_PLAYERS']),
                                 row[1]['TEAM_ID_2']: split_row(row[1]['TEAM_2_PLAYERS'])}

# players on the court need to be updated after every substitution
def update_subs(row):
    period = row[period_column]
    # If the event is a substitution we need to sub out the players on the court
    if is_substitution(row):
        team_id = row[player1_team_id]
        player_in = str(row[player2_id])
        player_out = str(row[player1_id])
        players = sub_map[period][team_id]
        players_index = players.index(player_out)
        players[players_index] = player_in
        players.sort()
        sub_map[period][team_id] = players
    # Once we have subbed the players in/out in our sub map we can add those players to the current event row so that
    # Each event has all of the players involved with the event included
    for i, k in enumerate(sub_map[period].keys()):
        row['TEAM{}_ID'.format(i + 1)] = k
        row['TEAM{}_PLAYER1'.format(i + 1)] = sub_map[period][k][0]
        row['TEAM{}_PLAYER2'.format(i + 1)] = sub_map[period][k][1]
        row['TEAM{}_PLAYER3'.format(i + 1)] = sub_map[period][k][2]
        row['TEAM{}_PLAYER4'.format(i + 1)] = sub_map[period][k][3]
        row['TEAM{}_PLAYER5'.format(i + 1)] = sub_map[period][k][4]

"""
What ends a possession?


1. Made Shot (Need to account for And-1s)
2. Defensive Rebound
3. Turnover
4. Last made free throw  (Ignore FT 1 of 1 on away from play fouls with no made shot)
"""
def is_end_of_possession(ind, row, rows):
    return is_turnover(row) or (is_last_free_throw_made(ind, row, rows)) or is_defensive_rebound(ind, row, rows) or \
           is_make_and_not_and_1(ind, row, rows) or is_end_of_period(row)


# The main function of our tutorial, the method to group events by possession
def parse_possession(rows):
    # we will have a list of possessions and each possession will be a list of events
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




# convert dataframe into a list of rows. I know there is a better way to do this,
# but this is the first thing I thought of.
pbp_rows = list(play_by_play.iterrows())
possessions = parse_possession(pbp_rows)


# Print out the first couple of possessions so that you can see how the parser split them.
for possession in possessions[:4]:
    print('POSSESSION')
    for p in possession:
        print(p[period_column], p[time_elapsed], p[home_description], p[neutral_description], p[away_description])
    print('\n')


# We need to count up each teams points from a possession
def count_points(possession):
    # points will be a map where the key is the team id and the value is the number of points scored in that possesion
    points = {}
    for p in possession:
        if is_made_shot(p) or (not is_miss(p) and is_free_throw(p)):
            if p[player1_team_id] in points:
                points[p[player1_team_id]] += extract_points(p)
            else:
                points[p[player1_team_id]] = extract_points(p)
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

# We need to determine which team has possession of the ball based on how the possession ended

# If the possession ended with a made shot or free throw then we can determine that the team of the player
# who made the shot was the team with possession of the ball
#
# If the possession ended with a rebound then we can determine that the team that did not get the rebound is
# the team that had possession of the ball (ORBDs do not end possessions)
#
# If the possession ended with a turnover then we can determine that the team that committed the turnover is
# the team that had possession of the ball
#
# If the possession ended due to the end of a period, we probably have some other random event as the last event
# We can assume that the team1 id of that event is the team with the ball
# improvements can be made by handling each event type individually
def determine_possession_team(p, team1, team2):
    if is_made_shot(p) or is_free_throw(p):
        return str(int(p[player1_team_id]))
    elif is_rebound(p):
        if is_team_rebound(p):
            if p[player1_id] == team1:
                return team2
            else:
                return team1
        else:
            if p[player1_team_id] == team1:
                return team2
            else:
                return team1
    elif is_turnover(p):
        if is_team_turnover(p):
           return str(int(p[player1_id]))
        else:
            return str(int(p[player1_team_id]))
    else:
        if math.isnan(p[player1_team_id]):
            return str(int(p[player1_id]))
        else:
            return str(int(p[player1_team_id]))


# Parse out the list of events in a possession into a single possession object
# for this tutorial we will only include the players on the court, the game id, period, start and end time of possesion,
# points scored by each team, and which team was on offense during the possession.
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
