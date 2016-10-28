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
#events_db.create_index([('SEASONID', pymongo.ASCENDING), ('GAMEID', pymongo.ASCENDING)])

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
  off_possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'OFFTEAM':team_id}, {'EVENTTYPE':{'$in':[1,2,3,5]}}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                      {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1, 'DURATION':1}
                      )
  N_off = off_possessions.count()
  X_off = np.zeros([N_off, Nteam_players])
  y_off = np.zeros([N_off])
  z_off = np.zeros([N_off])
    
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
    #z_off[i] = s['DURATION']
    i+=1
    
  #m_off = slm.LassoCV() # L1 reg
  m_off = slm.Ridge(alpha=500)
  #m_off = slm.ElasticNetCV(l1_ratio = 0.8)
  m_off.fit_intercept = False
  m_off = m_off.fit(X_off, y_off)
  
  # Defense
  def_possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'DEFTEAM':team_id}, {'EVENTTYPE':{'$in':[1,2,3,5]}}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                      {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1, 'DURATION':1}
                      )
  N_def = def_possessions.count()
  X_def = np.zeros([N_def, Nteam_players])
  y_def = np.zeros([N_def])
  z_def = np.zeros([N_def])
    
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
    #z_def[i] = s['DURATION']
    i+=1
  
  #m_def = slm.LassoCV() # L1 reg
  m_def = slm.Ridge(alpha=750)
  #m_def = slm.ElasticNetCV(l1_ratio = 0.8)
  m_def.fit_intercept = False
  m_def = m_def.fit(X_def, y_def)

  team_players['ORtg'] = np.round( m_off.coef_ * 100, 2)
  team_players['DRtg'] = np.round( m_def.coef_ * 100, 2)
  team_players['NetRtg'] = team_players['ORtg'] + team_players['DRtg']
  team_players['O_Poss'] = np.sum(X_off,0)
  team_players['D_Poss'] = np.sum(np.abs(X_def),0)
  team_players['Points'] = np.round(team_players['ORtg']/100.0 * team_players['O_Poss'])
  team_players['Points_Opp'] = np.round(team_players['DRtg']/100.0 * team_players['D_Poss'])
  team_players['Net_Points'] = team_players['Points'] + team_players['Points_Opp']
  #team_players['Net_Points'] = team_players['ORPM']/100.0 * team_players['O_Poss'] + team_players['DRPM']/100.0 * team_players['D_Poss']
  
  #print np.sum(y_off), np.sum(y_def)
  #return team_players.sort(columns='RPM',ascending=False)[['PLAYER', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']]
  #return team_players.sort(columns='Points',ascending=False)[['PLAYER', 'ORtg', 'DRtg', 'NetRtg', 'O_Poss', 'D_Poss', 'Points', 'Points_Opp', 'Net_Points']]
  #return team_players.sort(columns='Points',ascending=False)[['PLAYER', 'ORtg', 'DRtg', 'NetRtg', 'O_Poss', 'Points']]
  return team_players.sort(columns='NetRtg',ascending=False)[['PLAYER', 'ORtg', 'DRtg', 'NetRtg', 'O_Poss', 'Points']]

#%% Print models

m = pd.DataFrame()
i=0
for team_id in teams['TEAM_ID'].values:
  print '\n'
  m1 = fit_team_rpm(team_id)
  print m1
  m = pd.concat((m,m1))
  i+=1

print m[m['O_Poss']>=2000].sort(columns='NetRtg',ascending=False)[0:60]
#print m[m['O_Poss']>=2000].sort(columns='Points',ascending=False)[0:60]
#print m[m['O_Poss']>=2000].sort(columns='ORPM',ascending=False)[0:60]
#print m[m['O_Poss']>=2000].sort(columns='Points',ascending=False)[0:60]

#team_id = teams['TEAM_ID'].values[1]
#m1 = fit_team_rpm(team_id)
#m1['Points'] = m1['ORPM']/100.0 * m1['O_Poss']
#print m1.sort(columns='Points', ascending=False)
