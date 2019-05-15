## Parsing Play by Play - Analyze the Play by Play Data:
This is the first step in building a play by play parser. This tutorial
will continue to be updated as I write the Play by Play parser tutorial.

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
by the nba has 5 (11 if you include player ids) columns that tell
you exactly what happened. Those columns are:
1. `EVENTMSGTYPE`           - The event type
2. `EVENTMSGACTIONTYPE`     - The event sub type
3. `HOMEDESCRIPTION`        - The home team description of the event
4. `NEUTRALDESCRIPTION`     - The neutral description of the event
5. `VISITORDESCRIPTION`     - The away team description of the event

In this tutorial we will take an example of each
`EVENTMSGTYPE` and `EVENTMSGACTIONTYPE` combination and use the
`HOMEDESCRIPTION`, `NEUTRALDESCRIPTION` and `VISITORDESCRIPTION` to determine
exactly what each `EVENTMSGTYPE` and `EVENTMSGACTIONTYPE`


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
play_by_play_for_analysis = play_by_play[['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE', 'HOMEDESCRIPTION', 'NEUTRALDESCRIPTION', 'VISITORDESCRIPTION']]
play_by_play_for_analysis = play_by_play_for_analysis.fillna('')
```

Generate a single joined description using all 3 description columns and
only reduce our selection to just the `EVENTMSGTYPE` `EVENTMSGACTIONTYPE`
and `DESCRIPTION` columns
```
play_by_play_for_analysis['DESCRIPTION'] = play_by_play_for_analysis['HOMEDESCRIPTION'] + ' ' + play_by_play_for_analysis['NEUTRALDESCRIPTION'] + ' ' + play_by_play_for_analysis['VISITORDESCRIPTION']
play_by_play_for_analysis = play_by_play_for_analysis[['EVENTMSGTYPE', 'EVENTMSGACTIONTYPE','DESCRIPTION']]
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
    EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION
0              1                   1       Smith  3PT Jump Shot (3 PTS) (James 3 AST)
1              1                   2  Young 13 Running Jump Shot (14 PTS) (Livingsto...
2              1                   3                       Horford 14 Hook Shot (4 PTS)
3              1                   5              Brown 2 Layup (12 PTS) (Irving 4 AST)
4              1                   6     Rose 1 Driving Layup (7 PTS) (Crowder 1 AST)
5              1                   7                              Capela 1 Dunk (8 PTS)
6              1                   9                      Gordon 1 Driving Dunk (7 PTS)
7              1                  41   Thompson 1 Running Layup (4 PTS) (James 4 AST)
8              1                  43  Thompson  Alley Oop Layup (2 PTS) (Smith 1 AST)
9              1                  44    Crowder 1 Reverse Layup (9 PTS) (James 6 AST)
10             1                  47             Wade 11 Turnaround Jump Shot (7 PTS)
11             1                  50                    James 2 Running Dunk (16 PTS)
12             1                  51        Barton 1 Reverse Dunk (7 PTS) (Jokic 3 AST)
13             1                  52      Tatum 2 Alley Oop Dunk (4 PTS) (Irving 6 AST)
14             1                  57  Fournier 7 Driving Hook Shot (2 PTS) (Payton 1...
15             1                  58           Curry 12 Turnaround Hook Shot (15 PTS)
16             1                  63    Hayward 9 Fadeaway Jumper (2 PTS) (Horford 2...
17             1                  66               Augustin 12 Jump Bank Shot (7 PTS)
18             1                  67    Griffin 7 Hook Bank Shot (27 PTS) (Williams ...
19             1                  71                Cousins 2 Finger Roll Layup (9 PTS)
20             1                  72                     Love 1 Putback Layup (4 PTS)
21             1                  73    Mbah a Moute 2 Driving Reverse Layup (2 PTS)...
22             1                  74    Richardson 3 Running Reverse Layup (10 PTS) ...
23             1                  75        Gordon 2 Driving Finger Roll Layup (15 PTS)
24             1                  76     Oladipo 1 Running Finger Roll Layup (17 PTS)
25             1                  78             Smith 13 Floating Jump Shot (10 PTS)
26             1                  79                 Irving 16 Pullup Jump Shot (6 PTS)
27             1                  80              Irving 18 Step Back Jump Shot (9 PTS)
28             1                  86  Wade 12 Turnaround Fadeaway (2 PTS) (James 1 A...
29             1                  87                  Drummond 1 Putback Dunk (6 PTS)
30             1                  93    Felder 6 Driving Bank Hook Shot (2 PTS) (Lop...
31             1                  96  Valanciunas 1 Turnaround Bank Hook Shot (19 PT...
32             1                  97                    Mozgov 1 Tip Layup Shot (2 PTS)
33             1                  98    Brown 1 Cutting Layup Shot (14 PTS) (Horford...
34             1                  99  James 1 Cutting Finger Roll Layup Shot (6 PTS)...
35             1                 100  Martin  Running Alley Oop Layup Shot (4 PTS) (...
36             1                 101     James 10 Driving Floating Jump Shot (12 PTS)
37             1                 102  Durant 10 Driving Floating Bank Jump Shot (15 ...
38             1                 103    Redick 26 3PT Running Pull-Up Jump Shot (3 PTS)
39             1                 104         Brooks 14 Step Back Bank Jump Shot (2 PTS)
40             1                 105    Smart 13 Turnaround Fadeaway Bank Jump Shot ...
41             1                 106  Chandler 1 Running Alley Oop Dunk Shot (2 PTS)...
42             1                 107                   Brooks 1 Tip Dunk Shot (6 PTS)
43             1                 108  Green 3 Cutting Dunk Shot (4 PTS) (James 8 AST)
44             1                 109  Noel 1 Driving Reverse Dunk Shot (2 PTS) (Barn...
45             1                 110        Brown 1 Running Reverse Dunk Shot (5 PTS)

```
From the above data it is can be inferred that `EVENTMSGTYPE=1` is a `Made Shot`
and `EVENTMSGACTIONTYPE` represents the various types of shots

### EVENTMSGTYPE = 2
```
    EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION
46             2                   1                        MISS Brown 26 3PT Jump Shot
47             2                   2                   MISS Harden 10 Running Jump Shot
48             2                   3                            MISS Capela 6 Hook Shot
49             2                   5            MISS Wade 2 Layup  Baynes BLOCK (1 BLK)
50             2                   6                         MISS Smart 2 Driving Layup
51             2                   7                               MISS Harris 1 Dunk
52             2                   9                          MISS Brown 1 Driving Dunk
53             2                  41                        MISS Rose 1 Running Layup
54             2                  43                  MISS Thompson 2 Alley Oop Layup
55             2                  44                         MISS Brown 2 Reverse Layup
56             2                  47             MISS Crowder 13 Turnaround Jump Shot
57             2                  50   Chriss BLOCK (2 BLK)  MISS Brewer 2 Running Dunk
58             2                  51   Gasol BLOCK (1 BLK)  MISS Plumlee 1 Reverse Dunk
59             2                  52                   MISS Drummond 2 Alley Oop Dunk
60             2                  57                   MISS Horford 8 Driving Hook Shot
61             2                  58               MISS Simmons 13 Turnaround Hook Shot
62             2                  63                     MISS Wade 15 Fadeaway Jumper
63             2                  66                    MISS Williams 15 Jump Bank Shot
64             2                  67                      MISS Lopez 3 Hook Bank Shot
65             2                  71                    MISS Olynyk 4 Finger Roll Layup
66             2                  72                         MISS Brown 1 Putback Layup
67             2                  73               MISS Curry 2 Driving Reverse Layup
68             2                  74                 MISS Allen 2 Running Reverse Layup
69             2                  75               MISS Lin 1 Driving Finger Roll Layup
70             2                  76           MISS Evans 1 Running Finger Roll Layup
71             2                  78                MISS Jackson 6 Floating Jump Shot
72             2                  79                      MISS Smart 4 Pullup Jump Shot
73             2                  80                 MISS Irving 19 Step Back Jump Shot
74             2                  86           MISS James 17 Turnaround Fadeaway Shot
75             2                  87                      MISS Porzingis 3 Putback Dunk
76             2                  93              MISS Mahinmi 5 Driving Bank Hook Shot
77             2                  96     MISS Connaughton 3 Turnaround Bank Hook Shot
78             2                  97                       MISS Wade 1 Tip Layup Shot
79             2                  98  James BLOCK (1 BLK)  MISS Tatum 3 Cutting Layu...
80             2                  99      MISS Mills 2 Cutting Finger Roll Layup Shot
81             2                 100        MISS James 1 Running Alley Oop Layup Shot
82             2                 101          MISS Wade 13 Driving Floating Jump Shot
83             2                 102     MISS Green 7 Driving Floating Bank Jump Shot
84             2                 103     MISS Gordon 26 3PT Running Pull-Up Jump Shot
85             2                 104            MISS Harden 13 Step Back Bank Jump Shot
86             2                 105  MISS Nowitzki 9 Turnaround Fadeaway Bank Jump ...
87             2                 106         MISS Kuzma 1 Running Alley Oop Dunk Shot
88             2                 107                      MISS Swanigan 3 Tip Dunk Shot
89             2                 108                   MISS Chriss  Cutting Dunk Shot
90             2                 109  MISS Mark Morris 3 Driving Reverse Dunk Shot  ...

```
From the above data it is can be inferred that `EVENTMSGTYPE=2` is a `Missed Shot`
and `EVENTMSGACTIONTYPE` represents the various types of shots

### EVENTMSGTYPE = 3
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                      DESCRIPTION
91              3                  10                  Brown Free Throw 1 of 1 (7 PTS)
92              3                  11                 Rose Free Throw 1 of 2 (5 PTS)
93              3                  12                    MISS Rose Free Throw 2 of 2
94              3                  13                    MISS Walker Free Throw 1 of 3
95              3                  14                 Walker Free Throw 2 of 3 (5 PTS)
96              3                  15                 Walker Free Throw 3 of 3 (6 PTS)
97              3                  16              Irving Free Throw Technical (7 PTS)
98              3                  18      Durant Free Throw Flagrant 1 of 2 (8 PTS)
99              3                  19      Durant Free Throw Flagrant 2 of 2 (9 PTS)
100             3                  20         Tatum Free Throw Flagrant 1 of 1 (4 PTS)
101             3                  21       Prince Free Throw Technical 1 of 2 (4 PTS)
102             3                  22       Prince Free Throw Technical 2 of 2 (5 PTS)
103             3                  25    VanVleet Free Throw Clear Path 1 of 2 (7 PTS)
104             3                  26    VanVleet Free Throw Clear Path 2 of 2 (6 PTS)
105             3                  27    Fournier Free Throw Flagrant 1 of 3 (6 PTS)
```
From the above data it is can be inferred that `EVENTMSGTYPE=3` is a `FreeThrow`
and `EVENTMSGACTIONTYPE` represents the various types of freethrows.
One thing to note here is that the `EVENTMSGACTIONTYPE` does NOT indicate 
if the freethrow was made of missed.If you want to determine the result 
of the freethrow, you will need to search the description for `MISS`


### EVENTMSGTYPE = 4
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                      DESCRIPTION
106             4                   0  Crowder REBOUND (Off:1 Def:1)
107             4                   1                  Celtics Rebound
```
From the above data it is can be inferred that `EVENTMSGTYPE=4` is a `Rebound`
and `EVENTMSGACTIONTYPE` tells you if it is a player rebound or team rebound. 
One thing to note here is that the `EVENTMSGACTIONTYPE` does NOT indicate 
if the rebound was an offensive or defensive rebound. If you want to 
determine if the rebound is offensive or defensive you will need to go
find the last shot taken before the rebound and check to see if the team
of the player who took the shot is the same as the player who gathered
the rebound.


### EVENTMSGTYPE = 5
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION
108             5                   0                        Holiday No Turnover (P3.T9)
109             5                   1  Love Bad Pass Turnover (P1.T5)  Irving STEAL (...
110             5                   2  Shumpert STEAL (1 STL)  Baynes Lost Ball Turno...
111             5                   4                  Wade Traveling Turnover (P1.T2)
112             5                   6           Irving Double Dribble Turnover (P2.T3)
113             5                   7      Waiters Discontinue Dribble Turnover (P3.T11)
114             5                   8        Tucker 3 Second Violation Turnover (P3.T12)
115             5                   9         Raptors Turnover: 5 Second Violation (T#2)
116             5                  10      HORNETS Turnover: 8 Second Violation (T#12)
117             5                  11                 Celtics Turnover: Shot Clock (T#4)
118             5                  12                Galloway Inbound Turnover (P1.T6)
119             5                  13                   Lamb Backcourt Turnover (P2.T17)
120             5                  15    Gobert Offensive Goaltending Turnover (P1.T4)
121             5                  17           Felicio Lane Violation Turnover (P3.T14)
122             5                  18      Drummond Jump Ball Violation Turnover (P2.T4)
123             5                  19  Patterson Kicked Ball Violation Turnover (P1.T...
124             5                  20            Bradley Illegal Assist Turnover (P2.T7)
125             5                  21                     Brown Palming Turnover (P1.T1)
126             5                  33           Pachulia Punched Ball Turnover (P1.T2)
127             5                  35        Gordon Basket from Below Turnover (P1.T9)
128             5                  36          Bayless Illegal Screen Turnover (P1.T6)
129             5                  37            Green Offensive Foul Turnover (P1.T3)
130             5                  39          Brown Step Out of Bounds Turnover (P2.T2)
131             5                  40   James Out of Bounds Lost Ball Turnover (P1.T4)
132             5                  44           SPURS Turnover: Too Many Players (T#2)
133             5                  45    Smart Out of Bounds - Bad Pass Turnover Turn...
```
From the above data it is can be inferred that `EVENTMSGTYPE=5` is a `Turnover`
and `EVENTMSGACTIONTYPE` tells you the type of `Turnover`.

### EVENTMSGTYPE = 6
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION
134             6                   0                        Holiday NO.FOUL (P1.PN) (.)
135             6                   1                    Irving P.FOUL (P1.T4) (B.Forte)
136             6                   2                    Baynes S.FOUL (P1.T3) (M.Smith)
137             6                   3               Tatum L.B.FOUL (P2.T3) (M.McCutchen)
138             6                   4                     Baynes OFF.Foul (P4) (B.Forte)
139             6                   5               Shumpert IN.FOUL (P3.PN) (M.Smith)
140             6                   6    Speights AWAY.FROM.PLAY.FOUL (P1.T3) (K.Cutler)
141             6                   9                   Griffin C.P.FOUL (P1.T4) (J.Orr)
142             6                  10
143             6                  11                    Irving T.FOUL (P2.T1) (M.Smith)
144             6                  12     Grant Non-Unsportsmanlike (P0.T1) (D.Stafford)
145             6                  13  Valanciunas HANGING.TECH.FOUL (P0.T2) (C.Kirkl...
146             6                  14      Tucker FLAGRANT.FOUL.TYPE1 (P1.T4) (T.Maddox)
147             6                  15       Anthony FLAGRANT.FOUL.TYPE2 (P4.PN) (R.Mott)
148             6                  16
149             6                  17  CAVALIERS T.Foul (Def. 3 Sec Love ) (M.McCutch...
150             6                  18
151             6                  19                   Harris Taunting (P1.T3) (L.Wood)
152             6                  26  Green Offensive Charge Foul (P1.T4) (M.McCutch...
153             6                  27  Stephenson Personal Block Foul (P1.T1) (D.Coll...
154             6                  28      LeVert Personal Take Foul (P3.PN) (D.Collins)
155             6                  29  Oladipo Shooting Block Foul (P2.T3) (T.Brother...
156             6                  30
```
From the above data it is can be inferred that `EVENTMSGTYPE=6` is a `Foul`
and `EVENTMSGACTIONTYPE` tells you the type of `Foul`.

### EVENTMSGTYPE = 7
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                        DESCRIPTION
157             7                   1
158             7                   2    Capela Violation:Defensive Goaltending (R.Ga...
159             7                   3                          Walker Violation:Lane (.)
160             7                   4                 Ulis Violation:Jump Ball (K.Scott)
161             7                   5             Baynes Violation:Kicked Ball (B.Forte)
162             7                   6                  Maker Violation:Double Lane (.)
 ```
From the above data it is can be inferred that `EVENTMSGTYPE=7` is a `Violation`
and `EVENTMSGACTIONTYPE` tells you the type of `Violation`.

### EVENTMSGTYPE = 8
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE               DESCRIPTION
163             8                   0  SUB: Shumpert FOR Rose
  ```
From the above data it is can be inferred that `EVENTMSGTYPE=8` is a `Substitution`
and `EVENTMSGACTIONTYPE` provides no value.

### EVENTMSGTYPE = 9
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                 DESCRIPTION
164             9                   1    Celtics Timeout: Regular (Reg.1 Short 0)
```
From the above data it is can be inferred that `EVENTMSGTYPE=9` is a `Timeout`
and `EVENTMSGACTIONTYPE` provides no value.

### EVENTMSGTYPE = 10
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE                                  DESCRIPTION
165            10                   0  Jump Ball Love vs. Horford: Tip to Irving
  ```
From the above data it is can be inferred that `EVENTMSGTYPE=10` is a `Jumpball`
and `EVENTMSGACTIONTYPE` provides no value.

### EVENTMSGTYPE = 11
```
     EVENTMSGTYPE  EVENTMSGACTIONTYPE             DESCRIPTION
166            11                   4    Curry Ejection:Other
```
From the above data it is can be inferred that `EVENTMSGTYPE=11` is an `Ejection`
and `EVENTMSGACTIONTYPE` provides no value.

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
