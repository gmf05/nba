nba analysis code
======

Scripts for the collection and analysis of NBA box score & play-by-play data.

Data collection and output is divided into four Python scripts:

1. nbagames.py : Given a range of dates & season code (e.g. 00214 = 2014-15 regular season), formulates a text list of all NBA games in the range

2. nbascores.py : Given a list of games, queries NBA.com and writes box score data for each one.

3. nbaplays.py : Given a list of games, queries NBA.com and writes play-by-play data for each one.

4. nbastats.py : Given a list of play-by-play data, convert certain events (shots attempted/made, fouls, turnovers) into point process data (i.e. list of binary outcomes over time [0 0 0 0 1 ...])


Further point process analysis is implemented through Matlab scripts and relies on the Point Process Toolbox (pp_tools) repo. This includes methods for data visualization, model estimation, model validation, etc.

Other learning methods are implemented in R scripts and include logistic regression, decision trees, K-nearest neighbors, and K-means clustering.
