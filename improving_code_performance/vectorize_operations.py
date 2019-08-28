# Import pandas, numpy and RidgeCV from sklearn
import datetime

import pandas as pd

# Set display options for pandas for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Read possessions CSV
possessions = pd.read_csv('data/rapm_possessions.csv')

# Filter out 0 possession possessions
possessions = possessions[possessions['possessions'] > 0]

# Calculate pts/100 possessions for each possession
start_df = datetime.datetime.now()
possessions['PointsPerPossession'] = 100 * possessions['points'] / possessions['possessions']
end_df = datetime.datetime.now()
print('Time to run as Dataframe operation', end_df-start_df)

start_np = datetime.datetime.now()
possessions['PointsPerPossessionVec'] = 100 * possessions['points'].values / possessions['possessions'].values
end_np = datetime.datetime.now()
print('Time to run as Numpy operation', end_np-start_np)

print('Speedup: {0:.2f}x'.format((end_df-start_df).microseconds / (end_np-start_np).microseconds))