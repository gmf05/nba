#!/usr/bin/python#!/usr/bin/python
# get JSON from NBA.com -> raw text
import requests # query web
import json # parse json
import sys # take input arguments from command line

if __name__ == '__main__':

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
  sv_url = 'http://stats.nba.com/stats/locations_getmoments/'
  sv_params = {'eventid':1, 'gameid': 0}

  season_code = sys.argv[1]
  #season_code = '00214'
  
  # get number of games in given season
  fr = open("ngames_season.csv","r")
  fr.readline() # drop headers    
  endid = None
  for r in fr.readlines():
    season,ngames = r.strip().split(',')
    if season[-2:]==season_code[-2:]:
        endid = int(ngames)
        break
  
  # loop over games, collect data
  #for gamenum in range(1,endid+1):
  for gamenum in range(101,105):
    #
    gameid = season_code + str(gamenum).zfill(5)
    print gameid # debug
    #
    fw = open("json/pbp_" + gameid + ".json", "w")
    pbp_params['GameID'] = gameid    
    j = requests.get(pbp_url, params=pbp_params).json()['resultSets'][0]
    json.dump(j, fw)    
    fw.close()
    #
    fw = open("json/shots_" + gameid + ".json", "w")    
    sc_params['GameID'] = gameid
    #sc_params['SeasonType'] = 'Playoffs'
    j = requests.get(sc_url, params=sc_params).json()['resultSets'][0]
    json.dump(j, fw)
    fw.close()
    #
    fw = open("json/bs_" + gameid + ".json", "w")    
    bs_params['GameID'] = gameid
    j = requests.get(bs_url, params=bs_params).json()['resultSets']
    json.dump(j, fw)
    fw.close()    
    #
    sv_params['GameID'] = gameid
    # get eventidlist from pbp    
    # loop over eventid    
    #fw = open("json/sv_" + gameid + ".json", "w")    
    #j = requests.get(sv_url, params=sv_params).json()
    #json.dump(j, fw)
    #fw.close()