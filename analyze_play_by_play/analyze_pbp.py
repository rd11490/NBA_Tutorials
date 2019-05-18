import pandas as pd
import os


pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


dirname = os.path.dirname(__file__)
input_file = os.path.join(dirname, 'data/2017-18_pbp.csv')
output_file = os.path.join(dirname, 'data/unique_pbp.csv')

play_by_play = pd.read_csv(input_file)
play_by_play_for_analysis = play_by_play[['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE', 'HOMEDESCRIPTION', 'NEUTRALDESCRIPTION',
                                          'VISITORDESCRIPTION','PLAYER1_ID', 'PLAYER1_NAME', 'PLAYER1_TEAM_ID',
                                          'PLAYER1_TEAM_NICKNAME', 'PLAYER2_ID', 'PLAYER2_NAME', 'PLAYER2_TEAM_ID',
                                          'PLAYER2_TEAM_NICKNAME', 'PLAYER3_ID', 'PLAYER3_NAME', 'PLAYER3_TEAM_ID',
                                          'PLAYER3_TEAM_NICKNAME']]
play_by_play_for_analysis = play_by_play_for_analysis.fillna('')

play_by_play_for_analysis['DESCRIPTION'] = play_by_play_for_analysis['HOMEDESCRIPTION'] + ' ' + \
                                           play_by_play_for_analysis['NEUTRALDESCRIPTION'] + ' ' + \
                                           play_by_play_for_analysis['VISITORDESCRIPTION']

play_by_play_for_analysis = play_by_play_for_analysis[['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE','DESCRIPTION','PLAYER1_ID',
                                                       'PLAYER1_NAME', 'PLAYER1_TEAM_ID', 'PLAYER1_TEAM_NICKNAME',
                                                       'PLAYER2_ID', 'PLAYER2_NAME', 'PLAYER2_TEAM_ID',
                                                       'PLAYER2_TEAM_NICKNAME', 'PLAYER3_ID', 'PLAYER3_NAME',
                                                       'PLAYER3_TEAM_NICKNAME']]

def take_one(group):
    return group.head(1)

unique_pbp = play_by_play_for_analysis.groupby(by=['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE']).apply(take_one).reset_index(drop=True)

for event in unique_pbp['EVENTMSGTYPE'].unique():
    print(unique_pbp[unique_pbp['EVENTMSGTYPE'] == event])


unique_pbp.to_csv(output_file, index=False)