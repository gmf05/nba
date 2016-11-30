#%%
import numpy as np
import bb_tools as bb

# DB
from pymongo import MongoClient
client = MongoClient('localhost', 27117)
db = client['nba']
events_db = db['possessions']

teams = bb.get_teams_current()

for n in range(30):
  t = teams.iloc[n]
  teamid = t['TEAM_ID']
    
  off_poss = events_db.find({'OFF_TEAM':teamid})
  def_poss = events_db.find({'DEF_TEAM':teamid})
  
  pts_scored = 0
  o_poss = 0
  for o in off_poss:
    o_poss+=1
    pts_scored += o['SCORE_CHANGE']
  
  pts_against = 0
  d_poss = 0
  for d in def_poss:
    d_poss+=1
    pts_against += d['SCORE_CHANGE']
    
  ortg = np.round(1.0*pts_scored / o_poss * 100, 1)
  drtg = np.round(1.0*pts_against / d_poss * 100, 1)

  poss = events_db.find({'OFF_TEAM':teamid})
  team_games = np.unique([o['GAME_ID'] for o in poss])  
  pace = np.zeros(len(team_games))  
  for n in range(len(team_games)):
    gameid = team_games[n]
    poss_n = events_db.find({'$and': [{'GAME_ID':gameid},{'OFF_TEAM':teamid}]})
    pace[n] = poss_n.count() * 2880.0 / bb.nsec_total_gameid(gameid)
  np.mean(pace)  
  
  print t['TEAM_CITY'],ortg,drtg,np.round(np.mean(pace),1)
  

#%% Benchmark SQL query for games against searching box scores

import psycopg2
import datetime
import pandas as pd
#import bb_tools as bb

conn = psycopg2.connect("user='postgres' password='docker' host='localhost'")

# Make list of game dates
# Should we attach as date data type to rows??
cur = conn.cursor()
cur.execute("SELECT game_code FROM nbaGames g where g.SEASON_ID=296")
G = cur.fetchall()
game_dates = [datetime.date(int(g[0][0:4]), int(g[0][4:6]), int(g[0][6:8])) for g in G]

# 
cur = conn.cursor()
# First get table structure (field names)
cur.execute("SELECT * FROM nbaPlayerSeasonTotals g where g.PLAYER_ID=1886;") 
#cur.execute("SELECT * FROM nbaPlayerSeasonTotals g where g.PLAYER_ID=1886;")
columns = ['player_id', 'season_id', 'age', 'gp', 'gs', 'min', 'fgm', 'fga', 'fg_pct',
           'fg3m', 'fg3a', 'fg3_pct', 'ftm', 'fta', 'ft_pct', 'oreb', 'dreb', 'reb',
           'ast', 'stl', 'blk', 'tov', 'pf', 'pts']
data = cur.fetchall()
df = pd.DataFrame(data=data, columns=columns)
