## Getting the players at the start of a period:

If you see any issues or think there is a better way to do something,
don't hesitate to open a PR, submit an issue, or reach out to me directly

### Using the stats.nba API

#### Getting the players who played in a period

The NBA indirectly provides the players on the court at the start of a
period through the advancedboxscorev2 endpoint. It does this by allowing
the caller to specify a start time and end time between which stats are
calculated. From this information we can determine only the players who are on the
the court during a given period.

Example GET call:
```
https://stats.nba.com/stats/boxscoreadvancedv2/?gameId=0041700404&startPeriod=0&endPeriod=14&startRange=0&endRange=2147483647&rangeType=0
```


In order to use this method you need to set 4 parameters to non-default values:
1. gameId: The id of the game you want
2. startRange: half a second past the start of the period. (if you are processing Q2, then the startRange should be `7200 +5 = 7205`
3. startRange: half a second before the end of the period. (if you are processing Q2, then the startRange should be `14400 - 5 = 14395`
4. rangeType: should always be 2


Example call:
```
https://stats.nba.com/stats/boxscoreadvancedv2/?gameId=0041700404&startPeriod=0&endPeriod=14&startRange=7205&endRange=14395&rangeType=2
```

From this call we can see that all of the players that played in
Q2 in game 4 of the 2018 NBA Finals were:

GSW
1. Draymond Green
2. Klay Thompson
3. Stephen Curry
4. Shaun Livingston
5. David West
6. Kevin Durant
7. JaVale McGee
8. Andre Iguodala
9. Jordan Bell
10. Nick Young

CLE
1. LeBron James
2. Rodney Hood
3. Jeff Green
4. Kyle Korver
5. Larry Nance Jr.
6. Kevin Love"
7. Tristan Thompson
8. JR Smith
9. George Hill


#### Getting the subsitutions in a period
Once we have a list of all of the players who were on the court in a
given period we can use all of the substitution events during that period
to determine who started the period on the court. First we take
all of the substitution events for each player during the period (SUB IN vs SUB OUT)
and then find out which of the two was the first substitution event for the player. We then take all of
the players whose first event was SUBBED IN and filter those out of the list
of players who played in the period. We are then left with the players
who started the period.


Example call:
```
https://stats.nba.com/stats/playbyplayv2/?gameId=0041700404&&startPeriod=0&endPeriod=14
```

The field `EVENTMSGTYPE` can be used to determine which event type each row
corresponds to. Substitutions are `EVENTMSGTYPE = 8`

By determining which player's first substitution event is to be subbed
into the game and filtering those players from the above list, we are
left with only the starters:

GSW
1. Draymond Green
2. Klay Thompson
3. Stephen Curry
4. Shaun Livingston
5. David West

CLE
1. LeBron James
2. Rodney Hood
3. Jeff Green
4. Kyle Korver
5. Larry Nance Jr.

#### Example

[Example Code](players_on_court.py)

Using Python 3.6

imports and settings
```
import json
import pandas as pd
import urllib3

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
```

Set the following headers for the API calls
```
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
```

Build the urls for the play by play and the advanced box score
```
# endpoints
def play_by_play_url(game_id):
    return "https://stats.nba.com/stats/playbyplayv2/?gameId={0}&startPeriod=0&endPeriod=14".format(game_id)


def advanced_boxscore_url(game_id, start, end):
    return "https://stats.nba.com/stats/boxscoreadvancedv2/?gameId={0}&startPeriod=0&endPeriod=14&startRange={1}&endRange={2}&rangeType=2".format(game_id, start, end)
```

generate a http client
```
http = urllib3.PoolManager()
```


Function for downloading and extracting the data from a stats.nba endpoint into a dataframe
note: `results = resp['resultSets'][0]` only works because in all cases I only need the first item in the resultsSet
```
def extract_data(url):
    r = http.request('GET', url, headers=header_data)
    resp = json.loads(r.data)
    results = resp['resultSets'][0]
    headers = results['headers']
    rows = results['rowSet']
    frame = pd.DataFrame(rows)
    frame.columns = headers
    return frame
```

Function for calculating the start time of each period
```
def calculate_time_at_period(period):
    if period > 5:
        return (720 * 4 + (period - 5) * (5 * 60)) * 10
    else:
        return (720 * (period - 1)) * 10

```

Helper Function for splitting SUB IN and SUB OUT players for processing
```
def split_subs(df, tag):
    subs = df[[tag, 'PERIOD', 'EVENTNUM']]
    subs['SUB'] = tag
    subs.columns = ['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']
    return subs
```

Given a game_id download and extract the play by play data
```
game_id = "0041700404"
frame = extract_data(play_by_play_url(game_id))
```

Filter the play by play to only include the substitutions
```
substitutionsOnly = frame[frame["EVENTMSGTYPE"] == 8][['PERIOD', 'EVENTNUM', 'PLAYER1_ID', 'PLAYER2_ID']]
substitutionsOnly.columns = ['PERIOD', 'EVENTNUM', 'OUT', 'IN']
```

Split the frame into subs in and subs out with label
```
subs_in = split_subs(substitutionsOnly, 'IN')
subs_out = split_subs(substitutionsOnly, 'OUT')
```

Merge the two frames together
```
full_subs = pd.concat([subs_out, subs_in], axis=0).reset_index()[['PLAYER_ID', 'PERIOD', 'EVENTNUM', 'SUB']]
```

Group by the player and period then take the first substitution event for each player in each period
```
first_event_of_period = full_subs.loc[full_subs.groupby(by=['PERIOD', 'PLAYER_ID'])['EVENTNUM'].idxmin()]
```

Filter so that only the players whose first event was to be subbed into the game are in the dataframe
```
players_subbed_in_at_each_period = first_event_of_period[first_event_of_period['SUB'] == 'IN'][['PLAYER_ID', 'PERIOD', 'SUB']]
```

Get a list of each period in the game
```
periods = players_subbed_in_at_each_period['PERIOD'].drop_duplicates().values.tolist()
```


Calculate the start and end time of the period (offset by .5 seconds so that there
is no collision at the start/end barrier between periods). Then download
the boxscore for that time range, extract the player name, id, and team.
Join the boxscore with the substitution frame from above and filter out any
rows where the join was successful
(Any player who was subbed in will have SUB as `IN`.
Any player who started will have SUB as `NAN`)

```
frames = []
for period in periods:

    low = calculate_time_at_period(period) + 5
    high = calculate_time_at_period(period + 1) - 5
    boxscore = advanced_boxscore_url(game_id, low, high)
    boxscore_players = extract_data(boxscore)[['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION']]
    boxscore_players['PERIOD'] = period

    players_subbed_in_at_period = players_subbed_in_at_each_period[players_subbed_in_at_each_period['PERIOD'] == period]

    joined_players = pd.merge(boxscore_players, players_subbed_in_at_period, on=['PLAYER_ID', 'PERIOD'], how='left')
    joined_players = joined_players[pd.isnull(joined_players['SUB'])][['PLAYER_NAME', 'PLAYER_ID', 'TEAM_ABBREVIATION', 'PERIOD']]
    frames.append(joined_players)

out = pd.concat(frames)
print(out)
```


###### Special thanks to Jason Roman of nbasense for documenting the NBA APIs

BoxScoreAdvanced:
http://nbasense.com/nba-api/Stats/Stats/Game/BoxScoreAdvanced

PlayByPlay:
http://nbasense.com/nba-api/Stats/Stats/Game/PlayByPlay
