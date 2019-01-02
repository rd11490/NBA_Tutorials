import bs4
import urllib3
import pandas as pd


def player_totals_page(season):
    return "https://www.basketball-reference.com/leagues/NBA_{0}_totals.html".format(season)


def extract_column_names(table):
    columns = [col["aria-label"] for col in table.find_all("thead")[0].find_all("th")][1:]
    columns.append("id")
    return columns


def extract_rows(table):
    rows = table.find_all("tbody")[0].find_all("tr")
    parsed_rows = []
    for r in rows:
        parsed = parse_row(r)
        if len(parsed) > 0:
            parsed_rows.append(parsed)
    return parsed_rows


def parse_row(row):
    other_data = row.find_all("td")
    if len(other_data) == 0:
        return []
    id = other_data[0].find_all("a")[0]["href"].replace("/players/", "").replace(".html","").split("/")[-1]
    row_data = [td.string for td in other_data]
    row_data.append(id)
    return row_data


http = urllib3.PoolManager()

season = '2019'

columns = []
rows = []

r = http.request('GET', player_totals_page(season))         # Request the page
soup = bs4.BeautifulSoup(r.data, 'html')                    # Parse page with BeuatifulSoup
f = soup.find_all("table")                                  # Find the talbe
if len(f) > 0:                                              # Check to ensure the table is there
    columns = extract_column_names(f[0])                    # Extract column names from the table header
    rows = rows + extract_rows(f[0])                        # Extract data from table rows

frame = pd.DataFrame(rows)                                  # Convert rows to Dataframe

frame.columns = columns
frame.to_csv("basketball_reference_totals_{0}.csv".format(season), index=False)
