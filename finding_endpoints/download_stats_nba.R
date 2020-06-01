require(httr)



headers = c(
  `Connection` = 'keep-alive',
  `Accept` = 'application/json, text/plain, */*',
  `x-nba-stats-token` = 'true',
  `X-NewRelic-ID` = 'VQECWF5UChAHUlNTBwgBVw==',
  `User-Agent` = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36',
  `x-nba-stats-origin` = 'stats',
  `Sec-Fetch-Site` = 'same-origin',
  `Sec-Fetch-Mode` = 'cors',
  `Referer` = 'https://stats.nba.com/players/shooting/',
  `Accept-Encoding` = 'gzip, deflate, br',
  `Accept-Language` = 'en-US,en;q=0.9'
)

params = list(
  `College` = '',
  `Conference` = '',
  `Country` = '',
  `DateFrom` = '',
  `DateTo` = '',
  `DistanceRange` = '5ft Range',
  `Division` = '',
  `DraftPick` = '',
  `DraftYear` = '',
  `GameScope` = '',
  `GameSegment` = '',
  `Height` = '',
  `LastNGames` = '0',
  `LeagueID` = '00',
  `Location` = '',
  `MeasureType` = 'Base',
  `Month` = '0',
  `OpponentTeamID` = '0',
  `Outcome` = '',
  `PORound` = '0',
  `PaceAdjust` = 'N',
  `PerMode` = 'PerGame',
  `Period` = '0',
  `PlayerExperience` = '',
  `PlayerPosition` = '',
  `PlusMinus` = 'N',
  `Rank` = 'N',
  `Season` = '2019-20',
  `SeasonSegment` = '',
  `SeasonType` = 'Regular Season',
  `ShotClockRange` = '',
  `StarterBench` = '',
  `TeamID` = '0',
  `VsConference` = '',
  `VsDivision` = '',
  `Weight` = ''
)

res <- httr::GET(url = 'https://stats.nba.com/stats/leaguedashplayershotlocations', httr::add_headers(.headers=headers), query = params)
res <- httr::GET(url = url, httr::add_headers(.headers=headers))

json_resp <- jsonlite::fromJSON(content(res, "text"))
frame <- data.frame(json_resp$resultSets$rowSet)

# res <- httr::GET(url = 'https://stats.nba.com/stats/leaguedashplayershotlocations?College=&Conference=&Country=&DateFrom=&DateTo=&DistanceRange=5ft+Range&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2019-20&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight=', httr::add_headers(.headers=headers), httr::set_cookies(.cookies = cookies))