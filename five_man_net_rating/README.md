# 5 Man Lineup Net Rating Are Bad

I've never really thought about 5 man unit net ratings until this year. I've always heard them brought up by various
talking headers and occasionally a stats person will say they are small sample size theater, but in general they've been
outside my focus. This year I've started to see these numbers pop up as a way to say "See our new starting lineup with
newly acquired players A and B is dominating" or "Wow what a terrible move signing player C, they are dragging down the closing lineup".
The problem with making these judgements is that they are based on something like a 55 possession sample. Using points per 100 possession
on less than 100 possessions is insanity, especially when a single basket changes Net Rating by 2-3 points at 100 possessions.

## 5 Man Units Are Almost All Small Sample

#### 2019-20 (December 10, 2019)
Let's start with the current season. Through December 10th the stats for
the number of offensive and defensive possessions played 5 man units are shown below.

```
The minimum number of possessions played: 0, the maximum number of possessions played 806 <br />
82 out of 5440 lineups have played more than 100 possessions together <br />
3 out of 5440 lineups have played more than 500 possessions together <br />
0 out of 5440 lineups have played more than 1000 possessions together <br />
The average number of possessions a lineup has played together is: 12.52 <br />

The minimum number of possessions faced: 0, the maximum number of possessions faced 809 <br />
82 out of 5440 lineups have faced more than 100 possessions together <br />
3 out of 5440 lineups have played more than 500 possessions together <br />
0 out of 5440 lineups have played more than 1000 possessions together <br />
The average number of possessions a lineup has faced together is: 12.52 <br />
```

This means that the MOST played 5 man unit in the league at this point has
played about 8 games worth of possessions, only 3 linupes have played the equivalent of 5 games together,
and only 82 lineups have played the equivalent or more of 1 game of
possession. Below is a histogram of
how many lineup possession. It's pretty easy to tell that the vast majority
of lineups at this point have less than 20 possessions.

![2019-20 5 Man Unit Possession Histogram](plots/PossessionHisto1920.png)
![2019-20 5 Man Unit Possession Histogram (<100 Possession)](plots/PossessionHisto1920_100.png)

#### 2018-19 Full Season
Since we know that at ~25 games only a handful of 5 man units have played
enough possessions to make it so that a single basket doesn't have a large impact on the net rating
we should look at a full season.
```
The minimum number of possessions played: 0, the maximum number of possessions played 2110 <br />
371 out of 15297 lineups have played more than 100 possessions together <br />
40 out of 15297 lineups have played more than 500 possessions together <br />
15 out of 15297 lineups have played more than 1000 possessions together <br />
The average number of possessions a lineup has played together is: 16.92 <br />

The minimum number of possessions faced: 0, the maximum number of possessions faced 2122 <br />
371 out of 15297 lineups have faced more than 100 possessions together <br />
40 out of 15297 lineups have played more than 500 possessions together <br />
15 out of 15297 lineups have played more than 1000 possessions together <br />
The average number of possessions a lineup has faced together is: 16.92 <br />
```

From the histograms below and from the numbers above, we can see that the distribution is about the same.
We now have 2.5% of all 5 man units with at least 100 possessions played and the average is up to ~17 possessions.
The most played lineup has about 21 games worth of possessions and it's net rating would no longer be impacted by a large run.
Only 40 lineups have played the equivalent of 5 games together and only 15 have played the equivalent of 10 games.

![2018-19 5 Man Unit Possession Histogram](plots/PossessionHisto1819.png)
![2018-19 5 Man Unit Possession Histogram (<100 Possession)](plots/PossessionHisto1819_100.png)

Even by the end of a season, we only have a handful of 5 man units whose net rating we could discuss as any indication of
talent and even then we are only looking at 10 games worth of possessions.
How much can you tell about a team from the net rating after 10 games?

## Small Sample Means Each Event Can Have Dramatic Impact

Now that we know that 5 Man Units are all pretty much small sample size
theater, let's look at the impact a single offensive and defensive
possession have on net rating.

Let us assume that we have a 5 man unit that has a league average net rating after N possession.
What would the result of possession N+1 have on the lineups net rating?
Below there is a chart showing the results of this idea. If a 5 man unit
has played 99 offensive and defensive possessions and on offensive
possession 100 they miss a shot and their opponent gets the rebound and then hits a 3,
that is a -3 swing in the lineups net rating!
A single trip up and down the court has that big of an impact.


![1 Possession Swing](plots/OnePossessionSwing.png)

## Your Favorite Teams Most Played Lineup is a 15 point run away from Glory/Disaster

### 76ers
![76ers](plots/76ers.png)

### Bucks
![Bucks](plots/Bucks.png)

### Bulls
![Bulls](plots/Bulls.png)

### Clippers
![Clippers](plots/Clippers.png)

### Grizzlies
![Grizzlies](plots/Grizzlies.png)

### Hawks
![Hawks](plots/Hawks.png)

### Heat
![Heat](plots/Heat.png)

### Hornets
![Hornets](plots/Hornets.png)

### Jazz
![Jazz](plots/Jazz.png)

### Kings
![Kings](plots/Kings.png)

### Knicks
![Knicks](plots/Knicks.png)

### Lakers
![Lakers](plots/Lakers.png)

### Magic
![Magic](plots/Magic.png)

### Mavericks
![Mavericks](plots/Mavericks.png)

### Nuggets
![Nuggets](plots/Nuggets.png)

### Pelicans
![Pelicans](plots/Pelicans.png)

### Raptors
![Raptors](plots/Raptors.png)

### Rockets
![Rockets](plots/Rockets.png)

### Spurs
![Spurs](plots/Spurs.png)

### Suns
![Suns](plots/Suns.png)

### Thunder
![Thunder](plots/Thunder.png)

### Timberwolves
![Timberwolves](plots/Timberwolves.png)

### Trail Blazers
![Trail Blazers](plots/Trail_Blazers.png)

### Warriors
![Warriors](plots/Warriors.png)

### Wizards
![Wizards](plots/Wizards.png)

