import pandas as pd
import os


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


dirname = os.path.dirname(__file__)
input_file = os.path.join(dirname, 'data/2017-18_pbp.csv')
output_file = os.path.join(dirname, 'data/unique_pbp.csv')

play_by_play = pd.read_csv(input_file)
play_by_play_for_analysis = play_by_play[['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE', 'HOMEDESCRIPTION', 'NEUTRALDESCRIPTION', 'VISITORDESCRIPTION']]
play_by_play_for_analysis = play_by_play_for_analysis.fillna('')

play_by_play_for_analysis['DESCRIPTION'] = play_by_play_for_analysis['HOMEDESCRIPTION'] + ' ' + play_by_play_for_analysis['NEUTRALDESCRIPTION'] + ' ' + play_by_play_for_analysis['VISITORDESCRIPTION']
play_by_play_for_analysis = play_by_play_for_analysis[['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE','DESCRIPTION']]

def take_one(group):
    return group.head(1)

unique_pbp = play_by_play_for_analysis.groupby(by=['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE']).apply(take_one).reset_index(drop=True)

for event in unique_pbp['EVENTMSGTYPE'].unique():
    print(unique_pbp[unique_pbp['EVENTMSGTYPE'] == event])


unique_pbp.to_csv(output_file, index=False)