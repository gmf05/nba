# Scripts to scrape and analyze basketball data.


Data collection is done via savejson.py, which can be run via the command line:
  
    python savejson.py 00214
  

This example gets regular season data for the 2014-15 season. For each game, it creates 3 JSON files:

    bs_GAMEID.json -- Box score
    pbp_GAMEID.json -- Play-by-play
    shots_GAMEID.json -- Shot chart
  

GAMEID is a 10-digit code: XXXYYGGGGG where XXX refers to a season prefix, YY is the season year (e.g. 14 for 2014-15), and GGGGG refers to the game number (1-1230 for a full 30-team regular season). Season prefixes are...

    001 = Pre Season
    002 = Regular Season
    003 = All-Star
    004 = Post Season


See folder json for sample data.

=======

Older data collection scripts parse HTML into CSV and include:

1. nbagames.py : Given a range of dates & season code (e.g. 00214 = 2014-15 regular season), formulates a text list of all NBA games in the range

2. nbascores.py : Given a list of games, queries NBA.com and writes box score data for each one. Also can query vegasinsider.com to get moneyline odds for each game.

3. nbaplays.py : Given a list of games, queries NBA.com and writes play-by-play data for each one.

4. nbastats.py : Given a list of play-by-play data, convert certain events (shots attempted/made, fouls, turnovers) into point process data (i.e. list of binary outcomes over time [0 0 0 0 1 ...])

=======

Point process analysis is implemented in Matlab scripts and relies on the Point Process Toolbox (pp_tools) repo. This includes methods for data visualization, model estimation, model validation, etc.

Other learning methods are implemented in R scripts and include logistic regression, decision trees, K-nearest neighbors, and K-means clustering.
