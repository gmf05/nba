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

#%% Fit league RPM model

#def fit_league_rpm():
Nplayers = len(all_players)
player_dict = bb.zip2(all_players['PERSON_ID'].values, range(Nplayers)) 

# Offense
possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'EVENTTYPE':{'$in':[1,2,3,5]}}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                    {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1, 'POSSTYPE':1}
                    )
N_poss = possessions.count()
X_off = np.zeros([N_poss, Nplayers])
X_def = np.zeros([N_poss, Nplayers])
y = np.zeros([N_poss])
z = np.zeros([N_poss])
  
i=0
for s in possessions:
  
  #if np.mod(i,1e3)==1: print i
    #t1 = time.time()
    #print i,t1-t0
    #t0 = t1
  
  try:
    o_idx = [player_dict[p] for p in s['OFFPLAYERS']]
  except:
    S = np.copy(s['OFFPLAYERS'])
    S = S[S>0]
    S = np.setdiff1d(S, S[np.where([p not in player_dict.keys() for p in S])[0]])
    o_idx = [player_dict[p] for p in S]

  try:
    d_idx = [player_dict[p] for p in s['DEFPLAYERS']]
  except:
    S = np.copy(s['DEFPLAYERS'])
    S = S[S>0]
    S = np.setdiff1d(S, S[np.where([p not in player_dict.keys() for p in S])[0]])
    d_idx = [player_dict[p] for p in S]

  X_off[i, o_idx] = 1      
  X_def[i, d_idx] = -1      
  y[i] = s['SCORECHANGE']
  z[i] = s['POSSTYPE']
  i+=1

#m = slm.LassoLarsCV() # L1 reg
m = slm.ElasticNet(l1_ratio = 0.8, alpha=4.5e-5) # L1-L2 combo reg
#m.fit_intercept = True
m.fit_intercept = False
#m = m.fit(X_off, y)
m = m.fit(np.hstack((X_off, X_def)), y)

rpm_o = m.coef_[0:Nplayers]
rpm_d = m.coef_[Nplayers:]
all_players['ORPM'] = np.round( rpm_o * 100, 1)
all_players['DRPM'] = np.round( rpm_d * 100, 1)
all_players['RPM'] = all_players['ORPM'] + all_players['DRPM']
#all_players['O_Poss'] = np.sum(X_off,0)
#all_players['D_Poss'] = np.sum(np.abs(X_def),0)
#all_players['Poss'] = 0.5*(all_players['O_Poss'] + all_players['D_Poss'])
#all_players['Points'] = all_players['ORPM']/100.0 * all_players['O_Poss']
# USE Z TO ESTIMATE  O/D Possession totals
#all_players['MinEst'] = np.round(all_players['Poss']/110.0 * 48.0)
#all_players['Net_Points'] = all_players['RPM']/100.0 * (all_players['O_Poss'] + all_players['D_Poss'])
#all_players['Net_Points'] = np.round(all_players['ORPM']/100.0 * all_players['O_Poss'] + all_players['DRPM']/100.0 * all_players['D_Poss'], 1)
#all_players['PPG'] = all_players['Poss'] / 82.0
#all_players['O_PPG'] = all_players['ORPM'] /100.0 * all_players['Poss']
#all_players['D_PPG'] = all_players['DRPM'] /100.0 * all_players['Poss']
#all_players['Net_PPG'] = all_players['O_PPG'] + all_players['D_PPG'] 
#all_players['Value'] = all_players['Net_Points'] / all_players['Salary']

#print all_players.sort(columns='Net_Points',ascending=False)[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'MinEst', 'Net_Points']][0:60]
#print all_players.sort(columns='Value',ascending=False)[['DISPLAY_FIRST_LAST', 'RPM','Net_Points', 'Salary', 'Value']][0:60]
#print all_players.sort(columns='Value',ascending=False)[['DISPLAY_FIRST_LAST', 'Poss', 'Net_PPG', 'Salary']][0:60]
#print all_players.sort(columns='RPM',ascending=False)[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'Poss', 'Points']][0:60]
#print all_players.sort(columns='Points',ascending=False)[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'MinEst', 'Points']][0:60]
print all_players[all_players['Poss']>=1000].sort(columns='RPM',ascending=False)[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'MinEst', 'Points']][0:60]

#%%