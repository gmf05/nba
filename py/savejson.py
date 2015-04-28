# get JSON from NBA.com -> raw text
import urllib2 # query web
import json # parse json
import sys # take input arguments from command line

if __name__ == '__main__':

    # Base URLs
    # Play by Play. Works for 1996-97 onward    
    pbp_url = 'http://stats.nba.com/stats/playbyplay?GameID=*GAMEID*&RangeType=0&StartPeriod=0&EndPeriod=0&StartRange=0&EndRange=0&playbyplay=undefined'
    # Shot Chart. Works for 1996-97 onward
    sc_url = 'http://stats.nba.com/stats/shotchartdetail?Season=&SeasonType=Regular+Season&LeagueID=00&TeamID=0&PlayerID=0&GameID=*GAMEID*&Outcome=&Location=&Month=0&SeasonSegment=&DateFrom=&DateTo=&OpponentTeamID=0&VsConference=&VsDivision=&Position=&RookieYear=&GameSegment=&Period=0&LastNGames=0&ContextFilter=&ContextMeasure=FG_PCT&zone-mode=basic&viewShots=true'
    # Box Score. Works for historic games back to 1949+    
    bs_url = 'http://stats.nba.com/stats/boxscore?GameID=*GAMEID*&RangeType=0&StartPeriod=0&EndPeriod=0&StartRange=0&EndRange=0&playbyplay=undefined'

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
    for gamenum in range(1,endid+1):
      gameid = season_code + str(gamenum).zfill(5)
      print gameid # debug
      #
      fw = open("json/bs_" + gameid + ".json", "w")
      j = urllib2.urlopen(bs_url.replace('*GAMEID*', gameid)).read()['resultSets']
      fw.write(j)
      fw.close()
      #
      fw = open("json/shots_" + gameid + ".json", "w")
      j = json.loads(urllib2.urlopen(sc_url.replace('*GAMEID*', gameid)).read())['resultSets'][0]
      fw.write(j)
      fw.close()
      #
      fw = open("json/pbp_" + gameid + ".json", "w")
      j = json.loads(urllib2.urlopen(pbp_url.replace('*GAMEID*', gameid)).read())['resultSets'][0]
      fw.write(j)
      fw.close()