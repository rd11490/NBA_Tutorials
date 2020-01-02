import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

data = pd.read_csv('data/rapm_adjusted.csv')
print(data)
brown = data[data['Player']=='Brown']
tatum = data[data['Player']=='Tatum']

fig = plt.figure(figsize=(12, 6))
plt.plot(brown['AdjustedPossessions'], brown['RAPM'], color='blue', label='Brown RAPM')
plt.plot(brown['AdjustedPossessions'], brown['RAPM__Def'], color='blue', label='Brown DRAPM', linestyle=':')
plt.plot(brown['AdjustedPossessions'], brown['RAPM__Off'], color='blue', label='Brown ORAPM', linestyle='--')


plt.plot(tatum['AdjustedPossessions'], tatum['RAPM'], color='red', label='Tatum RAPM')
plt.plot(tatum['AdjustedPossessions'], tatum['RAPM__Def'], color='red', label='Tatum DRAPM', linestyle=':')
plt.plot(tatum['AdjustedPossessions'], tatum['RAPM__Off'], color='red', label='Tatum ORAPM', linestyle='--')

plt.ylim(-1,4)
plt.legend(loc='upper right')
plt.title('Change in RAPM After Adjusting Possessions')
plt.xlabel('Number of Changed Possessions')
plt.ylabel('RAPM')

plt.savefig('ChangeInRAPM.png')

fig2 = plt.figure(figsize=(12, 6))
plt.plot(brown['AdjustedPossessions'], brown['RAPM_Rank'], color='blue', label='Brown RAPM Rank')
plt.plot(brown['AdjustedPossessions'], brown['RAPM__Def_Rank'], color='blue', label='Brown DRAPM Rank', linestyle=':')
plt.plot(brown['AdjustedPossessions'], brown['RAPM_Off_Rank'], color='blue', label='Brown ORAPM Rank', linestyle='--')


plt.plot(tatum['AdjustedPossessions'], tatum['RAPM_Rank'], color='red', label='Tatum RAPM Rank')
plt.plot(tatum['AdjustedPossessions'], tatum['RAPM__Def_Rank'], color='red', label='Tatum DRAPM Rank', linestyle=':')
plt.plot(tatum['AdjustedPossessions'], tatum['RAPM_Off_Rank'], color='red', label='Tatum ORAPM Rank', linestyle='--')

plt.ylim(0,350)
plt.legend(loc='upper right')
plt.title('Change in RAPM  Rank After Adjusting Possessions')
plt.xlabel('Number of Changed Possessions')
plt.ylabel('RAPM  Rank')

plt.savefig('ChangeInRAPMRank.png')
plt.show()