import random

import pandas as pd

shots = 90
ot_shots = 10

##########
# Team 1 #
##########
team1 = {
    '2pt rate': .80,
    '3pt rate': .20,
    '2pt%': .50,
    '3pt%': .33333,
    'orbd': .225
}

##########
# Team 2 #
##########
team2 = {
    '2pt rate': .50,
    '3pt rate': .50,
    '2pt%': .50,
    '3pt%': .33333,
    'orbd': .225
}

def points(team):
    roll_shot_type = random.random()
    roll_make = random.random()

    if roll_shot_type <= team['2pt rate']:
        if roll_make <= team['2pt%']:
            return 2
    else:
        if roll_make <= team['3pt%']:
            return 3

    roll_orbd = random.random()

    if roll_orbd < team['orbd']:
        return points(team)

    return 0


def play_game(shots_to_take):
    t1_points_in_game = 0
    t2_points_in_game = 0
    for shot in range(shots_to_take):
        t1_points_in_game += points(team1)
        t2_points_in_game += points(team2)
    return t1_points_in_game, t2_points_in_game


results = []

for game in range(1000000):
    t1_points, t2_points = play_game(shots)

    while t1_points == t2_points:
        t1_new, t2_new = play_game(ot_shots)
        t1_points += t1_new
        t2_points += t2_new

    result = {
        'team1': t1_points,
        'team2': t2_points,
        'game': game,
        'team1_win': t1_points > t2_points,
        'team2_win': t2_points > t1_points,
    }
    results.append(result)

frame = pd.DataFrame(results)

team1_wins = frame['team1_win'].sum() / frame.shape[0]
team2_wins = frame['team2_win'].sum() / frame.shape[0]

print('Team 1 wins {0:.2f}% of the time'.format(team1_wins * 100))
print('Team 2 wins {0:.2f}% of the time'.format(team2_wins * 100))
