import pandas as pd

# Set display options for pandas for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

rapm = pd.read_csv('data/rapm_adjusted.csv')


abs_player_change = []


def calculate_change(player):
    print(player)
    base = player['RAPM'].values[0]
    player['Abs Change RAPM'] = abs(player['RAPM']-base)
    return player

rapm = rapm.groupby(by='playerId').apply(calculate_change)
mean_change = rapm.groupby(by='adjustedPossessions')['Abs Change RAPM'].describe()
print(mean_change)

print(rapm.describe())