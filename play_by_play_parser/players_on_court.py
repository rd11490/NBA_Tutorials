import pandas as pd
import requests

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# Game Id
game_id = '0041700404'

# Headers for API Request
header_data = {
    'Host': 'stats.nba.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    'Referer': 'stats.nba.com',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
}


###
### Calculate Players on court at the start of each period
###

# Build advanced boxscore url
def advanced_boxscore_url(game_id, start, end):
    return 'https://stats.nba.com/stats/boxscoreadvancedv2/?gameId={0}&startPeriod=0&endPeriod=14&startRange={1}&endRange={2}&rangeType=2'.format(
        game_id, start, end)


# Helper functions
def calculate_time_at_period(period):
    if period > 5:
        return (720 * 4 + (period - 5) * (5 * 60)) * 10
    else:
        return (720 * (period - 1)) * 10


def split_subs(df, tag):
    subs = df[[tag, 'PERIOD', 'EVENTNUM']]
    subs['SUB'] = tag
    subs.columns = ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']
    return subs


def frame_to_row(df):
    team1 = df['TEAM_ID'].unique()[0]
    team2 = df['TEAM_ID'].unique()[1]
    players1 = df[df['TEAM_ID'] == team1]['PLAYER_ID'].tolist()
    players1.sort()
    players2 = df[df['TEAM_ID'] == team2]['PLAYER_ID'].tolist()
    players2.sort()

    lst = [team1]
    lst.append(players1)
    lst.append(team2)
    lst.append(players2)


    return lst


# extracts data from api response
def extract_data(url):
    print(url)
    r = requests.get(url, headers=header_data)
    resp = r.json()
    results = resp['resultSets'][0]
    headers = results['headers']
    rows = results['rowSet']
    frame = pd.DataFrame(rows)
    frame.columns = headers
    return frame


play_by_play = pd.read_csv(('data/{}_pbp.csv'.format(game_id)))

substitutionsOnly = play_by_play[play_by_play['EVENTMSGTYPE'] == 8][['PERIOD', 'EVENTNUM', 'PLAYER1_ID', 'PLAYER2_ID']]
substitutionsOnly.columns = ['PERIOD', 'EVENTNUM', 'OUT', 'IN']

subs_in = split_subs(substitutionsOnly, 'IN')
subs_out = split_subs(substitutionsOnly, 'OUT')

full_subs = pd.concat([subs_out, subs_in], axis=0).reset_index()[['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']]
first_event_of_period = full_subs.loc[full_subs.groupby(by=['PERIOD', 'PLAYER_ID'])['EVENTNUM'].idxmin()]
players_subbed_in_at_each_period = first_event_of_period[first_event_of_period['SUB'] == 'IN'][
    ['PLAYER_ID', 'PERIOD', 'SUB']]

periods = players_subbed_in_at_each_period['PERIOD'].drop_duplicates().values.tolist()

rows = []
for period in periods:
    low = calculate_time_at_period(period) + 5
    high = calculate_time_at_period(period + 1) - 5
    boxscore = advanced_boxscore_url(game_id, low, high)
    boxscore_players = extract_data(boxscore)[['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ID']]
    boxscore_players['PERIOD'] = period

    players_subbed_in_at_period = players_subbed_in_at_each_period[players_subbed_in_at_each_period['PERIOD'] == period]

    joined_players = pd.merge(boxscore_players, players_subbed_in_at_period, on=['PLAYER_ID', 'PERIOD'], how='left')
    joined_players = joined_players[pd.isnull(joined_players['SUB'])][['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ID', 'PERIOD']]
    row = frame_to_row(joined_players)
    row.append(period)
    rows.append(row)

players_on_court_at_start_of_period = pd.DataFrame(rows)
cols = ['TEAM_ID_1', 'TEAM_1_PLAYERS', 'TEAM_ID_2', 'TEAM_2_PLAYERS', 'PERIOD']
players_on_court_at_start_of_period.columns = cols
players_on_court_at_start_of_period.to_csv("data/{}_players_at_period.csv".format(game_id), index=False)
