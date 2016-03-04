# Scripts to scrape and analyze basketball data.

Scripts scrape NBA.com, Sports Illustrated, etc. and analyze the resulting data.

Newest data collection scripts pull JSON (using the requests module) via the NBA API. For instance, this block of Python code saves data for the first game of the 2014-15 regular season:

    import bb_tools as bb
    gameid = '0021400001'
    bb.write_game_json(gameid) # save to disk (not necessary, but faster)
    box = bb.get_boxscore(gameid) # read from disk -- or web if not saved 
    pbp = bb.get_pbp(gameid)
    shots = bb.get_shots(gameid)
  
Data read/write paths are set in bb_tools.py.

The NBA's Game ID, 0021400001, is a 10-digit code: XXXYYGGGGG, where XXX refers to a season prefix, YY is the season year (e.g. 14 for 2014-15), and GGGGG refers to the game number (1-1230 for a full 30-team regular season).

Season prefixes are...

    001 : Pre Season
    002 : Regular Season
    003 : All-Star
    004 : Post Season

To save all data for the current season, run the following from the command line:

    python nbaupdate.py

To save data from previous seasons, you can pass an entire list of games. For example, the list of regular season games from 1996-97 to 2014-15 is provided in the repo.

    gamelist = bb.REPOHOME + '/data/csv/games_96-14.csv'
    bb.write_gamelist_json(gamelist)

=======

Older data collection scripts parse HTML (using modules re, BeautifulSoup, etc.) into CSV and include:

1. nbagames.py : Given a range of dates & season code (e.g. 00214 = 2014-15 regular season), formulates a text list of all NBA games in the range. [REPLACED BY savegames.py]

2. nbascores.py : Given a list of games, queries NBA.com and writes box score data for each one. Also can query vegasinsider.com to get moneyline odds for each game. [REPLACED BY savejson.py]

3. nbaplays.py : Given a list of games, queries NBA.com and writes play-by-play data for each one. [REPLACED BY savejson.py]

4. nbastats.py : Given a list of play-by-play data, convert certain events (shots attempted/made, fouls, turnovers) into point process data (i.e. list of binary outcomes over time [0 0 0 0 1 ...]) [REPLACED BY parse_possession.py]

=======

Analysis scripts apply machine learning techniques to the resulting data in Python, Matlab, and R. Some simple examples are shown in IPython Notebooks.
