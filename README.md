sports
======

Scripts for the collection and analysis of NBA play-by-play data.

Data collection and formatting is divided into three Python scripts:
1. nbagames.py : Given a range of dates, formulates a text list of all NBA games in the range
2. nbaplays.py : Given a list of games, query the NBA.com database for play-by-play data on each one.
3. nbastats.py : Given a list of play-by-play data, convert certain events (shots attempted/made, fouls, turnovers) into point process data (i.e. list of binary outcomes over time [0 0 0 0 1 ...])
  
Further point process analysis relies on the Point Process Toolbox (pp_tools) repo. This includes data visualization, model estimation, model validation, etc.
