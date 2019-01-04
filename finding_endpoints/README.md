## Finding endpoints from pages on Stats(dot)NBA(dot)com

In this tutorial I will show you how to use google chrome's developer tools
to get the information necessary to scrape data on stats.nba.com.

This tutorial will be broken into 2 parts:
1. Getting the endpoint from the page
2. Calling the endpoint and saving the data

### 0.1 Notes
The method presented here works for stats.nba.com, and may work for other data sources, but it will not work for all sources.
It will only work for javascript based pages that fill their data dynamically from external APIs. Any site that uses
dynamically generated pages through the use of a web framework such as Rails or Django will need to be scraped using a scraping library
such as BeautifulSoup4

### 0.2 Requirements
This tutorial uses the latest version of Google Chrome for finding the endpoint information.
The code in this tutorial was written in python 3.7 and uses the following libraries:
1. Pandas 0.23.4
2. urllib 1.24.1


### 1. Finding the endpoint information

For this tutorial I will be downloading the per game stats of every player in the league
in a single season which can be found on https://stats.nba.com/leaders/

The first step is to open google chrome and navigate to the page we want to gather the data from.

![League Leaders](screen_shots/players_page.png)

### 2. Getting data from stats.nba.com

#### Source Code

[Source Code](download_stats_nba_data.py)

For this we will be getting single season totals for all players who played in a single season using the endpoint `leaguedashplayerstats`.
The necessary params for this call can be found here: http://nbasense.com/nba-api/Stats/Stats/Players/PlayersGeneralStats

The code for this process is very simple:
First we need to import the necessary libraries. We need json for parsing the
response from the nba api, pandas for building our dataframe and urllib3 for making calls to the nba api.
```
import json
import pandas as pd
import urllib3
```

We now need to instantiate a client and choose a season
```
client = urllib3.PoolManager()
season = "2018-19"
```

Then we need to build our dataframe We do this by calling the endpoint described above and parsing the json into our dataframe.
Luckily the stats.nba api returns objects that can easily be converted into a dataframe, with a single field of headers and then an array of arrays
```
frame = extract_data(client, player_stats_url(season))

# Extract json
def extract_data(http_client, url):
    r = http_client.request('GET', url, headers=header_data)      # Call the GET endpoint
    resp = json.loads(r.data)                                     # Convert the response to a json object
    results = resp['resultSets'][0]                               # Take the first item in the resultsSet (This can be determined by inspection of the json response)
    headers = results['headers']                                  # Take the headers of the response (our column names)
    rows = results['rowSet']                                      # Take the rows of our response
    frame = pd.DataFrame(rows)                                    # Convert the rows to a dataframe
    frame.columns = headers                                       # Set our column names using the  extracted headers
    return frame


```


Now we just need to save our dataframe as a csv.
```
frame.to_csv("stats_nba_player_data_{0}.csv".format(season), index=False)
```
