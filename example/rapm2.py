# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 16:04:20 2016

@author: gmf
"""

# Import modules
import re
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

# only need once:
#import pymongo
#events_db.create_index([('SEASON_ID', pymongo.ASCENDING), ('GAME_ID', pymongo.ASCENDING)])

#season_year = '1996-97'
#season_year = '2014-15'
season_year = '2015-16'

seasonid = '002' + season_year.split('-')[0][2:]
all_players = bb.get_players_season(season=season_year)
teams = bb.get_teams_current()
Nplayers = len(all_players)
Nteams = len(teams)

#%% Fit team RPM models

def fit_team_rpm(team_id):
  team_players = bb.get_team_roster(team_id, season=season_year)
  Nteam_players = len(team_players)
  team_dict = bb.zip2(team_players['PLAYER_ID'].values, range(Nteam_players))
  
  # Offense
  off_possessions = events_db.find({'$and': [{'SEASON_ID': seasonid}, {'OFF_TEAM':team_id}]},
                      {'OFF_PLAYERS':1, 'DEF_PLAYERS':1, 'SCORE_CHANGE':1, 'DURATION':1}
                      )
  N_off = off_possessions.count()
  X_off = np.zeros([N_off, Nteam_players])
  y_off = np.zeros([N_off])
  
  i=0
  for s in off_possessions:
    
    try:
      o_idx = [team_dict[p] for p in s['OFF_PLAYERS']]
    except:
      S = np.copy(s['OFF_PLAYERS'])
      S = S[S>0]
      S = np.setdiff1d(S, S[np.where([p not in team_dict.keys() for p in S])[0]])
      o_idx = [team_dict[p] for p in S]
    
    # If poss_type == 2: change i
    # 
    X_off[i, o_idx] = 1
    y_off[i] += s['SCORE_CHANGE']
    i+=1
    
  m_off = slm.Ridge(alpha=3000)
  m_off.fit_intercept = False
  m_off = m_off.fit(X_off, y_off)
  
  # Defense
  def_possessions = events_db.find({'$and': [{'SEASON_ID': seasonid}, {'DEF_TEAM':team_id}]},
                      {'OFF_PLAYERS':1, 'DEF_PLAYERS':1, 'SCORE_CHANGE':1, 'DURATION':1}
                      )
  N_def = def_possessions.count()
  X_def = np.zeros([N_def, Nteam_players])
  y_def = np.zeros([N_def])
  
  i=0
  for s in def_possessions:
    
    try:
      d_idx = [team_dict[p] for p in s['DEF_PLAYERS']]
    except:
      S = np.copy(s['DEF_PLAYERS'])
      S = S[S>0]
      S = np.setdiff1d(S, S[np.where([p not in team_dict.keys() for p in S])[0]])
      d_idx = [team_dict[p] for p in S]
      
    X_def[i, d_idx] = -1
    y_def[i] = s['SCORE_CHANGE']
    i+=1
  
  m_def = slm.Ridge(alpha=3000)
  m_def.fit_intercept = False
  m_def = m_def.fit(X_def, y_def)

  team_players['ORtg'] = np.round( m_off.coef_ * 100, 2)
  team_players['DRtg'] = np.round( m_def.coef_ * 100, 2)
  team_players['NetRtg'] = team_players['ORtg'] + team_players['DRtg']
  team_players['O_Poss'] = np.sum(X_off,0)
  team_players['D_Poss'] = np.sum(np.abs(X_def),0)
  team_players['Points_Est'] = np.round(team_players['ORtg']/100.0 * team_players['O_Poss'])
  team_players['Points_Opp'] = np.round(team_players['DRtg']/100.0 * team_players['D_Poss'])
  team_players['Net_Points'] = team_players['Points_Est'] + team_players['Points_Opp']
  
  #return team_players.sort(columns='Net_Points',ascending=False)[['PLAYER', 'ORtg', 'DRtg', 'NetRtg', 'O_Poss', 'D_Poss', 'Net_Points']]
  #return team_players.sort(columns='Net_Points',ascending=False)[['PLAYER', 'ORtg', 'DRtg', 'NetRtg', 'O_Poss', 'Points_Est', 'Net_Points']]
  return team_players.sort(columns='Net_Points',ascending=False)[['PLAYER', 'ORtg', 'DRtg', 'NetRtg', 'O_Poss', 'Points_Est','Net_Points']]

#%% Print models

m = pd.DataFrame()
i=0
for team_id in teams['TEAM_ID'].values:
  print '\n'
  m1 = fit_team_rpm(team_id)
  print m1
  m = pd.concat((m,m1))
  i+=1
m = m.reset_index()

#print m[m['O_Poss']>=2000].sort(columns='NetRtg',ascending=False)[0:60]
#print m[m['O_Poss']>=2000].sort(columns='Net_Points',ascending=False)[0:60]
#print m[m['O_Poss']>=2000].sort(columns='Net_Points',ascending=True)[0:60]

#print m[m['O_Poss']>=2000].sort(columns='ORtg',ascending=False)[0:60]
#print m[m['O_Poss']>=2000].sort(columns='ORtg',ascending=True)[0:60]
#print m[m['O_Poss']>=2000].sort(columns='DRtg',ascending=False)[0:60]
#print m[m['O_Poss']>=2000].sort(columns='DRtg',ascending=True)[0:60]

#print m[m['O_Poss']>=2000].sort(columns='Points_Est',ascending=False)[['PLAYER','Points_Est']][0:60]