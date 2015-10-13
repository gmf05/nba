# -*- coding: utf-8 -*-
"""
Created on Tue Oct 13 00:23:47 2015

@author: gmf
"""
import requests
import datetime

games_url_base = 'http://data.nba.com/5s/json/cms/noseason/scoreboard/%s/games.json'

def get_gamelist(date_iso):
  games_url = games_url_base % date_iso
  G = requests.get(games_url).json()['sports_content']['games']
  if G is not None and len(G)>0:
    return G['game']
  else:
    return []

seasonid = '00214'
startday = datetime.date(2014,10,28)
stopday = datetime.date(2015,04,15)
numdays = (stopday-startday).days
datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]
count=1
season_year = str(startday.year - (startday.month<8))

f = open('/home/gmf/gamelist.csv','w')
for d in datelist:
  diso = str.replace(d.isoformat(),'-','')
  gamelist = get_gamelist(diso)
  # do something with gamelist
  ngames = len(gamelist)
  for n in range(ngames):
    seasonid0 = gamelist[n]['season_id']
    seasonid1 = '00%s%s%s' % (seasonid0[0], seasonid0[3], seasonid0[4])
    if seasonid1 == seasonid:
      gameid,homeabbr,awayabbr = gamelist[n]['id'],gamelist[n]['home']['abbreviation'],gamelist[n]['visitor']['abbreviation']    
      gameid0 = diso + awayabbr + homeabbr
      print d,gameid,seasonid,homeabbr,awayabbr
      f.write(','.join([gameid,seasonid1,gameid0,homeabbr,awayabbr]) + '\n')
f.close()
