# -*- coding: utf-8 -*-
"""
Created on Fri Oct 28 16:18:59 2016

@author: gmf
"""

# Import modules
import numpy as np
import pandas as pd
import bb_tools as bb
#import statsmodels.api as sm
import sklearn.linear_model as slm
#from sklearn.feature_extraction import DictVectorizer # from RAPM tutorial

# Connect to MongoDB
from pymongo import MongoClient
client = MongoClient('localhost', 27117)
db = client['nba']
events_db = db['possessions']

def fit_team_rpm(team_id, season='2015-16'):
  seasonid = '002' + season[2:4]
  team_players = bb.get_team_roster(team_id, season=season)
  Nteam_players = len(team_players)
  team_dict = bb.zip2(team_players['PLAYER_ID'].values, range(Nteam_players))
  
  # Offense
  off_possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'OFFTEAM':team_id}, {'EVENTTYPE':{'$in':[1,2,3,5]}}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                      {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1}
                      )
  N_off = off_possessions.count()
  X_off = np.zeros([N_off, Nteam_players])
  y_off = np.zeros([N_off])
    
  i=0
  for s in off_possessions:
    
    try:
      o_idx = [team_dict[p] for p in s['OFFPLAYERS']]
    except:
      S = np.copy(s['OFFPLAYERS'])
      S = S[S>0]
      S = np.setdiff1d(S, S[np.where([p not in team_dict.keys() for p in S])[0]])
      o_idx = [team_dict[p] for p in S]
      
    X_off[i, o_idx] = 1
    y_off[i] = s['SCORECHANGE']
    i+=1
  
  m_off = slm.Ridge(alpha=750)
  m_off.fit_intercept = False
  m_off = m_off.fit(X_off, y_off)
  
  # Defense
  def_possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'DEFTEAM':team_id}, {'EVENTTYPE':{'$in':[1,2,3,5]}}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                      {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1}
                      )
  N_def = def_possessions.count()
  X_def = np.zeros([N_def, Nteam_players])
  y_def = np.zeros([N_def])
    
  i=0
  for s in def_possessions:
    
    try:
      d_idx = [team_dict[p] for p in s['DEFPLAYERS']]
    except:
      S = np.copy(s['DEFPLAYERS'])
      S = S[S>0]
      S = np.setdiff1d(S, S[np.where([p not in team_dict.keys() for p in S])[0]])
      d_idx = [team_dict[p] for p in S]
      
    X_def[i, d_idx] = -1
    y_def[i] = s['SCORECHANGE']
    i+=1
  
  m_def = slm.Ridge(alpha=750)
  m_def.fit_intercept = False
  m_def = m_def.fit(X_def, y_def)

  team_players['ORtg'] = np.round( m_off.coef_ * 100, 2)
  team_players['DRtg'] = np.round( m_def.coef_ * 100, 2)
  team_players['NetRtg'] = team_players['ORtg'] + team_players['DRtg']
  team_players['O_Poss'] = np.sum(X_off,0)
  team_players['D_Poss'] = np.sum(np.abs(X_def),0)
  team_players['O_Points'] = np.round(team_players['ORtg']/100.0 * team_players['O_Poss'])
  team_players['D_Points'] = np.round(team_players['DRtg']/100.0 * team_players['D_Poss'])
  team_players['Net_Points'] = team_players['O_Points'] + team_players['D_Points']
  
  return team_players.sort(columns='NetRtg',ascending=False)[['PLAYER', 'PLAYER_ID', 'ORtg', 'DRtg', 'NetRtg', 'O_Poss', 'D_Poss', 'O_Points', 'D_Points', 'Net_Points']]

#%%

all_players = bb.get_players_all()
all_players = all_players[[int(i)>=1996 for i in all_players['TO_YEAR'].values]]
Nplayers = len(all_players)

player_table = pd.DataFrame()
player_table['Name'] = all_players['DISPLAY_FIRST_LAST'].values
player_table['ID'] = all_players['PERSON_ID'].values
player_table['ORtg'] = 0
player_table['DRtg'] = 0 
player_table['Box'] = 0 # per game box score stats

teams = bb.get_teams_current()
Nteams = len(teams)

for season_year in range(1996, 2016):
  season_str = str(season_year) + '-' + str(season_year+1)[2:]
  teams_season = teams[[int(t)<=season_year for t in teams['START_YEAR'].values]]
  for nt,team in teams_season.iterrows():
    print season_str, team['TEAM_NAME'], team['TEAM_ID']
    m = fit_team_rpm(team['TEAM_ID'], season=season_str)
    # 
    idx = [np.where(player_table['ID']==p)[0][0] for p in m['PLAYER_ID'].values]
    # save results:
    #player_table.iloc[idx]
    
    # Also save box score totals    
    


#%%
# for each player in list
# bb.get_player_career(203087)
# # get relevant years (>= 1996), save stats (normalized per game??)
# 




