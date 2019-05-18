## Parsing Play by Play - Analyze the Play by Play Data:
This is the first step in building a play by play parser. This tutorial
will continue to be updated as I write the Play by Play parser tutorial.

If you see any issues or think there is a better way to do something,
don't hesitate to open a PR, submit an issue, or reach out to me directly

### Getting the data:
For this tutorial I will provide a subset of columns from the 2017-18
season's play by play data (entire season).
If you are interested in downloading the data for yourself you can
follow the section on downloading play by play data in the
[Players on Court Tutorial](../players_on_court).

### Analyzing the data:

The play by play data is divided into rows of events, with each row
representing a single action in the game. Multiple events can make
up a possession, so if we want to parse out the possessions, we need to
determine where the cutoffs are. Luckily the play by play data provided
by the nba has 5 (17 if you include player ids) columns that tell
you exactly what happened. Those columns are:
1. `EVENTMSGTYPE`           - The event type
2. `EVENTMSGACTIONTYPE`     - The event sub type
3. `HOMEDESCRIPTION`        - The home team description of the event
4. `NEUTRALDESCRIPTION`     - The neutral description of the event
5. `VISITORDESCRIPTION`     - The away team description of the event
6. `PLAYER1_ID`             - The id of the first player involved
7. `PLAYER1_NAME`           - The name of the first player involved
8. `PLAYER1_TEAM_ID`        - The team id of the first player involved
9. `PLAYER1_TEAM_NICKNAME`  - The team name of the first player involved
10. `PLAYER2_ID`             - The id of the second player involved
11. `PLAYER2_NAME`           - The name of the second player involved
12. `PLAYER2_TEAM_ID`        - The team id of the second player involved
13. `PLAYER2_TEAM_NICKNAME`  - The team name of the second player involved
14. `PLAYER3_ID`             - The id of the third player involved
15. `PLAYER3_NAME`           - The name of the third player involved
16. `PLAYER3_TEAM_ID`        - The team id of the third player involved
17. `PLAYER3_TEAM_NICKNAME`  - The team name of the third player involved

In this tutorial we will take an example of each
`EVENTMSGTYPE` and `EVENTMSGACTIONTYPE` combination and use the
`HOMEDESCRIPTION`, `NEUTRALDESCRIPTION` and `VISITORDESCRIPTION` to determine
exactly what each `EVENTMSGTYPE` and `EVENTMSGACTIONTYPE`mean. We will
also use the player ids and player team ids to help determine who is
involved with each event and how they are involved.


### The Code:
As with every python tutorial I write, we will start off with the setting
up the script.

The first thing we need to do is import the necessary libraries.
Pandas will be used for reading and processing the data.
os will be used for relative pathing to the input and output files
```
import pandas as pd
import os
```


Set the max number of columns and the column width for easier readability
```
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
```

Get the directory of the current file so that we can get the path to
the desired input and output files
```
dirname = os.path.dirname(__file__)
input_file = os.path.join(dirname, 'data/2017-18_pbp.csv')
output_file = os.path.join(dirname, 'data/unique_pbp.csv')
```

Read the play by play data <br>
Select only the columns we need <br>
Fill all NaNs with empty strings. We need to do this because by default pandas will fill Nulls with NaN
```
play_by_play = pd.read_csv(input_file)
play_by_play_for_analysis = play_by_play[['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE', 'HOMEDESCRIPTION', 'NEUTRALDESCRIPTION',
                                          'VISITORDESCRIPTION','PLAYER1_ID', 'PLAYER1_NAME', 'PLAYER1_TEAM_ID',
                                          'PLAYER1_TEAM_NICKNAME', 'PLAYER2_ID', 'PLAYER2_NAME', 'PLAYER2_TEAM_ID',
                                          'PLAYER2_TEAM_NICKNAME', 'PLAYER3_ID', 'PLAYER3_NAME', 'PLAYER3_TEAM_ID',
                                          'PLAYER3_TEAM_NICKNAME']]
play_by_play_for_analysis = play_by_play_for_analysis.fillna('')
```

Generate a single joined description using all 3 description columns and
only reduce our selection to just the `EVENTMSGTYPE` `EVENTMSGACTIONTYPE`
and `DESCRIPTION` columns
```
play_by_play_for_analysis['DESCRIPTION'] = play_by_play_for_analysis['HOMEDESCRIPTION'] + ' ' + play_by_play_for_analysis['NEUTRALDESCRIPTION'] + ' ' + play_by_play_for_analysis['VISITORDESCRIPTION']
play_by_play_for_analysis = play_by_play_for_analysis[['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE','DESCRIPTION','PLAYER1_ID',
                                                       'PLAYER1_NAME', 'PLAYER1_TEAM_ID', 'PLAYER1_TEAM_NICKNAME',
                                                       'PLAYER2_ID', 'PLAYER2_NAME', 'PLAYER2_TEAM_ID',
                                                       'PLAYER2_TEAM_NICKNAME', 'PLAYER3_ID', 'PLAYER3_NAME',
                                                       'PLAYER3_TEAM_NICKNAME']]
```

Write a function that takes in a group of rows and only return the first
row.
```
def take_one(group):
    return group.head(1)
```

Group our dataframe by `EVENTMSGTYPE` and `EVENTMSGACTIONTYPE`. This will
generate a series of grouped objects where each group only contains
descriptions asigned to a single `EVENTMSGTYPE` and `EVENTMSGACTIONTYPE`
combination. We then apply our take_one function to each group to pair
down the groups. Afterwards we reset the index so that our output only
has the columns `EVENTMSGTYPE` `EVENTMSGACTIONTYPE` and `DESCRIPTION`

```
unique_pbp = play_by_play_for_analysis.groupby(by=['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE'])
                                      .apply(take_one)
                                      .reset_index(drop=True)
```

Print out the groupings and save them in a csv.
```
for event in unique_pbp['EVENTMSGTYPE'].unique():
    print(unique_pbp[unique_pbp['EVENTMSGTYPE'] == event])


unique_pbp.to_csv(output_file, index=False)
```


The result is shown below. From this data we can determine what each
`EVENTMSGTYPE` and `EVENTMSGACTIONTYPE` means.

### EVENTMSGTYPE = 1
```
    EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION  PLAYER1_ID       PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID      PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID PLAYER3_NAME PLAYER3_TEAM_NICKNAME
0              1                   1       Smith  3PT Jump Shot (3 PTS) (James 3 AST)          2747           JR Smith     1.61061e+09             Cavaliers        2544      LeBron James     1.61061e+09             Cavaliers           0
1              1                   2  Young 13 Running Jump Shot (14 PTS) (Livingsto...      201156         Nick Young     1.61061e+09              Warriors        2733  Shaun Livingston     1.61061e+09              Warriors           0
2              1                   3                       Horford 14 Hook Shot (4 PTS)      201143         Al Horford     1.61061e+09               Celtics           0                                                                   0
3              1                   5              Brown 2 Layup (12 PTS) (Irving 4 AST)     1627759       Jaylen Brown     1.61061e+09               Celtics      202681      Kyrie Irving     1.61061e+09               Celtics           0
4              1                   6     Rose 1 Driving Layup (7 PTS) (Crowder 1 AST)        201565       Derrick Rose     1.61061e+09             Cavaliers      203109       Jae Crowder     1.61061e+09             Cavaliers           0
5              1                   7                              Capela 1 Dunk (8 PTS)      203991       Clint Capela     1.61061e+09               Rockets           0                                                                   0
6              1                   9                      Gordon 1 Driving Dunk (7 PTS)      201569        Eric Gordon     1.61061e+09               Rockets           0                                                                   0
7              1                  41   Thompson 1 Running Layup (4 PTS) (James 4 AST)        202684   Tristan Thompson     1.61061e+09             Cavaliers        2544      LeBron James     1.61061e+09             Cavaliers           0
8              1                  43  Thompson  Alley Oop Layup (2 PTS) (Smith 1 AST)        202684   Tristan Thompson     1.61061e+09             Cavaliers        2747          JR Smith     1.61061e+09             Cavaliers           0
9              1                  44    Crowder 1 Reverse Layup (9 PTS) (James 6 AST)        203109        Jae Crowder     1.61061e+09             Cavaliers        2544      LeBron James     1.61061e+09             Cavaliers           0
10             1                  47             Wade 11 Turnaround Jump Shot (7 PTS)          2548        Dwyane Wade     1.61061e+09             Cavaliers           0                                                                   0
11             1                  50                    James 2 Running Dunk (16 PTS)          2544       LeBron James     1.61061e+09             Cavaliers           0                                                                   0
12             1                  51        Barton 1 Reverse Dunk (7 PTS) (Jokic 3 AST)      203115        Will Barton     1.61061e+09               Nuggets      203999      Nikola Jokic     1.61061e+09               Nuggets           0
13             1                  52      Tatum 2 Alley Oop Dunk (4 PTS) (Irving 6 AST)     1628369       Jayson Tatum     1.61061e+09               Celtics      202681      Kyrie Irving     1.61061e+09               Celtics           0
14             1                  57  Fournier 7 Driving Hook Shot (2 PTS) (Payton 1...      203095      Evan Fournier     1.61061e+09                 Magic      203901     Elfrid Payton     1.61061e+09                 Magic           0
15             1                  58           Curry 12 Turnaround Hook Shot (15 PTS)        201939      Stephen Curry     1.61061e+09              Warriors           0                                                                   0
16             1                  63    Hayward 9 Fadeaway Jumper (2 PTS) (Horford 2...      202330     Gordon Hayward     1.61061e+09               Celtics      201143        Al Horford     1.61061e+09               Celtics           0
17             1                  66               Augustin 12 Jump Bank Shot (7 PTS)        201571      D.J. Augustin     1.61061e+09                 Magic           0                                                                   0
18             1                  67    Griffin 7 Hook Bank Shot (27 PTS) (Williams ...      201933      Blake Griffin     1.61061e+09              Clippers      101150      Lou Williams     1.61061e+09              Clippers           0
19             1                  71                Cousins 2 Finger Roll Layup (9 PTS)      202326   DeMarcus Cousins     1.61061e+09              Pelicans           0                                                                   0
20             1                  72                     Love 1 Putback Layup (4 PTS)        201567         Kevin Love     1.61061e+09             Cavaliers           0                                                                   0
21             1                  73    Mbah a Moute 2 Driving Reverse Layup (2 PTS)...      201601   Luc Mbah a Moute     1.61061e+09               Rockets        2772      Trevor Ariza     1.61061e+09               Rockets           0
22             1                  74    Richardson 3 Running Reverse Layup (10 PTS) ...     1626196    Josh Richardson     1.61061e+09                  Heat      201949     James Johnson     1.61061e+09                  Heat           0
23             1                  75        Gordon 2 Driving Finger Roll Layup (15 PTS)      201569        Eric Gordon     1.61061e+09               Rockets           0                                                                   0
24             1                  76     Oladipo 1 Running Finger Roll Layup (17 PTS)        203506     Victor Oladipo     1.61061e+09                Pacers           0                                                                   0
25             1                  78             Smith 13 Floating Jump Shot (10 PTS)          2747           JR Smith     1.61061e+09             Cavaliers           0                                                                   0
26             1                  79                 Irving 16 Pullup Jump Shot (6 PTS)      202681       Kyrie Irving     1.61061e+09               Celtics           0                                                                   0
27             1                  80              Irving 18 Step Back Jump Shot (9 PTS)      202681       Kyrie Irving     1.61061e+09               Celtics           0                                                                   0
28             1                  86  Wade 12 Turnaround Fadeaway (2 PTS) (James 1 A...        2548        Dwyane Wade     1.61061e+09             Cavaliers        2544      LeBron James     1.61061e+09             Cavaliers           0
29             1                  87                  Drummond 1 Putback Dunk (6 PTS)        203083     Andre Drummond     1.61061e+09               Pistons           0                                                                   0
30             1                  93    Felder 6 Driving Bank Hook Shot (2 PTS) (Lop...     1627770         Kay Felder     1.61061e+09                 Bulls      201577       Robin Lopez     1.61061e+09                 Bulls           0
31             1                  96  Valanciunas 1 Turnaround Bank Hook Shot (19 PT...      202685  Jonas Valanciunas     1.61061e+09               Raptors           0                                                                   0
32             1                  97                    Mozgov 1 Tip Layup Shot (2 PTS)      202389     Timofey Mozgov     1.61061e+09                  Nets           0                                                                   0
33             1                  98    Brown 1 Cutting Layup Shot (14 PTS) (Horford...     1627759       Jaylen Brown     1.61061e+09               Celtics      201143        Al Horford     1.61061e+09               Celtics           0
34             1                  99  James 1 Cutting Finger Roll Layup Shot (6 PTS)...        2544       LeBron James     1.61061e+09             Cavaliers      201565      Derrick Rose     1.61061e+09             Cavaliers           0
35             1                 100  Martin  Running Alley Oop Layup Shot (4 PTS) (...     1626185      Jarell Martin     1.61061e+09             Grizzlies      203516   James Ennis III     1.61061e+09             Grizzlies           0
36             1                 101     James 10 Driving Floating Jump Shot (12 PTS)          2544       LeBron James     1.61061e+09             Cavaliers           0                                                                   0
37             1                 102  Durant 10 Driving Floating Bank Jump Shot (15 ...      201142       Kevin Durant     1.61061e+09              Warriors      203110    Draymond Green     1.61061e+09              Warriors           0
38             1                 103    Redick 26 3PT Running Pull-Up Jump Shot (3 PTS)      200755          JJ Redick     1.61061e+09                 76ers           0                                                                   0
39             1                 104         Brooks 14 Step Back Bank Jump Shot (2 PTS)     1628415      Dillon Brooks     1.61061e+09             Grizzlies           0                                                                   0
40             1                 105    Smart 13 Turnaround Fadeaway Bank Jump Shot ...      203935       Marcus Smart     1.61061e+09               Celtics           0                                                                   0
41             1                 106  Chandler 1 Running Alley Oop Dunk Shot (2 PTS)...        2199     Tyson Chandler     1.61061e+09                  Suns      203933         TJ Warren     1.61061e+09                  Suns           0
42             1                 107                   Brooks 1 Tip Dunk Shot (6 PTS)       1628415      Dillon Brooks     1.61061e+09             Grizzlies           0                                                                   0
43             1                 108  Green 3 Cutting Dunk Shot (4 PTS) (James 8 AST)        201145         Jeff Green     1.61061e+09             Cavaliers        2544      LeBron James     1.61061e+09             Cavaliers           0
44             1                 109  Noel 1 Driving Reverse Dunk Shot (2 PTS) (Barn...      203457       Nerlens Noel     1.61061e+09             Mavericks      203084   Harrison Barnes     1.61061e+09             Mavericks           0
45             1                 110        Brown 1 Running Reverse Dunk Shot (5 PTS)       1627759       Jaylen Brown     1.61061e+09               Celtics           0                                                                   0

```
From the above data it is can be inferred that `EVENTMSGTYPE=1` is a `Made Shot`
and `EVENTMSGACTIONTYPE` represents the various types of shots. It can also
be seen that player 1 is the shooter and player 2 is the player who
provided the assist, assuming there is one.

### EVENTMSGTYPE = 2
```
    EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION  PLAYER1_ID        PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID     PLAYER3_NAME PLAYER3_TEAM_NICKNAME
46             2                   1                        MISS Brown 26 3PT Jump Shot     1627759        Jaylen Brown     1.61061e+09               Celtics           0                                                              0
47             2                   2                   MISS Harden 10 Running Jump Shot      201935        James Harden     1.61061e+09               Rockets           0                                                              0
48             2                   3                            MISS Capela 6 Hook Shot      203991        Clint Capela     1.61061e+09               Rockets           0                                                              0
49             2                   5            MISS Wade 2 Layup  Baynes BLOCK (1 BLK)        2548         Dwyane Wade     1.61061e+09             Cavaliers           0                                                         203382      Aron Baynes               Celtics
50             2                   6                         MISS Smart 2 Driving Layup      203935        Marcus Smart     1.61061e+09               Celtics           0                                                              0
51             2                   7                               MISS Harris 1 Dunk        202699       Tobias Harris     1.61061e+09               Pistons           0                                                              0
52             2                   9                          MISS Brown 1 Driving Dunk     1627759        Jaylen Brown     1.61061e+09               Celtics           0                                                              0
53             2                  41                        MISS Rose 1 Running Layup        201565        Derrick Rose     1.61061e+09             Cavaliers           0                                                              0
54             2                  43                  MISS Thompson 2 Alley Oop Layup        202684    Tristan Thompson     1.61061e+09             Cavaliers           0                                                              0
55             2                  44                         MISS Brown 2 Reverse Layup     1627759        Jaylen Brown     1.61061e+09               Celtics           0                                                              0
56             2                  47             MISS Crowder 13 Turnaround Jump Shot        203109         Jae Crowder     1.61061e+09             Cavaliers           0                                                              0
57             2                  50   Chriss BLOCK (2 BLK)  MISS Brewer 2 Running Dunk      201147        Corey Brewer     1.61061e+09                Lakers           0                                                        1627737  Marquese Chriss                  Suns
58             2                  51   Gasol BLOCK (1 BLK)  MISS Plumlee 1 Reverse Dunk      203101       Miles Plumlee     1.61061e+09                 Hawks           0                                                         201188       Marc Gasol             Grizzlies
59             2                  52                   MISS Drummond 2 Alley Oop Dunk        203083      Andre Drummond     1.61061e+09               Pistons           0                                                              0
60             2                  57                   MISS Horford 8 Driving Hook Shot      201143          Al Horford     1.61061e+09               Celtics           0                                                              0
61             2                  58               MISS Simmons 13 Turnaround Hook Shot     1627732         Ben Simmons     1.61061e+09                 76ers           0                                                              0
62             2                  63                     MISS Wade 15 Fadeaway Jumper          2548         Dwyane Wade     1.61061e+09             Cavaliers           0                                                              0
63             2                  66                    MISS Williams 15 Jump Bank Shot      101107     Marvin Williams     1.61061e+09               Hornets           0                                                              0
64             2                  67                      MISS Lopez 3 Hook Bank Shot        201572         Brook Lopez     1.61061e+09                Lakers           0                                                              0
65             2                  71                    MISS Olynyk 4 Finger Roll Layup      203482        Kelly Olynyk     1.61061e+09                  Heat           0                                                              0
66             2                  72                         MISS Brown 1 Putback Layup     1627759        Jaylen Brown     1.61061e+09               Celtics           0                                                              0
67             2                  73               MISS Curry 2 Driving Reverse Layup        201939       Stephen Curry     1.61061e+09              Warriors           0                                                              0
68             2                  74                 MISS Allen 2 Running Reverse Layup        2754          Tony Allen     1.61061e+09              Pelicans           0                                                              0
69             2                  75               MISS Lin 1 Driving Finger Roll Layup      202391          Jeremy Lin     1.61061e+09                  Nets           0                                                              0
70             2                  76           MISS Evans 1 Running Finger Roll Layup        201936        Tyreke Evans     1.61061e+09             Grizzlies           0                                                              0
71             2                  78                MISS Jackson 6 Floating Jump Shot        202704      Reggie Jackson     1.61061e+09               Pistons           0                                                              0
72             2                  79                      MISS Smart 4 Pullup Jump Shot      203935        Marcus Smart     1.61061e+09               Celtics           0                                                              0
73             2                  80                 MISS Irving 19 Step Back Jump Shot      202681        Kyrie Irving     1.61061e+09               Celtics           0                                                              0
74             2                  86           MISS James 17 Turnaround Fadeaway Shot          2544        LeBron James     1.61061e+09             Cavaliers           0                                                              0
75             2                  87                      MISS Porzingis 3 Putback Dunk      204001  Kristaps Porzingis     1.61061e+09                Knicks           0                                                              0
76             2                  93              MISS Mahinmi 5 Driving Bank Hook Shot      101133         Ian Mahinmi     1.61061e+09               Wizards           0                                                              0
77             2                  96     MISS Connaughton 3 Turnaround Bank Hook Shot       1626192     Pat Connaughton     1.61061e+09         Trail Blazers           0                                                              0
78             2                  97                       MISS Wade 1 Tip Layup Shot          2548         Dwyane Wade     1.61061e+09             Cavaliers           0                                                              0
79             2                  98  James BLOCK (1 BLK)  MISS Tatum 3 Cutting Layu...     1628369        Jayson Tatum     1.61061e+09               Celtics           0                                                           2544     LeBron James             Cavaliers
80             2                  99      MISS Mills 2 Cutting Finger Roll Layup Shot        201988         Patty Mills     1.61061e+09                 Spurs           0                                                              0
81             2                 100        MISS James 1 Running Alley Oop Layup Shot       1628455          Mike James     1.61061e+09                  Suns           0                                                              0
82             2                 101          MISS Wade 13 Driving Floating Jump Shot          2548         Dwyane Wade     1.61061e+09             Cavaliers           0                                                              0
83             2                 102     MISS Green 7 Driving Floating Bank Jump Shot        201145          Jeff Green     1.61061e+09             Cavaliers           0                                                              0
84             2                 103     MISS Gordon 26 3PT Running Pull-Up Jump Shot        203932        Aaron Gordon     1.61061e+09                 Magic           0                                                              0
85             2                 104            MISS Harden 13 Step Back Bank Jump Shot      201935        James Harden     1.61061e+09               Rockets           0                                                              0
86             2                 105  MISS Nowitzki 9 Turnaround Fadeaway Bank Jump ...        1717       Dirk Nowitzki     1.61061e+09             Mavericks           0                                                              0
87             2                 106         MISS Kuzma 1 Running Alley Oop Dunk Shot       1628398          Kyle Kuzma     1.61061e+09                Lakers           0                                                              0
88             2                 107                      MISS Swanigan 3 Tip Dunk Shot     1628403      Caleb Swanigan     1.61061e+09         Trail Blazers           0                                                              0
89             2                 108                   MISS Chriss  Cutting Dunk Shot       1627737     Marquese Chriss     1.61061e+09                  Suns           0                                                              0
90             2                 109  MISS Mark Morris 3 Driving Reverse Dunk Shot  ...      202693     Markieff Morris     1.61061e+09               Wizards           0                                                        1626257      Salah Mejri             Mavericks

```
From the above data it is can be inferred that `EVENTMSGTYPE=2` is a `Missed Shot`
and `EVENTMSGACTIONTYPE` represents the various types of shots. It can
be seen that player 1 is the player who took the shot and player 3 is the
player who blocked the shot assuming there was a block.

### EVENTMSGTYPE = 3
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                      DESCRIPTION  PLAYER1_ID    PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID PLAYER3_NAME PLAYER3_TEAM_NICKNAME
91              3                  10                  Brown Free Throw 1 of 1 (7 PTS)     1627759    Jaylen Brown     1.61061e+09               Celtics           0                                                              0
92              3                  11                 Rose Free Throw 1 of 2 (5 PTS)        201565    Derrick Rose     1.61061e+09             Cavaliers           0                                                              0
93              3                  12                    MISS Rose Free Throw 2 of 2        201565    Derrick Rose     1.61061e+09             Cavaliers           0                                                              0
94              3                  13                    MISS Walker Free Throw 1 of 3      202689    Kemba Walker     1.61061e+09               Hornets           0                                                              0
95              3                  14                 Walker Free Throw 2 of 3 (5 PTS)      202689    Kemba Walker     1.61061e+09               Hornets           0                                                              0
96              3                  15                 Walker Free Throw 3 of 3 (6 PTS)      202689    Kemba Walker     1.61061e+09               Hornets           0                                                              0
97              3                  16              Irving Free Throw Technical (7 PTS)      202681    Kyrie Irving     1.61061e+09               Celtics           0                                                              0
98              3                  18      Durant Free Throw Flagrant 1 of 2 (8 PTS)        201142    Kevin Durant     1.61061e+09              Warriors           0                                                              0
99              3                  19      Durant Free Throw Flagrant 2 of 2 (9 PTS)        201142    Kevin Durant     1.61061e+09              Warriors           0                                                              0
100             3                  20         Tatum Free Throw Flagrant 1 of 1 (4 PTS)     1628369    Jayson Tatum     1.61061e+09               Celtics           0                                                              0
101             3                  21       Prince Free Throw Technical 1 of 2 (4 PTS)     1627752  Taurean Prince     1.61061e+09                 Hawks           0                                                              0
102             3                  22       Prince Free Throw Technical 2 of 2 (5 PTS)     1627752  Taurean Prince     1.61061e+09                 Hawks           0                                                              0
103             3                  25    VanVleet Free Throw Clear Path 1 of 2 (7 PTS)     1627832   Fred VanVleet     1.61061e+09               Raptors           0                                                              0
104             3                  26    VanVleet Free Throw Clear Path 2 of 2 (6 PTS)     1627832   Fred VanVleet     1.61061e+09               Raptors           0                                                              0
105             3                  27    Fournier Free Throw Flagrant 1 of 3 (6 PTS)        203095   Evan Fournier     1.61061e+09                 Magic           0                                                              0
```
From the above data it is can be inferred that `EVENTMSGTYPE=3` is a `FreeThrow`
and `EVENTMSGACTIONTYPE` represents the various types of freethrows.
One thing to note here is that the `EVENTMSGACTIONTYPE` does NOT indicate 
if the freethrow was made of missed.If you want to determine the result 
of the freethrow, you will need to search the description for `MISS`

Player 1 is the player who took the freethrows


### EVENTMSGTYPE = 4
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                      DESCRIPTION  PLAYER1_ID PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID PLAYER3_NAME PLAYER3_TEAM_NICKNAME
106             4                   0  Crowder REBOUND (Off:1 Def:1)        203109  Jae Crowder     1.61061e+09             Cavaliers           0                                                              0
107             4                   1                  Celtics Rebound  1610612738                                                              0                                                              0
```
From the above data it is can be inferred that `EVENTMSGTYPE=4` is a `Rebound`
and `EVENTMSGACTIONTYPE` tells you if it is a player rebound or team rebound. 
One thing to note here is that the `EVENTMSGACTIONTYPE` does NOT indicate 
if the rebound was an offensive or defensive rebound. If you want to 
determine if the rebound is offensive or defensive you will need to go
find the last shot taken before the rebound and check to see if the team
of the player who took the shot is the same as the player who gathered
the rebound.

Player 1 is the player who secured the rebound


### EVENTMSGTYPE = 5
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION  PLAYER1_ID       PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID   PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID PLAYER3_NAME PLAYER3_TEAM_NICKNAME
108             5                   0                        Holiday No Turnover (P3.T9)      201950       Jrue Holiday     1.61061e+09              Pelicans           0                                                                0
109             5                   1  Love Bad Pass Turnover (P1.T5)  Irving STEAL (...      201567         Kevin Love     1.61061e+09             Cavaliers      202681   Kyrie Irving     1.61061e+09               Celtics           0
110             5                   2  Shumpert STEAL (1 STL)  Baynes Lost Ball Turno...      203382        Aron Baynes     1.61061e+09               Celtics      202697  Iman Shumpert     1.61061e+09             Cavaliers           0
111             5                   4                  Wade Traveling Turnover (P1.T2)          2548        Dwyane Wade     1.61061e+09             Cavaliers           0                                                                0
112             5                   6           Irving Double Dribble Turnover (P2.T3)        202681       Kyrie Irving     1.61061e+09               Celtics           0                                                                0
113             5                   7      Waiters Discontinue Dribble Turnover (P3.T11)      203079       Dion Waiters     1.61061e+09                  Heat           0                                                                0
114             5                   8        Tucker 3 Second Violation Turnover (P3.T12)      200782          PJ Tucker     1.61061e+09               Rockets           0                                                                0
115             5                   9         Raptors Turnover: 5 Second Violation (T#2)  1610612761                                                                    0                                                                0
116             5                  10      HORNETS Turnover: 8 Second Violation (T#12)    1610612766                                                                    0                                                                0
117             5                  11                 Celtics Turnover: Shot Clock (T#4)  1610612738                                                                    0                                                                0
118             5                  12                Galloway Inbound Turnover (P1.T6)        204038  Langston Galloway     1.61061e+09               Pistons           0                                                                0
119             5                  13                   Lamb Backcourt Turnover (P2.T17)      203087        Jeremy Lamb     1.61061e+09               Hornets           0                                                                0
120             5                  15    Gobert Offensive Goaltending Turnover (P1.T4)        203497        Rudy Gobert     1.61061e+09                  Jazz           0                                                                0
121             5                  17           Felicio Lane Violation Turnover (P3.T14)     1626245  Cristiano Felicio     1.61061e+09                 Bulls           0                                                                0
122             5                  18      Drummond Jump Ball Violation Turnover (P2.T4)      203083     Andre Drummond     1.61061e+09               Pistons           0                                                                0
123             5                  19  Patterson Kicked Ball Violation Turnover (P1.T...      202335  Patrick Patterson     1.61061e+09               Thunder           0                                                                0
124             5                  20            Bradley Illegal Assist Turnover (P2.T7)      202340      Avery Bradley     1.61061e+09               Pistons           0                                                                0
125             5                  21                     Brown Palming Turnover (P1.T1)     1627759       Jaylen Brown     1.61061e+09               Celtics           0                                                                0
126             5                  33           Pachulia Punched Ball Turnover (P1.T2)          2585      Zaza Pachulia     1.61061e+09              Warriors           0                                                                0
127             5                  35        Gordon Basket from Below Turnover (P1.T9)        201569        Eric Gordon     1.61061e+09               Rockets           0                                                                0
128             5                  36          Bayless Illegal Screen Turnover (P1.T6)        201573     Jerryd Bayless     1.61061e+09                 76ers           0                                                                0
129             5                  37            Green Offensive Foul Turnover (P1.T3)        201145         Jeff Green     1.61061e+09             Cavaliers           0                                                                0
130             5                  39          Brown Step Out of Bounds Turnover (P2.T2)     1627759       Jaylen Brown     1.61061e+09               Celtics           0                                                                0
131             5                  40   James Out of Bounds Lost Ball Turnover (P1.T4)          2544       LeBron James     1.61061e+09             Cavaliers           0                                                                0
132             5                  44           SPURS Turnover: Too Many Players (T#2)    1610612759                                                                    0                                                                0
133             5                  45    Smart Out of Bounds - Bad Pass Turnover Turn...      203935       Marcus Smart     1.61061e+09               Celtics           0                                                                0

```
From the above data it is can be inferred that `EVENTMSGTYPE=5` is a `Turnover`
and `EVENTMSGACTIONTYPE` tells you the type of `Turnover`.

Player 1 is the player who committed the turnover and player 2 is the
player who caused the turnover if it was forced.

If the turnover is a "team turnover" then the player 1 id will be the
team id of the team that committed the turnover.

### EVENTMSGTYPE = 6
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION  PLAYER1_ID       PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID      PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID PLAYER3_NAME PLAYER3_TEAM_NICKNAME
134             6                   0                        Holiday NO.FOUL (P1.PN) (.)      203200     Justin Holiday     1.61061e+09                 Bulls           0                                                                   0
135             6                   1                    Irving P.FOUL (P1.T4) (B.Forte)      202681       Kyrie Irving     1.61061e+09               Celtics        2544      LeBron James     1.61061e+09             Cavaliers           0
136             6                   2                    Baynes S.FOUL (P1.T3) (M.Smith)      203382        Aron Baynes     1.61061e+09               Celtics      202684  Tristan Thompson     1.61061e+09             Cavaliers           0
137             6                   3               Tatum L.B.FOUL (P2.T3) (M.McCutchen)     1628369       Jayson Tatum     1.61061e+09               Celtics      201145        Jeff Green     1.61061e+09             Cavaliers           0
138             6                   4                     Baynes OFF.Foul (P4) (B.Forte)      203382        Aron Baynes     1.61061e+09               Celtics      202684  Tristan Thompson     1.61061e+09             Cavaliers           0
139             6                   5               Shumpert IN.FOUL (P3.PN) (M.Smith)        202697      Iman Shumpert     1.61061e+09             Cavaliers      203935      Marcus Smart     1.61061e+09               Celtics           0
140             6                   6    Speights AWAY.FROM.PLAY.FOUL (P1.T3) (K.Cutler)      201578  Marreese Speights     1.61061e+09                 Magic     1627790        Ante Zizic     1.61061e+09             Cavaliers           0
141             6                   9                   Griffin C.P.FOUL (P1.T4) (J.Orr)      201933      Blake Griffin     1.61061e+09              Clippers      201572       Brook Lopez     1.61061e+09                Lakers           0
142             6                  10                                                        1626202          Joe Young     1.61061e+09                Pacers      203894    Shabazz Napier     1.61061e+09         Trail Blazers           0
143             6                  11                    Irving T.FOUL (P2.T1) (M.Smith)      202681       Kyrie Irving     1.61061e+09               Celtics           0                                                                   0
144             6                  12     Grant Non-Unsportsmanlike (P0.T1) (D.Stafford)      203924       Jerami Grant     1.61061e+09               Thunder           0                                                                   0
145             6                  13  Valanciunas HANGING.TECH.FOUL (P0.T2) (C.Kirkl...      202685  Jonas Valanciunas     1.61061e+09               Raptors           0                                                                   0
146             6                  14      Tucker FLAGRANT.FOUL.TYPE1 (P1.T4) (T.Maddox)      200782          PJ Tucker     1.61061e+09               Rockets      201142      Kevin Durant     1.61061e+09              Warriors           0
147             6                  15       Anthony FLAGRANT.FOUL.TYPE2 (P4.PN) (R.Mott)        2546    Carmelo Anthony     1.61061e+09               Thunder      203994      Jusuf Nurkic     1.61061e+09         Trail Blazers           0
148             6                  16                                                           2730      Dwight Howard     1.61061e+09               Hornets      203961     Eric Moreland     1.61061e+09               Pistons           0
149             6                  17  CAVALIERS T.Foul (Def. 3 Sec Love ) (M.McCutch...      201567         Kevin Love     1.61061e+09             Cavaliers           0                                                                   0
150             6                  18                                                              0                                                                    0                                                                   0
151             6                  19                   Harris Taunting (P1.T3) (L.Wood)      202699      Tobias Harris     1.61061e+09               Pistons           0                                                                   0
152             6                  26  Green Offensive Charge Foul (P1.T4) (M.McCutch...      201145         Jeff Green     1.61061e+09             Cavaliers     1628400      Semi Ojeleye     1.61061e+09               Celtics           0
153             6                  27  Stephenson Personal Block Foul (P1.T1) (D.Coll...      202362   Lance Stephenson     1.61061e+09                Pacers     1626156   DAngelo Russell     1.61061e+09                  Nets           0
154             6                  28      LeVert Personal Take Foul (P3.PN) (D.Collins)     1627747       Caris LeVert     1.61061e+09                  Nets      201152    Thaddeus Young     1.61061e+09                Pacers           0
155             6                  29  Oladipo Shooting Block Foul (P2.T3) (T.Brother...      203506     Victor Oladipo     1.61061e+09                Pacers      202344     Trevor Booker     1.61061e+09                  Nets           0
156             6                  30                                                              0                                                                    0                                                                   0
```
From the above data it is can be inferred that `EVENTMSGTYPE=6` is a `Foul`
and `EVENTMSGACTIONTYPE` tells you the type of `Foul`.

Player 1 is the player who committed the foul, player 2 is the player
who was on the receiving end of the foul.

### EVENTMSGTYPE = 7
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION  PLAYER1_ID  PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID PLAYER3_NAME PLAYER3_TEAM_NICKNAME
157             7                   1                                                              0                                                               0                                                              0
158             7                   2    Capela Violation:Defensive Goaltending (R.Ga...      203991  Clint Capela     1.61061e+09               Rockets           0                                                              0
159             7                   3                          Walker Violation:Lane (.)      202689  Kemba Walker     1.61061e+09               Hornets           0                                                              0
160             7                   4                 Ulis Violation:Jump Ball (K.Scott)     1627755    Tyler Ulis     1.61061e+09                  Suns           0                                                              0
161             7                   5             Baynes Violation:Kicked Ball (B.Forte)      203382   Aron Baynes     1.61061e+09               Celtics           0                                                              0
162             7                   6                  Maker Violation:Double Lane (.)       1627748    Thon Maker     1.61061e+09                 Bucks           0                                                              0
 ```
From the above data it is can be inferred that `EVENTMSGTYPE=7` is a `Violation`
and `EVENTMSGACTIONTYPE` tells you the type of `Violation`.

Player 1 is the player who committed the violation

### EVENTMSGTYPE = 8
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE               DESCRIPTION  PLAYER1_ID  PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID   PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID PLAYER3_NAME PLAYER3_TEAM_NICKNAME
163             8                   0  SUB: Shumpert FOR Rose        201565  Derrick Rose     1.61061e+09             Cavaliers      202697  Iman Shumpert     1.61061e+09             Cavaliers           0

```
From the above data it is can be inferred that `EVENTMSGTYPE=8` is a `Substitution`
and `EVENTMSGACTIONTYPE` provides no value.

Player 1 is the player being subbed out, player 2 is the player being
subbed in.


### EVENTMSGTYPE = 9
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                 DESCRIPTION  PLAYER1_ID PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID PLAYER3_NAME PLAYER3_TEAM_NICKNAME
164             9                   1    Celtics Timeout: Regular (Reg.1 Short 0)  1610612738                                                              0                                                              0
```
From the above data it is can be inferred that `EVENTMSGTYPE=9` is a `Timeout`
and `EVENTMSGACTIONTYPE` provides no value.

Player 1 id is the team id of the team that called the time out

### EVENTMSGTYPE = 10
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                  DESCRIPTION  PLAYER1_ID PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID  PLAYER3_NAME PLAYER3_TEAM_NICKNAME
165            10                   0  Jump Ball Love vs. Horford: Tip to Irving        201567   Kevin Love     1.61061e+09             Cavaliers      201143   Al Horford     1.61061e+09               Celtics      202681  Kyrie Irving               Celtics
  ```
From the above data it is can be inferred that `EVENTMSGTYPE=10` is a `Jumpball`
and `EVENTMSGACTIONTYPE` provides no value.

Player 1 and Player 2 are the players involved in the jump ball. Player 3
is the player who recieved the jump ball.
### EVENTMSGTYPE = 11
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE             DESCRIPTION  PLAYER1_ID   PLAYER1_NAME PLAYER1_TEAM_ID PLAYER1_TEAM_NICKNAME  PLAYER2_ID PLAYER2_NAME PLAYER2_TEAM_ID PLAYER2_TEAM_NICKNAME  PLAYER3_ID PLAYER3_NAME PLAYER3_TEAM_NICKNAME
166            11                   4    Curry Ejection:Other      201939  Stephen Curry     1.61061e+09              Warriors           0                                                              0
```
From the above data it is can be inferred that `EVENTMSGTYPE=11` is an `Ejection`
and `EVENTMSGACTIONTYPE` provides no value.


Player 1 is the player who was ejected

### EVENTMSGTYPE = 12
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE DESCRIPTION
167            12                   0
```
Unfortunately there is no description here, but  `EVENTMSGTYPE=12`
represents the start of a period

### EVENTMSGTYPE = 13
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE DESCRIPTION
168            13                   0
```
Unfortunately there is no description here, but  `EVENTMSGTYPE=13`
represents the end of a period

### EVENTMSGTYPE = 14
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE DESCRIPTION
169            14                   0
170            14                   1
171            14                   2

```
Unfortunately there is no description here, but  `EVENTMSGTYPE=14`
is used as a catch all by the api for blank lines.

### Todo:
Include player ID and Team ID in order to show how to calculate offensive
and defensive rebounds.
