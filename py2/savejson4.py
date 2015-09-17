#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 17:09:57 2015

Simple Python script to pull JSON data from NBA.com

@author: Grant Fiddyment  <neurocoding05@gmail.com>
"""
import requests # query web
import json # parse json
import datetime # useful for making lists of days between dates

# Where should the output files be saved?
NBAPATH = '/home/gfiddy/' # <<<< CHANGE THIS FOR YOUR SYSTEM!!

# Base URLs
# Play by Play. Works for 1996-97 onward    
pbp_url = 'http://stats.nba.com/stats/playbyplay'
pbp_params = {'GameID':0, 'RangeType':0, 'StartPeriod':0, 'EndPeriod':0, 'StartRange':0, 'EndRange':0, 'playbyplay':'undefined'}
# Shot Chart. Works for 1996-97 onward
sc_url = 'http://stats.nba.com/stats/shotchartdetail'
sc_params = {'Season':'', 'SeasonType':'Regular Season', 'LeagueID':'00', 'TeamID':0, 'PlayerID':0, 'GameID':0, 'Outcome':'', 'Location':'', 'Month':0, 'SeasonSegment':'', 'DateFrom':'', 'DateTo':'', 'OpponentTeamID':0, 'VsConference':'', 'VsDivision':'', 'Position':'', 'RookieYear':'', 'GameSegment':'', 'Period':0, 'LastNGames':0, 'ContextFilter':'', 'ContextMeasure':'FG_PCT', 'zone-mode':'basic', 'viewShots':'true'}
# Box Score. Works for historic games back to 1949+    
bs_url = 'http://stats.nba.com/stats/boxscore'
bs_params = {'GameID':0, 'RangeType':0, 'StartPeriod':0, 'EndPeriod':0, 'StartRange':0, 'EndRange':0, 'playbyplay':'undefined'}
# SportVu Data. Works for most games in 2014-15, not sure about 2013-14
#sv_url = 'http://stats.nba.com/stats/locations_getmoments/?eventid=1&gameid=*GAMEID*'

#season_code = '00299' # 1999 regular season
season_code = '00214' # 2014 regular season
#season_code = '00414' # 2014 playoffs

# 1. Find list of all games within given season
delim = ','
fw = open(NBAPATH + 'games_' + season_code + '.csv', 'w')
fw.write(delim.join(['gameid_num','gameid','away','home']) + '\n') # write headers

# 1a. Find start & stop dates for given season
fr = open(NBAPATH + 'nbaseasons.csv','r')
fr.readline() # drop headers
for r in fr.readlines():
  curr_season,start_date,stop_date = r.strip().split(delim)  
  if curr_season == season_code[-2:]: break

# 1b. Get list of all days between start date & stop date
start_date_int = [int(i) for i in start_date.split('/')]
stop_date_int = [int(i) for i in stop_date.split('/')]
sd1 = datetime.date(start_date_int[0], start_date_int[1], start_date_int[2])
sd2 = datetime.date(stop_date_int[0], stop_date_int[1], stop_date_int[2])
numdays = (sd2-sd1).days
datelist = [sd1 + datetime.timedelta(days=x) for x in range(0, numdays+1)]

# 1c. Loop over dates, find games for each date, save to game list
for d in datelist:
  diso = str(d.year) + str(d.month).zfill(2) + str(d.day).zfill(2)
  #print diso # debug
  try:
    games_url = 'http://data.nba.com/5s/json/cms/noseason/scoreboard/%s/games.json' % diso
    gamelist = requests.get(games_url).json()['sports_content']['games']['game']
    for g in gamelist:
      gamecode = diso + g['visitor']['abbreviation'] + g['home']['abbreviation']
      print gamecode # debug
      l = [g['id'], gamecode, g['visitor']['abbreviation'], g['home']['abbreviation']]
      fw.write(delim.join(l) + '\n')
  except:
    print 'Encountered error on %s' % diso

# 2. Get data for each game
# 2a. Open game list
fr = open(NBAPATH + 'games_' + season_code + '.csv','r')
fr.readline() # drop headers

# 2b. Pull JSON data [play by play, shot chart, box score] for each game!
for r in fr.readlines():
  gameid = r.split(',')[0]
  print gameid # debug
  try:
    # Get play by play (pbp)
    fw = open(NBAPATH + '/pbp_' + gameid + '.json', 'w')
    pbp_params['GameID'] = gameid    
    j = requests.get(pbp_url, params=pbp_params).json()['resultSets']
    json.dump(j, fw)    
    fw.close()
    # Get shot chart (sc)
    fw = open(NBAPATH + '/shots_' + gameid + '.json', 'w')
    sc_params['GameID'] = gameid
    sc_params['SeasonType'] = 'Playoffs'
    j = requests.get(sc_url, params=sc_params).json()['resultSets']
    json.dump(j, fw)
    fw.close()
    # Get box score (bs)
    fw = open(NBAPATH + '/bs_' + gameid + '.json', 'w')    
    bs_params['GameID'] = gameid
    j = requests.get(bs_url, params=bs_params).json()['resultSets']
    json.dump(j, fw)
    fw.close()
  except:
    print 'Encountered error on %s' % gameid