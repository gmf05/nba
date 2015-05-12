#!/usr/bin/python
# get JSON from NBA.com -> raw text
import requests # query web
import json # parse json
import sys # take input arguments from command line

if __name__ == '__main__':

  JSONPATH = '/home/gmf/Code/repos/nba/json'
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

  #season_code = sys.argv[1]
  #season_code = '00214'
  for y in range(2007, 2008):
    season_code = '004' + str(y)[2:]
    # get number of games in given season
    fr = open("/home/gmf/Code/repos/nba/csv/playoffs_" + season_code + ".csv","r")
    fr.readline() # drop headers
    for r in fr.readlines():
      #
      gameid = r.split(',')[0]
      #gameid = season_code + str(gamenum).zfill(5)
      print gameid # debug
      try:
        #
        fw = open(JSONPATH + "/pbp_" + gameid + ".json", "w")
        pbp_params['GameID'] = gameid    
        j = requests.get(pbp_url, params=pbp_params).json()['resultSets'][0]
        json.dump(j, fw)    
        fw.close()
        #
        fw = open(JSONPATH + "/shots_" + gameid + ".json", "w")    
        sc_params['GameID'] = gameid
        sc_params['SeasonType'] = 'Playoffs'
        j = requests.get(sc_url, params=sc_params).json()['resultSets'][0]
        json.dump(j, fw)
        fw.close()
        #
        fw = open(JSONPATH + "/bs_" + gameid + ".json", "w")    
        bs_params['GameID'] = gameid
        j = requests.get(bs_url, params=bs_params).json()['resultSets']
        json.dump(j, fw)
        fw.close()    
      except:
        0
      
