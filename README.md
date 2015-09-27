# Scripts to scrape and analyze basketball data.

Sample data available at the URL provided in the repo!

Scripts perform data scraping of various websites and run machine learning methods on the resulting data.

Most recent data collection scripts pull JSON (using the requests module) via the NBA's API. For instance, this simple call gets regular season data for the 2014-15 season:
  
    python savejson.py 00214

For each game, four JSON files are created:

    bs_GAMEID.json : Box score
    pbp_GAMEID.json : Play-by-play
    shots_GAMEID.json : Shot chart
    sv_GAMEID.json : SportVu data (if available/selected)

where GAMEID is a 10-digit code, XXXYYGGGGG, where XXX refers to a season prefix, YY is the season year (e.g. 14 for 2014-15), and GGGGG refers to the game number (1-1230 for a full 30-team regular season). Season prefixes are...

    001 : Pre Season
    002 : Regular Season
    003 : All-Star
    004 : Post Season
    
=======

Older data collection scripts parse HTML (using modules re, BeautifulSoup, etc.) into CSV and include:

1. nbagames.py : Given a range of dates & season code (e.g. 00214 = 2014-15 regular season), formulates a text list of all NBA games in the range

2. nbascores.py : Given a list of games, queries NBA.com and writes box score data for each one. Also can query vegasinsider.com to get moneyline odds for each game.

3. nbaplays.py : Given a list of games, queries NBA.com and writes play-by-play data for each one.

4. nbastats.py : Given a list of play-by-play data, convert certain events (shots attempted/made, fouls, turnovers) into point process data (i.e. list of binary outcomes over time [0 0 0 0 1 ...])

=======

Analysis scripts apply machine learning techniques to the resulting data in Python, Matlab, and R. Some simple examples are shown in iPython Notebooks.
