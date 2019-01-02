## Deduplicating players between different sources

In this tutorial I hope to show a method for mapping ids between different sources of nba data.
When working with nba data we often have to use different data sources. Unfortunately
those sources do no always provide an easy way to map from one source to another. For example
Basketball Reference lists Taurean Prince as Taurean Waller-Prince whereas stats.nba.com lists him as Taurean Prince.
We can not just split on the hyphen to clean up this name because Michael Kidd-Gilchrist is listed the same way on both sources.
To deal with this type of corner case and others we will use fuzzy string matching with stats that should be consistent across sources to match names and ids.

This tutorial will be broken into 3 parts:
1. Getting single season player data from stats.nba.com
2. Getting single season player data from basketball_reference
3. Performing a basic entity resolution technique to map the ids from the two sources

### 0.1 Notes/Warnings
This tutorial might be considered overkill for this exact problem. That is okay,
I really just want to get this idea out there for some of the more complicated
deduplication problems i've seen in the basketball stats world. This is a very simplified version
of a solution my team worked on at a previous employer in to deduplicate
over 1 billion employment records. That data was not nearly as clean and
did not have the same constant identifying data that you can use to make and break links, but the basic idea is the same.

I am not a python developer by trade, so if you think I am doing something incorrectly,
inefficiently, or poorly, please let me know. I am always working to become a better
developer and appreciate any criticism and/or suggetsions.

### 0.2 Requirements
This tutorial was written in python 3.7 and uses the following libraries:
1. Pandas 0.23.4
2. urllib 1.24.1
3. BeautifulSoup4 4.6.3
4. fuzzywuzzy 0.17.0

### 1. Getting data from stats.nba.com

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


### 2. Getting data from basketball reference

#### Source Code

[Source Code](scrape_bbref.py)

For this section we will be scraping the following basketball reference page: https://www.basketball-reference.com/leagues/NBA_2019_totals.html.

Like in the previous seciton, the code for this is very simple. We will download the page source, find the table we want, and extract the data from the talbe.

The first thing we need to do is import the libraries we need. We will use urllib3 for getting the page, bs4 for parsing the html, and pandas for storing our results.
```
import bs4
import urllib3
import pandas as pd
```

Once again we need to instatiate our client and select a season:
```
http = urllib3.PoolManager()

season = '2019'
```

We then need to initialize an array of column names and an array that will represent the table
```
columns = []
rows = []
```

We then process the results and store them in a dataframe
```
r = http.request('GET', player_totals_page(season))         # Request the page
soup = bs4.BeautifulSoup(r.data, 'html')                    # Parse page with BeuatifulSoup
f = soup.find_all("table")                                  # Find the talbe
if len(f) > 0:                                              # Check to ensure the table is there
    columns = extract_column_names(f[0])                    # Extract column names from the table header
    rows = rows + extract_rows(f[0])                        # Extract data from table rows

frame = pd.DataFrame(rows)                                  # Convert rows to Dataframe

```

To extract the column names we find all of the labels for the column headers and store them in an array
```
def extract_column_names(table):
    columns = [col["aria-label"] for col in table.find_all("thead")[0].find_all("th")][1:]
    columns.append("id")
    return columns
```

To extract the rows from the table we need to find all of the rows of the table and parse them
```
def extract_rows(table):
    rows = table.find_all("tbody")[0].find_all("tr")
    parsed_rows = []
    for r in rows:
        parsed = parse_row(r)
        if len(parsed) > 0:
            parsed_rows.append(parsed)
    return parsed_rows

```

Parsing the rows is straight forward, you just need to take all of the data from the row . We also want to get the player id
which can be extracted from the player link. To do that we find the anchor tag in the player name row and parse the href for the id.

```
def parse_row(row):
    other_data = row.find_all("td")
    if len(other_data) == 0:
        return []
    id = other_data[0].find_all("a")[0]["href"].replace("/players/", "").replace(".html","").split("/")[-1]
    row_data = [td.string for td in other_data]
    row_data.append(id)
    return row_data
```

Once we have the table in a dataframe, we set the column names and save to a CSV
```
frame.columns = columns
frame.to_csv("basketball_reference_totals_{0}.csv".format(season), index=False)

```


### 3. Entity Resolution

#### Source Code

[Source Code](deduplicate_sources.py)

In this section we will be using the data gathered in the previous section and deduplicating them in order to generate a map of player ids from one source to the other.

What we will do is take the player name, id, and some additional stats that we know will be consistent across sources.
In this tutorial we will take total assists, field goal attempts and rebounds, but if we had different data we could use
team, first year in league, age, college, etc. You just need some piece of identifying data that should remain constant across sources.

We will then do a full outer join on between the two sources on player name and the identifying data to get all of the exact name matches.
Then we take the remaining players who did not meet the join requirements and try to fuzzy match them


As with the other steps in this tutorial, the first thing we need to do is import our libraries.
We will be using pandas to read the csvs and join them, and fuzzywuzzy for fuzzy string compare.
```
import pandas as pd
from fuzzywuzzy import fuzz
```

We need to select our season (I am using basketball reference season as the base season for this) and read the data we previously gathered
```
season = "2019"

# Read our basketball_reference data
bbref_data = pd.read_csv("basketball_reference_totals_{}.csv".format(season))

# read out stats.nba.com data
nba_data = pd.read_csv("stats_nba_player_data_{}.csv".format(convert_bbref_season_to_nba_season(season)))

# convert the player id from an int to a string
nba_data["PLAYER_ID"] = nba_data["PLAYER_ID"].astype(str)
```

To map from basketball reference season to stats.nba season we will use the following function:
```
# Converts a basketball reference season to a season recognized by stats.nba.com (2019 -> 2018-19)
def convert_bbref_season_to_nba_season(season):
    year = int(season)
    last_year = year - 1
    last_two = season[-2:]
    return "{0}-{1}".format(last_year, last_two)
```

We need to select the data we will be using for deduplication from our baseketball reference data.
```
# take the player name, id, team and fields we will use for deduplication from bbref data
bbref_base_data = bbref_data[["Player", "id", "Team", "Field Goal Attempts", "Total Rebounds", "Assists"]].groupby(
    by="id").apply(deduplicate_traded_players)
```

We also need to deduplicate players who played for multiple teams in a single year on
```
# Basketball reference contains multiple rows for players who have played on multiple teams.
# we only care about the season total for the player so we must deduplicate the rows (selected Team = TOT)
def deduplicate_traded_players(group):
    if len(group) > 1:
        return group[group["Team"] == "TOT"]
    return group
```

Like above we select the columns we need for deduplication from the stats.nba data
```
# take the player name, id, and fields we will use for deduplication from stats.nba.com data
nba_base_data = nba_data[["PLAYER_ID", "PLAYER_NAME", "FGA", "REB", "AST"]]

```

We then join the two dataframes together on the player name and the fields that should be constant between sources. After that we drop any row that the join failed on, take only the name and id columns and rename them.
```
# Perform a full outer join on the two dataframes. This allows us to get all of the exact matches
name_matches = bbref_base_data.merge(nba_base_data,
                                     left_on=["Player", "Field Goal Attempts", "Total Rebounds", "Assists"],
                                     right_on=["PLAYER_NAME", "FGA", "REB", "AST"], how="outer")

# take all of the exact matches and rename the columns, we only care about player name and id from each source
name_matches_ids = name_matches.dropna()
name_matches_ids = name_matches_ids[["Player", "id", "PLAYER_NAME", "PLAYER_ID"]]
name_matches_ids.columns = ["bbref_name", "bbref_id", "nba_name", "nba_id"]
```

Now we need to handle the cases where we couldn't get exact matches. We will take only the rows that have a null value and then seperate the frame back into their original bbref data and nba data.

```
# Take all of the rows from the full outer join that have null values. These are the cases where no match was found.
non_matches = name_matches[name_matches.isnull().any(axis=1)]

# take all of the bbref data from non_matches
bbref_non_matches = non_matches[["Player", "id", "Field Goal Attempts", "Total Rebounds", "Assists"]].dropna()

# take all of the stats.nba data from the non_matches
nba_non_matches = non_matches[["PLAYER_NAME", "PLAYER_ID", "FGA", "REB", "AST"]].dropna()
```

We then join again but this time we leave out the player name as a join condition. This will match fga, rebounds and assists. After that we will apply a fuzzy name match
to account for any cases where players had the same number of attempts, rebounds and assists to make sure their names match up.
I also print out any cases where the fuzzy matching failed so that I can be sure we matched all of the players.
```
possible_matches = bbref_non_matches.merge(nba_non_matches,
                                     left_on=["Field Goal Attempts", "Total Rebounds", "Assists"],
                                     right_on=["FGA", "REB", "AST"], how="outer").apply(check_names_fuzzy_match, axis=1)


#print out any misses
print( possible_matches[possible_matches["name_match"] != True].head(10))

fuzzy_matches = possible_matches[possible_matches["name_match"]][["Player", "id", "PLAYER_NAME", "PLAYER_ID"]]

# Give the dataframe column names
fuzzy_matches.columns = ["bbref_name", "bbref_id", "nba_name", "nba_id"]```
```

The fuzzy name match logic is really simple, just do a partial ratio match on the names and make sure the value is higher than some cutoff that you find appropriate. I found 60 to be good
```
def check_names_fuzzy_match(row):
    row["name_match"] = fuzz.partial_ratio(row["Player"], row["PLAYER_NAME"]) > 60
    return row
```

Finally I merge my fuzzy matches with my exact matches and save the results
```
# merge our fuzzy matched ids with our exact match ids
all_matches = fuzzy_matches.append(name_matches_ids)

# write to csv
all_matches.to_csv("nba_id_matches_{}.csv".format(season))
```

