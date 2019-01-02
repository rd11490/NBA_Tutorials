import pandas as pd
from fuzzywuzzy import fuzz

pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


# Container for our player object. It needs to hold our IDs and the fields we will use for entity resolution
class Player:
    def __init__(self, name, nba_id, bbref_id, fga, rbd, ast):
        self.name = name
        self.nba_id = nba_id
        self.bbref_id = bbref_id
        self.fga = fga
        self.rbd = rbd
        self.ast = ast


# Converts a basketball reference season to a season recognized by stats.nba.com (2019 -> 2018-19)
def convert_bbref_season_to_nba_season(season):
    year = int(season)
    last_year = year - 1
    last_two = season[-2:]
    return "{0}-{1}".format(last_year, last_two)


# Basketball reference contains multiple rows for players who have played on multiple teams.
# we only care about the season total for the player so we must deduplicate the rows (selected Team = TOT)
def deduplicate_traded_players(group):
    if len(group) > 1:
        return group[group["Team"] == "TOT"]
    return group


def check_names_fuzzy_match(row):
    row["name_match"] = fuzz.partial_ratio(row["Player"], row["PLAYER_NAME"]) > 60
    return row


season = "2019"

# Read our basketball_reference data
bbref_data = pd.read_csv("basketball_reference_totals_{}.csv".format(season))
# read out stats.nba.com data
nba_data = pd.read_csv("stats_nba_player_data_{}.csv".format(convert_bbref_season_to_nba_season(season)))
# convert the player id from an int to a string
nba_data["PLAYER_ID"] = nba_data["PLAYER_ID"].astype(str)

# take the player name, id, team and fields we will use for deduplication from bbref data
bbref_base_data = bbref_data[["Player", "id", "Team", "Field Goal Attempts", "Total Rebounds", "Assists"]].groupby(
    by="id").apply(deduplicate_traded_players)

# take the player name, id, and fields we will use for deduplication from stats.nba.com data
nba_base_data = nba_data[["PLAYER_ID", "PLAYER_NAME", "FGA", "REB", "AST"]]

# Perform a full outer join on the two dataframes. This allows us to get all of the exact matches
name_matches = bbref_base_data.merge(nba_base_data,
                                     left_on=["Player", "Field Goal Attempts", "Total Rebounds", "Assists"],
                                     right_on=["PLAYER_NAME", "FGA", "REB", "AST"], how="outer")

# take all of the exact matches and rename the columns, we only care about player name and id from each source
name_matches_ids = name_matches.dropna()
name_matches_ids = name_matches_ids[["Player", "id", "PLAYER_NAME", "PLAYER_ID"]]
name_matches_ids.columns = ["bbref_name", "bbref_id", "nba_name", "nba_id"]

# Take all of the rows from the full outer join that have null values. These are the cases where no match was found.
non_matches = name_matches[name_matches.isnull().any(axis=1)]

# take all of the bbref data from non_matches
bbref_non_matches = non_matches[["Player", "id", "Field Goal Attempts", "Total Rebounds", "Assists"]].dropna()

# take all of the stats.nba data from the non_matches
nba_non_matches = non_matches[["PLAYER_NAME", "PLAYER_ID", "FGA", "REB", "AST"]].dropna()

possible_matches = bbref_non_matches.merge(nba_non_matches,
                                     left_on=["Field Goal Attempts", "Total Rebounds", "Assists"],
                                     right_on=["FGA", "REB", "AST"], how="outer").apply(check_names_fuzzy_match, axis=1)


#print out any misses
print( possible_matches[possible_matches["name_match"] != True].head(10))

fuzzy_matches = possible_matches[possible_matches["name_match"]][["Player", "id", "PLAYER_NAME", "PLAYER_ID"]]

# Give the dataframe column names
fuzzy_matches.columns = ["bbref_name", "bbref_id", "nba_name", "nba_id"]

# merge our fuzzy matched ids with our exact match ids
all_matches = fuzzy_matches.append(name_matches_ids)

# write to csv
all_matches.to_csv("nba_id_matches_{}.csv".format(season))
