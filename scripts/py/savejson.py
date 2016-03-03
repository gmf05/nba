#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 23:28:55 2015

savejson.py
Get JSON from NBA.com -> raw text

@author: gmf
"""

import requests # query web
import json # parse json
import sys # take input arguments from command line

# Where is the data to be read/saved?
DATAPATH = '/media/gmf/GMF/unsynced/nba/data'
#DATAPATH = '/home/gmf/Code/git/nba'

# URLs & parameter sets for requests
user_agent = {'User-agent': 'Mozilla/5.0'}
# Play by Play. Works for 1996-97 onward    
pbp_url = 'http://stats.nba.com/stats/playbyplay'
pbp_params = {'GameID':0, 'RangeType':0, 'StartPeriod':0, 'EndPeriod':0, 'StartRange':0, 'EndRange':0}
# Shot Chart. Works for 1996-97 onward
sc_url = 'http://stats.nba.com/stats/shotchartdetail'
sc_params = {'Season':'', 'SeasonType':'Regular Season', 'LeagueID':'00', 'TeamID':0, 'PlayerID':0, 'GameID':0, 'Outcome':'', 'Location':'', 'Month':0, 'SeasonSegment':'', 'DateFrom':'', 'DateTo':'', 'OpponentTeamID':0, 'VsConference':'', 'VsDivision':'', 'Position':'', 'RookieYear':'', 'GameSegment':'', 'Period':0, 'LastNGames':0, 'ContextFilter':'', 'ContextMeasure':'FG_PCT', 'zone-mode':'basic', 'viewShots':'true'}
# Box Score. Works for historic games back to 1949+
bs_url = 'http://stats.nba.com/stats/boxscore'
bs_params = {'GameID':'0', 'RangeType':'0', 'StartPeriod':'0', 'EndPeriod':'0', 'StartRange':'0', 'EndRange':'0'}
# SportVu Data. WARNING: Time consuming & large. May want to comment out.
#do_sportvu = True
do_sportvu = False
sv_url = 'http://stats.nba.com/stats/locations_getmoments/'
sv_params = {'eventid':0, 'gameid':0}

def write_game_json(gameid):
  #  
  # Box score
  #
  print 'Game %s, box score' % gameid
  f = open('%s/json/bs_%s.json' % (DATAPATH, gameid), 'w')
  bs_params['GameID'] = gameid
  bs = requests.get(bs_url, params=bs_params, headers=user_agent).json()['resultSets']
  json.dump(bs, f)
  f.close()
  #  
  # Play by play
  #
  print 'Game %s, play by play' % gameid
  f = open('%s/json/pbp_%s.json' % (DATAPATH, gameid), 'w')
  pbp_params['GameID'] = gameid    
  pbp = requests.get(pbp_url, params=pbp_params, headers=user_agent).json()['resultSets'][0]
  json.dump(pbp, f)    
  f.close()
  # 
  # Shot chart
  #
  print 'Game %s, shot chart' % gameid
  f = open('%s/json/shots_%s.json' % (DATAPATH, gameid), 'w')
  sc_params['GameID'] = gameid
  sc_params['SeasonType'] = 'Playoffs'
  sc = requests.get(sc_url, params=sc_params, headers=user_agent).json()['resultSets'][0]
  json.dump(sc, f)
  f.close()
  #  
  # SportVu
  #
  if not do_sportvu:
    return
    
  print 'Game %s, SportVu' % gameid
  sv_params['gameid'] = gameid
  #
  eventids = []
  for p in pbp['rowSet'][1:]:
    eventids.append(p[1])
  print "Number of events: " + str(eventids[-1])
  #
  # loop over events, get sport vu data for each one, keep track of errors
  errlist = []
  for eventid in eventids:
    print str(eventid)
    try:
      sv_params['eventid'] = eventid
      sv = requests.get(sv_url, params=sv_params, headers=user_agent).json()
      f = open('%s/json/sv_%s_%s.json' % (DATAPATH, gameid, str(eventid).zfill(4), 'w'))
      json.dump(sv, f)
      f.close()
    #except IOError:
    except:
      errlist.append(str(eventid))
      print "Error on " + str(eventid)

def write_gamelist_json(gamelist):
  f = open(gamelist, 'r')
  f.readline() # drop headers    
  for r in f.readlines():
    gameid = r.split(',')[0]
    write_game_json(gameid)

def main():
  write_game_json(sys.argv[1]) 
  #write_gamelist_json(sys.argv[1])

if __name__ == '__main__': 
  main()
