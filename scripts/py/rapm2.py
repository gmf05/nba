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
events_db = db['scoring_plays']

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
                      {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1}
                      )
  N_off = off_possessions.count()
  X_off = np.zeros([N_off, Nteam_players])
  y_off = np.zeros([N_off])
    
  i=0
  for s in off_possessions:
    
    #if np.mod(i,1e3)==1: print i
      #t1 = time.time()
      #print i,t1-t0
      #t0 = t1
    
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
    
  m_off = slm.LassoCV() # L1 reg
  m_off.fit_intercept = True
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
    
    #if np.mod(i,1e3)==1: print i
      #t1 = time.time()
      #print i,t1-t0
      #t0 = t1
    
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
  
  m_def = slm.LassoCV() # L1 reg
  m_def.fit_intercept = True
  m_def = m_def.fit(X_def, y_def)

  team_players['ORPM'] = np.round( m_off.coef_ * 100, 2)
  team_players['DRPM'] = np.round( m_def.coef_ * 100, 2)
  team_players['RPM'] = team_players['ORPM'] + team_players['DRPM']
  team_players['O_Poss'] = np.sum(X_off,0)
  team_players['D_Poss'] = np.sum(np.abs(X_def),0)
  
  return team_players.sort(columns='RPM',ascending=False)[['PLAYER', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']]

##%% Print models
#
#m = pd.DataFrame()
#i=0
#for team_id in teams['TEAM_ID'].values:
#  print '\n'
#  m1 = fit_team_rpm(team_id)
#  print m1
#  m = pd.concat((m,m1))
#  i+=1

#%% Fit league RPM model

#def fit_league_rpm():
Nplayers = len(all_players)
player_dict = bb.zip2(all_players['PERSON_ID'].values, range(Nplayers)) 

# Offense
possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'EVENTTYPE':{'$in':[1,2,3,5]}}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                    {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1}
                    )
N_poss = possessions.count()
X_off = np.zeros([N_poss, Nplayers])
X_def = np.zeros([N_poss, Nplayers])
y = np.zeros([N_poss])
  
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
all_players['O_Poss'] = np.sum(X_off,0)
all_players['D_Poss'] = np.sum(np.abs(X_def),0)
all_players['Poss'] = 0.5*(all_players['O_Poss'] + all_players['D_Poss'])
all_players['MinEst'] = np.round(all_players['Poss']/125.0 * 48.0)
#all_players['Net_Points'] = all_players['RPM']/100.0 * (all_players['O_Poss'] + all_players['D_Poss'])
#all_players['Net_Points'] = np.round(all_players['ORPM']/100.0 * all_players['O_Poss'] + all_players['DRPM']/100.0 * all_players['D_Poss'], 1)
all_players['PPG'] = all_players['Poss'] / 82.0
all_players['O_PPG'] = all_players['ORPM'] /100.0 * all_players['Poss']
all_players['D_PPG'] = all_players['DRPM'] /100.0 * all_players['Poss']
all_players['Net_PPG'] = all_players['O_PPG'] + all_players['D_PPG'] 
all_players['Value'] = all_players['Net_Points'] / all_players['Salary']

#print all_players.sort(columns='Net_Points',ascending=False)[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'MinEst', 'Net_Points']][0:60]
#print all_players.sort(columns='Value',ascending=False)[['DISPLAY_FIRST_LAST', 'RPM','Net_Points', 'Salary', 'Value']][0:60]
print all_players.sort(columns='Value',ascending=False)[['DISPLAY_FIRST_LAST', 'Poss', 'Net_PPG', 'Salary']][0:60]


#print all_players.sort(columns='ORPM',ascending=False)[['DISPLAY_FIRST_LAST', 'DRPM', 'D_Poss']][0:60]

#print all_players.sort(columns='RPM',ascending=False)[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']][0:60]
#print all_players.sort(columns='RPM',ascending=False)[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']][60:120]
#print all_players.sort(columns='RPM',ascending=False)[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']][120:180]

#P = all_players.sort(columns='ORPM',ascending=False)[['DISPLAY_FIRST_LAST', 'TEAM_ID','ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']]
#for team_id in teams['TEAM_ID'].values:
#  print P[P['TEAM_ID']==team_id]

#return all_players.sort(columns='RPM',ascending=False)[['PLAYER', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']]

#%%

salary_array = np.zeros(len(all_players))
for i,p in salaries.iterrows():
  name = p['Name,Position'].split(',')[0]
  if name=='Nene Hilario': name = 'Nene'
  try:
    idx = np.where(all_players['DISPLAY_FIRST_LAST'].values==name)[0][0]    
    salary_array[idx] = int(p['Salary'].replace(',','').replace('$','')) / 1000.0
  except:
    0
salary_array[salary_array==0] = np.nan

all_players['Salary'] = salary_array


#%% 
# Lineup:
# Joe Johnson  31 mpg $261  + 5.5 [sf/sg]
# Kyle Korver 28 mpg $5746 + 10.94 [sg/sf]
# Rodney Hood 28 mpg $1348 +2.6 [sg]
# Gorgui Dieng 26 mpg $1474 + 4.96 [c]
# Rudy Gobert 22 mpg $1175 + 3.65 [c]

# Jerami Grant 25 mpg $845 + 2 [sf]
# Langston Galloway 24 mpg $845  + 1.87 [sg]
# Dellavedova  22 mpg $1147 + 4.27 [pg/sg]
# Tony Snell 16 mpg $1535 + 4.32 [sf]
# Lance Thomas 15 mpg $1636 + 3.3 [sf]

# s
# Bench
# Kentavious Caldwell Pope 33 mpg +4.4 $3891 [sg]
# Kelly Olynyk 17 mpg +3.74 $2165 [c]
# Garrett Temple 24 mpg $1100 + 2.09 [sg]
#
# ^^ ~ 16 million payroll   + 43 margin

roster = ['Joe Johnson', 'Kyle Korver', 'Rodney Hood', 'Gorgui Dieng', 'Rudy Gobert']
for r in roster:
  idx = np.where(p['Name']==r)[0][0]
  print p.iloc[idx]['DRPM']/100.0 * 30/48 * 125.0

roster = ['Jerami Grant', 'Langston Galloway', 'Matthew Dellavedova', 'Tony Snell', 'Lance Thomas']
for r in roster:
  idx = np.where(p['Name']==r)[0][0]
  print p.iloc[idx]['DRPM']/100.0 * 18/48 * 125.0

#%% Debugging total points / points against by team

import bb_tools as bb

season_year = '2015-16'

seasonid = '002' + season_year.split('-')[0][2:]
all_players = bb.get_players_season(season=season_year)
teams = bb.get_teams_current()
Nplayers = len(all_players)
Nteams = len(teams)

team_id = teams['TEAM_ID'].values[0]
team_players = bb.get_team_roster(team_id, season=season_year)
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
  
  #if np.mod(i,1e3)==1: print i
    #t1 = time.time()
    #print i,t1-t0
    #t0 = t1
  
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
  
# Defense
def_possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'DEFTEAM':team_id}, {'EVENTTYPE':{'$in':[1,2,3,5]}}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                    {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1}
                    )
N_def = def_possessions.count()
X_def = np.zeros([N_def, Nteam_players])
y_def = np.zeros([N_def])
  
i=0
for s in def_possessions:
  
  #if np.mod(i,1e3)==1: print i
    #t1 = time.time()
    #print i,t1-t0
    #t0 = t1
  
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
  
  
# NOW break up by game and see which games have wrong point totals
#
#
