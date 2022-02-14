import time
import pandas as pd
import requests

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# Headers for API Request
header_data  = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'x-nba-stats-token': 'true',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'x-nba-stats-origin': 'stats',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

# constants for season type
regular_season = 'Regular Season'
playoffs = 'Playoffs'

# build play by play url
def play_by_play_url(game_id):
    return "https://stats.nba.com/stats/playbyplayv2/?gameId={0}&startPeriod=0&endPeriod=14".format(game_id)

# build game log url
def game_log_url(season, season_type):
    return "http://stats.nba.com/stats/leaguegamelog/?leagueId=00&season={}&seasonType={}&playerOrTeam=T&counter=0&sorter=PTS&direction=ASC&dateFrom=&dateTo=".format(season, season_type)

# extracts pbp data from api response
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


###
### Download and Save Play by Play Data
###
def download_pbp(game_id):
    play_by_play = extract_data(play_by_play_url(game_id))

    play_by_play.to_csv("data/{}_pbp.csv".format(game_id), index=False)

# Set the season and season typ
season = '2021-22'
season_type = regular_season

# Download the league game log
schedule = extract_data(game_log_url(season, season_type))

# Save the game log in case you want it for future reference
schedule.to_csv('data/schedule_{}_{}.csv'.format(season, season_type), index=False)
# Get all of the unique game ids
game_ids = schedule['GAME_ID'].unique()

# For each game id, download the play by play then sleep for .75 seconds so that we don't hit the stats nba rate limit
for id in game_ids:
    download_pbp(id)
    time.sleep(.75)
