import pandas as pd

# Set display options for pandas for easier printing
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 101)



sspm = pd.read_csv('data/stable_spm.csv')

player_data = pd.read_csv('data/stats_nba_player_data_2019-20.csv')

# print(sspm)
# print(player_data)

player_data = player_data[['TEAM_ABBREVIATION', 'AGE', 'GP', 'PLAYER_ID', 'PLAYER_NAME']]
player_data['AGE'] = player_data['AGE'].astype(int)

sspm = sspm[['Tm','Age', 'G', 'Player', 'Stable SPR', 'Positionally Adj Stable SPR']]
sspm.columns = ['TEAM_ABBREVIATION', 'AGE', 'GP', 'PLAYER_NAME', 'Stable SPR', 'Positionally Adj Stable SPR']

def fix_team(df, old, new):
    tm_idx = df[df['TEAM_ABBREVIATION'] == old].index
    df.loc[tm_idx, 'TEAM_ABBREVIATION'] = new
    return df

def fix_dups(group):
    if group.shape[0]==1:
        return group
    else:
        return group[group['TEAM_ABBREVIATION'] == 'TOT']

sspm = sspm.groupby(by='PLAYER_NAME').apply(fix_dups).reset_index(drop=True)

sspm=fix_team(sspm, 'PHO', 'PHX')
sspm=fix_team(sspm, 'BRK', 'BKN')
sspm=fix_team(sspm, 'CHO', 'CHA')

print(sspm)

name_matches = player_data.merge(sspm, on='PLAYER_NAME', how='outer', suffixes=('_pd', '_sspm'))

name_matches_ids = name_matches.dropna()
name_matches_ids = name_matches_ids[['PLAYER_ID', 'PLAYER_NAME', 'Stable SPR', 'Positionally Adj Stable SPR']]

non_matches = name_matches[name_matches.isnull().any(axis=1)]

sspm_non_matches = non_matches[['TEAM_ABBREVIATION_sspm', 'AGE_sspm', 'GP_sspm', 'PLAYER_NAME', 'Stable SPR', 'Positionally Adj Stable SPR']].dropna()
sspm_non_matches.columns = ['TEAM_ABBREVIATION', 'AGE', 'GP', 'PLAYER_NAME', 'Stable SPR', 'Positionally Adj Stable SPR']
player_data_non_matches = non_matches[['TEAM_ABBREVIATION_pd', 'AGE_pd', 'GP_pd', 'PLAYER_ID', 'PLAYER_NAME']].dropna()
player_data_non_matches.columns = ['TEAM_ABBREVIATION', 'AGE', 'GP', 'PLAYER_ID', 'PLAYER_NAME']


joined = player_data_non_matches.merge(sspm_non_matches, how='outer', on=['TEAM_ABBREVIATION', 'AGE', 'GP'])
joined = joined.dropna()
joined = joined[['PLAYER_ID', 'PLAYER_NAME_x', 'Stable SPR', 'Positionally Adj Stable SPR']]
joined.columns = ['PLAYER_ID', 'PLAYER_NAME', 'Stable SPR', 'Positionally Adj Stable SPR']
prior = pd.concat([name_matches_ids, joined])
prior.to_csv('data/prior.csv', index=False)
print(prior)