# Scripts to scrape and analyze basketball data.

Scripts scrape NBA.com, Sports Illustrated, etc. and analyze the resulting data.

Newest data collection scripts pull JSON (using the requests module) via the NBA API. For instance, this simple call gets data for the first game of the 2014-15 regular season:

    python savejson.py 0021400001
  
where 0021400001 is a 10-digit game identifier used by the NBA: XXXYYGGGGG, where XXX refers to a season prefix, YY is the season year (e.g. 14 for 2014-15), and GGGGG refers to the game number (1-1230 for a full 30-team regular season).

Season prefixes are...

    001 : Pre Season
    002 : Regular Season
    003 : All-Star
    004 : Post Season

Hence 0021400001 is the first game of the 2014-15 regular season.

To create a list of regular season games, call:

    python savegames.py 2015

Then, after commenting/uncommenting the appropriate lines in savejson main(), pass that game list to savejson.py:

    python savejson.py gamelist_00214.csv

This will loop over all games in the given list and save data for each one.

Some sample data collected using savejson are available at the url listed in the repo. A full list of regular season game for season 1996-97 to 2014-15 is also available.

=======

Older data collection scripts parse HTML (using modules re, BeautifulSoup, etc.) into CSV and include:

1. nbagames.py : Given a range of dates & season code (e.g. 00214 = 2014-15 regular season), formulates a text list of all NBA games in the range. [REPLACED BY savegames.py]

2. nbascores.py : Given a list of games, queries NBA.com and writes box score data for each one. Also can query vegasinsider.com to get moneyline odds for each game. [REPLACED BY savejson.py]

3. nbaplays.py : Given a list of games, queries NBA.com and writes play-by-play data for each one. [REPLACED BY savejson.py]

4. nbastats.py : Given a list of play-by-play data, convert certain events (shots attempted/made, fouls, turnovers) into point process data (i.e. list of binary outcomes over time [0 0 0 0 1 ...]) [REPLACED BY parse_possession.py]

=======

Analysis scripts apply machine learning techniques to the resulting data in Python, Matlab, and R. Some simple examples are shown in IPython Notebooks.
