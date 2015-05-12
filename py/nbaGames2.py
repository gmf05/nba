#!/usr/bin/python
import requests
import json
import urllib2
import re
import datetime

# newer method using json
for season_year in range(2012,2013):
  #fr = open('csv/nbaseasons.csv','r')
  fr = open('csv/nbaplayoffs.csv','r')
  fr.readline()
  for r in fr.readlines():
    curr_year = int(r.split(',')[1][0:4])
    str_year = str(curr_year)[2:4]
    if season_year==curr_year:
      start_day = r.split(',')[1].replace('/','')
      stop_day = r.split(',')[2].strip().replace('/','')
      break
  start_date = datetime.date(int(start_day[0:4]),int(start_day[4:6]),int(start_day[6:]))
  stop_date = datetime.date(int(stop_day[0:4]),int(stop_day[4:6]),int(stop_day[6:]))
  numdays = (stop_date-start_date).days
  datelist = [start_date + datetime.timedelta(days=x) for x in range(0, numdays+1)]
  fw = open("csv/playoffs_004" + str(int(str_year)-1) + ".csv", "w")
  fw.write(','.join(['gameid_num','gameid','away','home']) + '\n')
  for d in datelist:
    diso = str(d.year) + str(d.month).zfill(2) + str(d.day).zfill(2)
    print diso
    try:
      games_url = 'http://data.nba.com/5s/json/cms/noseason/scoreboard/' + diso + '/games.json'  
      html = urllib2.urlopen(games_url).read()
      gamelist = json.loads(html)['sports_content']['games']['game']
      for g in gamelist:    
        gamecode = diso + g['visitor']['abbreviation'] + g['home']['abbreviation']
        print gamecode
        l = [g['id'], gamecode, g['visitor']['abbreviation'], g['home']['abbreviation']]
        fw.write(','.join(l) + '\n')
    except:
      0      
  fw.close()

# old but good method
delim = ","
#fw = file("games_" + season_code + ".csv", "w")
fw = open("test.csv", "w")
# add line of field names
keys = ['gameid_num', 'gameid', 'away', 'home']
fw.write(delim.join(keys) + '\n')
# get list of days and search for games
numdays = (stopday-startday).days
datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]
#count=101
season_year = str(startday.year - (startday.month<8))
for d in datelist:
  diso = str.replace(d.isoformat(),'-','')
  pingflag = True 
  url = 'http://www.nba.com/gameline/' + diso + '/'
  html = urllib2.urlopen(url).read()
  # div id="nbaGL' + season_code
  str_search = 'div id="nbaGL' + season_code
  gameids = re.findall('div id="nbaGL(0\d+)',html)
  teamcodes = list(set(re.findall('href="/games/' + diso + '/(.*?)/gameinfo.html',html)))
  count=0
  for t in teamcodes:
    gameid_num = gameids[count]
    count+=1
    away = t[0:3]
    home = t[3:6]
    gameid = diso + away + home
    dout = [gameid_num, gameid, away,home]
    print delim.join(dout)
    fw.write(delim.join(dout) + "\n")
fw.close()