import pandas as pd
import matplotlib.pyplot as plt

# Set display options for pandas for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.width', 1000)

# Read possessions CSV
rapm = pd.read_csv('results/rapm_by_date_20_21.csv')
first_day = rapm['gameDate'].min()

rapm['day'] = (rapm['gameDate'] - first_day)/(1000 * 60 * 60 * 24 * 7)
tatum = rapm[rapm['playerId'] == 1628369].sort_values(by='gameDate', ascending=True)
jokic = rapm[rapm['playerId'] == 203999].sort_values(by='gameDate', ascending=True)
harden = rapm[rapm['playerId'] == 201935].sort_values(by='gameDate', ascending=True)

fig = plt.figure(figsize=(12, 6))

plt.plot(tatum['day'], tatum['RAPM'], color='g', label='Tatum')
plt.plot(harden['day'], harden['RAPM'], color='k', label='Harden')
plt.plot(jokic['day'], jokic['RAPM'], color='b', label='Jokic')

plt.xlabel('Week')
plt.ylabel('RAPM')
plt.title('RAPM by Week')
plt.legend(loc='lower right')
plt.show()
