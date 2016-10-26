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
#events_db.create_index([('SEASONID', pymongo.ASCENDING), ('GAMEID', pymongo.ASCENDING)])

#%% Building design matrix

#season_year = '1996-97'
# m.intercept_ = 0.805 # same whether l1 or l2

#season_year = '2014-15'
# m.intercept_ = 0.8209 [[95% ci?]]

season_year = '2015-16'
# m.intercept_ = 0.828 [[95% ci?]]

seasonid = '002' + season_year.split('-')[0][2:]

all_players = bb.get_players_season(season=season_year)
Nplayers = len(all_players)
teams = bb.get_teams_current()
Nteams = len(teams)

#team_id = teams['TEAM_ID'].values[0]

def fit_team_model(team_id):
  team_players = all_players[all_players['TEAM_ID']==team_id]
  Nteam_players = len(team_players)
  team_dict = bb.zip2(team_players['PERSON_ID'].values, range(Nteam_players))
  
  # re-grab just scoring events
  # 1 made shot
  # 2 missed shot
  # 3 free throw
  # 4 rebound
  # 5 turnover
  # 6 foul
  # 7 violation -- seems to never have scorechange > 0, so ignore
  # 8 sub
  # 9 timeout
  # 10 jump ball
  # 11 ejection
  # 12-13 unknown
  off_possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'OFFTEAM':team_id}, {'EVENTTYPE':{'$in':[1,2,3,5]}}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                      {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1}
                      )
  def_possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'DEFTEAM':team_id}, {'EVENTTYPE':{'$in':[1,2,3,5]}}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                      {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1}
                      )
  #for p in possession_events:
  #  if p['SCORECHANGE']<0:
  #    print p['DESCRIPTION']
  N_off = off_possessions.count()
  N_def = def_possessions.count()
  
  # Design matrix
  X_off = np.zeros([N_off, Nteam_players])
  X_def = np.zeros([N_def, Nteam_players])
  y_off = np.zeros([N_off])
  y_def = np.zeros([N_def])
  
  #import time
  #t0 = time.time()
  
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
  
  #t1 = time.time()
  #print t1-t0
  
  i=0
  for s in def_possessions:
    
    #if np.mod(i,1e3)==1: print i
    #try:
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
  
  #t2 = time.time()
  #print t2-t1
  
  ## Drop any extra columns from X, all_players
  #good_idx = np.where(np.sum(np.abs(X_off)+np.abs(X_def),0)>0)[0]
  #X = X[:, good_idx]
  #all_players = all_players[good_idx]
  #print len(all_players)
  #print X.shape
  
  # Regularization?
  #m = sm.OLS(y, X) # no reg
  #m = slm.LassoCV() # L1 reg
  #m = slm.RidgeCV() # L2 reg
  #m = slm.RidgeCV(alphas=[1e-3,1e-2,1e-1,1,2,10,20])
  
  m_off = slm.LassoCV() # L1 reg
  m_def = slm.LassoCV() # L1 reg
  #m_off = slm.LassoLarsCV() # L1 reg
  #m_def = slm.LassoLarsCV() # L1 reg

  #m_off = slm.RidgeCV() # L2 reg
  #m_def = slm.RidgeCV() # L2 reg
  
  # Intercept?
  #m_off.fit_intercept = False
  #m_def.fit_intercept = False 
  m_off.fit_intercept = True
  m_def.fit_intercept = True
  
  # Fit
  m_off = m_off.fit(X_off, y_off)  
  m_def = m_def.fit(X_def, y_def)
  
  # Count possessions per player
  team_players['O_Poss'] = np.sum(X_off,0)
  team_players['D_Poss'] = -np.sum(X_def,0)
  
  # Estimate standard errors
  # Offense
#  weights = np.ones(y_off.shape[0])
#  ssr_off = np.sum(np.multiply(weights, (y_off - np.dot(X_off, m_off.coef_))**2))
#  dfe_off = np.max(X_off.shape[0] - Nteam_players, 0)
#  s_off = np.sqrt(ssr_off / dfe_off)
#  cov_off = s_off**2 * np.linalg.inv(np.dot(X_off.T , X_off))
#  se_off = np.sqrt(np.diag(cov_off))
#  rpm_o_lower = np.round((m_off.coef_ - 1.96*se_off)*100, 2)
#  #rpm_o_mid = m_off.coef_ * 100
#  rpm_o_upper = np.round((m_off.coef_ + 1.96*se_off)*100, 2)
#  
#  # Defense
#  weights = np.ones(y_def.shape[0])
#  ssr_def = np.sum(np.multiply(weights, (y_def - np.dot(X_def, m_def.coef_))**2))
#  dfe_def = np.max(X_def.shape[0] - Nteam_players, 0)
#  s_def = np.sqrt(ssr_def / dfe_def)
#  cov_def = s_def**2 * np.linalg.inv(np.dot(X_def.T , X_def))
#  se_def = np.sqrt(np.diag(cov_def))
#  rpm_d_lower = np.round((m_def.coef_ - 1.96*se_def)*100, 2)
#  #rpm_d_mid =  m_def.coef_ * 100
#  rpm_d_upper = np.round((m_def.coef_ + 1.96*se_def)*100, 2)

  #% Make a table of m.coef_ + player names
  
  #m = m_def
  #rpm = m.coef_
  rpm = m_off.coef_ + m_def.coef_
  idx = np.argsort(rpm)[-1:0:-1]
  rpm_o = np.round(m_off.coef_[idx]*100, 2)
  rpm_d = np.round(m_def.coef_[idx]*100, 2)
  rpm_sort = np.round(rpm[idx]*100, 2)
  players_sort = team_players.iloc[idx]
  players_sort['ORPM'] = rpm_o
  players_sort['DRPM'] = rpm_d
  players_sort['RPM'] = rpm_sort
  
  # How to avoid all this renaming??
  #players_sort['ORPM'] = rpm_o
  #players_sort['ORPM_low'] = rpm_o_lower[idx]
  #players_sort['ORPM_high'] = rpm_o_upper[idx]
  #players_sort['DRPM'] = rpm_d
  #players_sort['DRPM_low'] = rpm_d_lower[idx]
  #players_sort['DRPM_high'] = rpm_d_upper[idx]
  #players_sort['RPM'] = rpm_sort

  # VV use to test coeff. VV
  #P = players_sort[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']]
  #margin = 1.96 * np.sqrt(np.diag(np.linalg.inv(np.dot(X_off.T, X_off))))
  return players_sort[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']]
  #return players_sort[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss', 'ORPM_low', 'ORPM_high', 'DRPM_low', 'DRPM_high']]


#%

#team_id = teams['TEAM_ID'].values[0] # ATL
#team_id = teams['TEAM_ID'].values[1] # BOS
#team_id = teams['TEAM_ID'].values[2] # CLE
#team_id = teams['TEAM_ID'].values[4] # CHI
#team_id = teams['TEAM_ID'].values[7] # GSW
#team_id = teams['TEAM_ID'].values[12] # MIL
#team_id = teams['TEAM_ID'].values[13] # MIN
#team_id = teams['TEAM_ID'].values[22] # SAS
#team_id = teams['TEAM_ID'].values[23] # OKC

#m = fit_team_model(team_id)
#print '\n\n', m

#%%
m = pd.DataFrame()
i=0
for team_id in teams['TEAM_ID'].values:
  print '\n'
  m1 = fit_team_model(team_id)
  print m1
  m = pd.concat((m,m1))
  i+=1
#  print fit_team_model(team_id)

#%%

#print m[(m['O_Poss']>=1000) & (m['D_Poss']>=1000)].sort(columns='ORPM', ascending=False)[-1:-50:-1]
#print m[(m['O_Poss']>=1000) & (m['D_Poss']>=1000)].sort(columns='ORPM', ascending=False)[0:50]
#print m[(m['O_Poss']>=1000) & (m['D_Poss']>=1000)].sort(columns='DRPM', ascending=False)[0:50]
print m[(m['O_Poss']>=1000) & (m['D_Poss']>=1000)].sort(columns='RPM', ascending=False)[0:50]
#print m[(m['O_Poss']>=1000) & (m['D_Poss']>=1000)].sort(columns='RPM', ascending=False)[-1:-50:-1]




#%%


#season_year = '1996-97'
#season_year = '1997-98'
# m.intercept_ = 0.805 # same whether l1 or l2

#season_year = '2014-15'
# m.intercept_ = 0.8209 [[95% ci?]]

season_year = '2014-15'
#season_year = '2015-16'
# m.intercept_ = 0.828 [[95% ci?]]

seasonid = '002' + season_year.split('-')[0][2:]

all_players = bb.get_players_season(season=season_year)
Nplayers = len(all_players)
player_dict = bb.zip2(all_players['PERSON_ID'].values, range(Nplayers))
  
# re-grab just scoring events
# 1 made shot
# 2 missed shot
# 3 free throw
# 4 rebound
# 5 turnover
# 6 foul
# 7 violation -- seems to never have scorechange > 0, so ignore
# 8 sub
# 9 timeout
# 10 jump ball
# 11 ejection
# 12-13 unknown
possessions = events_db.find({'$and': [{'SEASONID': seasonid}, {'SCORECHANGE': {'$gte': 0}}, {'SCORECHANGE': {'$lte': 3}}]},
                    {'OFFPLAYERS':1, 'DEFPLAYERS':1, 'SCORECHANGE':1}
                    )

N_poss = possessions.count()

# Design matrix
X_off = np.zeros([N_poss, Nplayers])
X_def = np.zeros([N_poss, Nplayers])
y = np.zeros([N_poss])
  
i=0
for s in possessions:

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

#m = slm.LassoCV() # L1 reg 
#m = slm.RidgeCV() # L2 reg 

#m.fit_intercept = False
#m = m.fit(X, y)

m_off = slm.LassoLarsCV() # L1 reg 
m_def= slm.LassoLarsCV() # L1 reg 
m_off.fit_intercept = False
m_def.fit_intercept = False
m_off = m_off.fit(X_off, y)
#m_def = m_def.fit(X_def, y)
np.dot(X_off, m_off.coef_)
#epv = np.dot(X_off, m_off.coef_)

plt.plot(np.dott(X_off, m_off.oecf_), 'b')
plt.plot(y, 'r')
plt.xlim([0,200])

m_def = m_def.fit(np.dott(X_off, m_off.oecf_))

# Count possessions per player
all_players['O_Poss'] = np.sum(X_off,0)
all_players['D_Poss'] = np.sum(np.abs(X_def),0)
#all_players['Poss'] = np.sum(np.abs(X_off+X_def),0)

#rpm = m.coef_
#idx = np.argsort(rpm)[-1:0:-1]
rpm = m_off.coef_ + m_def.coef_
idx = np.argsort(rpm)[-1:0:-1]
idx = np.argsort(m_off.coef_)[-1:0:-1]
rpm_o = np.round(m_off.coef_[idx]*100, 2)
rpm_d = np.round(m_def.coef_[idx]*100, 2)
rpm_sort = np.round(rpm[idx]*100, 2)
players_sort = all_players.iloc[idx]
players_sort['ORPM'] = rpm_o
players_sort['DRPM'] = rpm_d
players_sort['RPM'] = rpm_sort

#print players_sort[['DISPLAY_FIRST_LAST', 'RPM', 'Poss']][0:50]
#print players_sort[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'Poss']][0:50]
#print players_sort[['DISPLAY_FIRST_LAST', 'RPM', 'Poss']][-1:-50:-1]
#return players_sort[['DISPLAY_FIRST_LAST', 'ORPM', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']]
players_sort['Pts'] = players_sort['ORPM']/100.0 * players_sort['O_Poss']

print players_sort[players_sort['Poss']>=2000][['DISPLAY_FIRST_LAST', 'ORPM', 'Pts', 'DRPM', 'RPM', 'O_Poss', 'D_Poss']][0:50]

#%% How well does 2014-15  season model [or even 2015-16 model...]
# predict 2015-16 results??

# Which player(s) ORPM differs most from ORTG??

