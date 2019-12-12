import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


possession = pd.read_csv('possession_2019-20.csv')

offensive_possessions = possession[['offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id',  'points', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']]

o_possession_counts = offensive_possessions.groupby(by=['offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id']).sum().reset_index()

defensive_possessions = possession[['defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id', 'defensePlayer4Id', 'defensePlayer5Id',  'points', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']]

d_possession_counts = defensive_possessions.groupby(by=['defensePlayer1Id','defensePlayer2Id', 'defensePlayer3Id', 'defensePlayer4Id', 'defensePlayer5Id']).sum().reset_index()

average_o = o_possession_counts[[ 'points', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']].mean()
average_d = d_possession_counts[[ 'points', 'fieldGoalAttempts', 'fieldGoals', 'threePtAttempts', 'threePtMade', 'freeThrowAttempts', 'freeThrowsMade', 'possessions', 'seconds']].mean()

print(average_o)
print(average_d)

avg_fga = average_o['fieldGoalAttempts'] / average_o['possessions']
avg_ppp = average_o['points'] / average_o['possessions']


rows = []
for i in range(0, 250):

    points = i * avg_ppp
    fga = i * avg_fga

    new_poss = i + 1

    body = {
        'POSS': new_poss,
        'MISS': points,
        'MAKE2': (points + 2),
        'MAKE3': (points + 3)
    }

    rows.append(body)

frame = pd.DataFrame(rows)
frame['RTG_MISS'] = 100 * frame['MISS'] / frame['POSS']
frame['RTG_MAKE2'] = 100 * frame['MAKE2'] / frame['POSS']
frame['RTG_MAKE3'] = 100 * frame['MAKE3'] / frame['POSS']

frame['NET_RTG_O_MISS_D_MAKE2'] = frame['RTG_MISS'] - frame['RTG_MAKE2']
frame['NET_RTG_O_MISS_D_MAKE3'] = frame['RTG_MISS'] - frame['RTG_MAKE3']

frame['NET_RTG_O_MAKE2_D_MISS'] = frame['RTG_MAKE2'] - frame['RTG_MISS']
frame['NET_RTG_O_MAKE2_D_MAKE3'] = frame['RTG_MAKE2'] - frame['RTG_MAKE3']

frame['NET_RTG_O_MAKE3_D_MISS'] = frame['RTG_MAKE3'] - frame['RTG_MISS']
frame['NET_RTG_O_MAKE3_D_MAKE2'] = frame['RTG_MAKE3'] - frame['RTG_MAKE2']

print(frame.head(20))

fig = plt.figure()

plt.plot(frame['POSS'], frame['NET_RTG_O_MISS_D_MAKE2'], label='Score 0, Allow 2')
plt.plot(frame['POSS'], frame['NET_RTG_O_MISS_D_MAKE3'], label='Score 0, Allow 3')

plt.plot(frame['POSS'], frame['NET_RTG_O_MAKE2_D_MISS'], label='Score 2, Allow 0')
plt.plot(frame['POSS'], frame['NET_RTG_O_MAKE2_D_MAKE3'], label='Score 2, Allow 3')

plt.plot(frame['POSS'], frame['NET_RTG_O_MAKE3_D_MISS'], label='Score 3, Allow 0')
plt.plot(frame['POSS'], frame['NET_RTG_O_MAKE3_D_MAKE2'], label='Score 3, Allow 2')

plt.legend()
plt.xlabel('Possessions')
plt.ylabel('Net Rating')

plt.ylim((-10,10))
plt.grid(axis='y')
plt.title('Impact of 1 Possession Swing on Net Rating')

fig2 = plt.figure()

plt.plot(frame['POSS'], frame['NET_RTG_O_MISS_D_MAKE2'], label='Score 0, Allow 2')
plt.plot(frame['POSS'], frame['NET_RTG_O_MISS_D_MAKE3'], label='Score 0, Allow 3')

plt.plot(frame['POSS'], frame['NET_RTG_O_MAKE2_D_MISS'], label='Score 2, Allow 0')
plt.plot(frame['POSS'], frame['NET_RTG_O_MAKE2_D_MAKE3'], label='Score 2, Allow 3')

plt.plot(frame['POSS'], frame['NET_RTG_O_MAKE3_D_MISS'], label='Score 3, Allow 0')
plt.plot(frame['POSS'], frame['NET_RTG_O_MAKE3_D_MAKE2'], label='Score 3, Allow 2')

plt.legend()
plt.xlabel('Possessions')
plt.ylabel('Net Rating')
plt.ylim((-50,50))
plt.grid(axis='y')
plt.title('Impact of 1 Possession Swing on Net Rating')

plt.show()