# Scripts to scrape and analyze basketball data.

Scripts scrape NBA.com, Sports Illustrated, etc. for various data and run machine learning methods on the resulting data.

Newest data collection scripts, savejson.py and others, pull JSON (using the requests module) via the NBA API. For instance, this simple call gets regular season data for the 2014-15 season:
  
    python savejson.py 00214

For each game, up to four JSON files are created:

    bs_GAMEID.json : Box score
    pbp_GAMEID.json : Play-by-play
    shots_GAMEID.json : Shot chart
    sv_GAMEID.json : SportVu data (if available/selected. *WARNING*: These are sampled at 25 Hz & sometimes redundant, therefore somewhat large : ~100 GB for an entire regular season.

GAMEID is a 10-digit code used by the NBA: XXXYYGGGGG, where XXX refers to a season prefix, YY is the season year (e.g. 14 for 2014-15), and GGGGG refers to the game number (1-1230 for a full 30-team regular season).
Season prefixes are...

    001 : Pre Season
    002 : Regular Season
    003 : All-Star
    004 : Post Season

Sample data collected using savejson are available at the url listed in the repo. By downloading, SportVu & play-by-play data for game '0021400001' (the first game of the 2014-15 regular season : ORL @ NOP 10/28/2014), one can reproduce the movie rebound1.mp4.

=======

Older data collection scripts parse HTML (using modules re, BeautifulSoup, etc.) into CSV and include:

1. nbagames.py : Given a range of dates & season code (e.g. 00214 = 2014-15 regular season), formulates a text list of all NBA games in the range

2. nbascores.py : Given a list of games, queries NBA.com and writes box score data for each one. Also can query vegasinsider.com to get moneyline odds for each game.

3. nbaplays.py : Given a list of games, queries NBA.com and writes play-by-play data for each one.

4. nbastats.py : Given a list of play-by-play data, convert certain events (shots attempted/made, fouls, turnovers) into point process data (i.e. list of binary outcomes over time [0 0 0 0 1 ...])

=======

Analysis scripts apply machine learning techniques to the resulting data in Python, Matlab, and R. Some simple examples are shown in IPython Notebooks.
