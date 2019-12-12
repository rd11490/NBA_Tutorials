import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


for season in ['2018-19', '2019-20']:
    print('Season: {}'.format(season))
    possession = pd.read_csv('possession_{}.csv'.format(season))


    offensive_possessions = possession[['offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id', 'possessions']]

    o_possession_counts = offensive_possessions.groupby(by=['offensePlayer1Id', 'offensePlayer2Id', 'offensePlayer3Id', 'offensePlayer4Id', 'offensePlayer5Id']).sum().reset_index()

    defensive_possessions = possession[['defensePlayer1Id', 'defensePlayer2Id', 'defensePlayer3Id', 'defensePlayer4Id', 'defensePlayer5Id', 'possessions']]

    d_possession_counts = defensive_possessions.groupby(by=['defensePlayer1Id','defensePlayer2Id', 'defensePlayer3Id', 'defensePlayer4Id', 'defensePlayer5Id']).sum().reset_index()


    ### Offensive possession - baseline
    maximum = o_possession_counts['possessions'].max()
    minimum = o_possession_counts['possessions'].min()
    n_bins = maximum-minimum
    print('The minimum number of possessions played: {}, the maximum number of possessions played {}'.format(minimum, maximum))


    plt.figure()
    plt.hist(o_possession_counts['possessions'], bins=n_bins)
    plt.xlabel('Number of Possessions')
    plt.ylabel('Count')
    plt.title('Histogram of possessions played - Offense - Season: {}'.format(season))


    ### Offensive possession - Filter > 100
    total_lineup_count = o_possession_counts.shape[0]
    filtered_offesnive_possessions = o_possession_counts[o_possession_counts['possessions'] <= 100]
    high_possession_count = o_possession_counts[o_possession_counts['possessions'] > 100].shape[0]
    print('{} out of {} lineups have played more than 100 possessions together'.format(high_possession_count, total_lineup_count))
    print('The average number of possessions a lineup has played together is: {}'.format(o_possession_counts['possessions'].mean().round(2)))

    plt.figure()
    plt.hist(filtered_offesnive_possessions['possessions'], bins=100)
    plt.xlabel('Number of Possessions')
    plt.ylabel('Count')
    plt.title('Histogram of possessions played - Offense(<100) - Season: {}'.format(season))

    print('\n')
    ### Defensive possession - baseline
    maximum = d_possession_counts['possessions'].max()
    minimum = d_possession_counts['possessions'].min()
    n_bins = maximum-minimum
    print('The minimum number of possessions faced: {}, the maximum number of possessions faced {}'.format(minimum, maximum))
    ### Defensive possession - Filter > 100
    total_lineup_count_d = d_possession_counts.shape[0]
    filtered_defensive_possessions = d_possession_counts[d_possession_counts['possessions'] <= 100]
    high_possession_count_d = d_possession_counts[d_possession_counts['possessions'] > 100].shape[0]
    print('{} out of {} lineups have faced more than 100 possessions together'.format(high_possession_count_d, total_lineup_count_d))
    print('The average number of possessions a lineup has faced together is: {}'.format(d_possession_counts['possessions'].mean().round(2)))


    print('\n\n\n')



plt.show()


