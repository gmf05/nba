# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 20:41:10 2015

@author: gmf
"""

import numpy as np
import pandas as pd
import json
import re

def get_boxscore(gameid):
  J = json.load( open( '%s/json/bs_%s.json' % (DATAPATH,gameid), 'r' ) )
  return [pd.DataFrame(data=j['rowSet'],columns=j['headers']) for j in J]

def get_pbp(gameid):
  J = json.load( open( '%s/json/pbp_%s.json' % (DATAPATH,gameid), 'r' ) )
  return pd.DataFrame(data=J['rowSet'],columns=J['headers'])

def get_shots(gameid):
  J = json.load( open( '%s/json/shots_%s.json' % (DATAPATH,gameid), 'r' ) )
  return pd.DataFrame(data=J['rowSet'],columns=J['headers'])

def get_reb_eventnum(gameid):
  pbp = get_pbp(gameid)
  homereb = []
  awayreb = []
  for i,p in pbp.iterrows():
    if p.HOMEDESCRIPTION and re.search('REBOUND', p.HOMEDESCRIPTION):
      homereb.append(p)
    if p.VISITORDESCRIPTION and re.search('REBOUND', p.VISITORDESCRIPTION):
      awayreb.append(p)
  i0 = [a.EVENTNUM for a in homereb]
  i1 = [a.EVENTNUM for a in awayreb]
  #i2 = np.union1d(i0,i1)
  return i0,i1

def compute_sec_elapsed(period, pctime_str):
  nmin,nsec = pctime_str.split(':')
  nmin = int(nmin)
  nsec = int(nsec)
  if period<5:
    pctime_sec = (11-nmin)*60 + 60 - nsec
    t = (period-1)*720 + pctime_sec
  else:
    pctime_sec = (4-nmin)*60 + 60 - nsec
    t = 2880 + (period-5)*300 + pctime_sec
  return t

def get_reb_pp(gameid):
  pbp = get_pbp(gameid)
  #
  # TO DO: DEAL WITH OT!!    
  dn1 = np.zeros(2880)
  dn2 = np.zeros(2880)
  #
  for i,p in pbp.iterrows():
    if p.VISITORDESCRIPTION and re.search('REBOUND', p.VISITORDESCRIPTION):
      t = compute_sec_elapsed(pbp.iloc[i]['PERIOD'], pbp.iloc[i]['PCTIMESTRING'])
      dn1[t] = 1
    if p.HOMEDESCRIPTION and re.search('REBOUND', p.HOMEDESCRIPTION):
      t = compute_sec_elapsed(pbp.iloc[i]['PERIOD'], pbp.iloc[i]['PCTIMESTRING'])
      dn2[t] = 1
  return dn1,dn2

DATAPATH = '/home/gmf/unsynced/nba/data'
gameid = '0021400001'
reb1,reb2 = get_reb_pp(gameid)
dn = np.vstack((reb1,reb2))
time = np.arange(0,2880)
d = pp.data(dn, time)


#
p = pp.params()
T_knots = np.arange(0, 1+ep, 1)
#T_knots = np.arange(0, 1+ep, 0.33333)
p.add_covar('Rate', -1, T_knots, 'indicator')
#p.add_covar('Rate', -1, T_knots, 'spline')

# Self history / Rhythms
Q_knots = np.array([1, 10, 20, 30, 50, 100])
Q_knots[0] = 1
p.add_covar('Self-History', response, Q_knots, 'spline')

m = pp.model()
m = m.fit(d, p)
