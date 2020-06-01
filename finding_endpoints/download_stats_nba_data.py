import json

import pandas as pd
import requests

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

header_data  = {
    'User-Agent': 'Some User Agent',
    'x-nba-stats-origin': 'stats',
    'Referer': 'https://stats.nba.com/',
}


# endpoints
def player_stats_url(season):
    return "https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season={0}&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight=".format(
        season)


# Extract json
def extract_data(url):
    r = requests.get(url, headers=header_data)                  # Call the GET endpoint
    resp = r.json()                                             # Convert the response to a json object
    print(resp)
    results = resp['resultSets'][0]                             # take the first item in the resultsSet (This can be determined by inspection of the json response)
    headers = results['headers']                                # take the headers of the response (our column names)
    rows = results['rowSet']                                    # take the rows of our response
    frame = pd.DataFrame(rows)                                  # convert the rows to a dataframe
    frame.columns = headers                                     # set our column names using the  extracted headers
    return frame


season = "2018-19"

frame = extract_data(player_stats_url(season))
print(frame)

frame.to_csv("stats_nba_player_data_{0}.csv".format(season), index=False)
