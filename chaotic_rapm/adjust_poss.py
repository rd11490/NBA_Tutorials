import pandas as pd

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def change_row(row):
    if row['points'] == 3:
       return  0.0
    else:
        return 3.0

def change_possessions(group, n):

    sample = group[group['threePtAttempts'] > 0].sample(n)

    rows = group.loc[sample.index, :]
    new_points = rows.apply(change_row, axis=1)

    group.loc[sample.index, 'points'] = new_points
    return group



for i in range(0, 10):
    print(i)
    data = pd.read_csv('data/possessions_19_20.csv')

    data = data.groupby(by='gameId').apply(change_possessions, n=i)

    print(data['points'].sum())

    data.to_csv('data/adjusted_possessions/adjusted_{}_possessions_per_game_19_20.csv'.format(i), index=False)









