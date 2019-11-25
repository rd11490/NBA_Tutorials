import pandas as pd
import numpy as np
import random

import matplotlib.pyplot as plt

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


fg3_pct = 0.33333
fg2_pct = 0.5

pps_results = []

def shots(n):
    shot_results_3 = []
    shot_results_2 = []

    result = { 'shots': n }
    for i in range(n):
        roll = random.random()
        if roll < fg3_pct:
            shot_results_3.append(3)
        else:
            shot_results_3.append(0)

        if roll < fg2_pct:
            shot_results_2.append(2)
        else:
            shot_results_2.append(0)



    result['Points Per Shot 3s'] = np.mean(shot_results_3)
    result['Variance 3s'] = np.var(shot_results_3)
    result['StDev 3s'] = np.std(shot_results_3)


    result['Points Per Shot 2s'] = np.mean(shot_results_2)
    result['Variance 2s'] = np.var(shot_results_2)
    result['StDev 2s'] = np.std(shot_results_2)

    return result

for n in range(1, 200):
    pps_results.append(shots(n))

df = pd.DataFrame(pps_results)

df[['Points Per Shot 3s', 'Points Per Shot 2s']].plot()
plt.title('PPS')
plt.xlabel('Shot Attempts')

df[['Variance 3s', 'Variance 2s']].plot()
plt.title('Variance')
plt.xlabel('Shot Attempts')

f3 = plt.figure()
plt.plot(df['shots'], df['Points Per Shot 3s'], color='orange', label='Points Per Shot 3s')
plt.fill_between(df['shots'], df['Points Per Shot 3s'] + df['StDev 3s'], df['Points Per Shot 3s'] - df['StDev 3s'], color='orange', alpha=0.2)

plt.plot(df['shots'], df['Points Per Shot 2s'], color='dodgerblue', label='Points Per Shot 2s')
plt.fill_between(df['shots'], df['Points Per Shot 2s'] + df['StDev 2s'], df['Points Per Shot 2s'] - df['StDev 2s'], color='dodgerblue', alpha=0.2)
plt.xlabel('Shot Attempts')
plt.ylabel('PPS')
plt.legend()
plt.title('PPS with Standard Deviation')

plt.show()


