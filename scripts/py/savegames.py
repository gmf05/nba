#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 23:28:55 2015

savegames.py
Get lists of games from NBA.com -> save as comma-separated-values (csv)

@author: gmf
"""

import sys
import requests
import datetime

DATAPATH = '/home/gmf/unsynced/nba/data'
#DATAPATH = '/home/gmf/Code/git/nba'
games_url_base = 'http://data.nba.com/5s/json/cms/noseason/scoreboard/%s/games.json'

def get_gamelist_by_date(date_iso):
  games_url = games_url_base % date_iso
  G = requests.get(games_url)
  try:
    return G.json()['sports_content']['games']['game']
  except:
    return []
    
def write_gamelist_by_date(seasonid,startday,stopday):
  numdays = (stopday-startday).days
  datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]

  f = open('%s/csv/gamelist_%s.csv' % (DATAPATH,seasonid), 'w')
  f.write('gameid,seasonid,gameabbr,home,away\n') # write headers
  for d in datelist:
    diso = str.replace(d.isoformat(),'-','')
    gamelist = get_gamelist_by_date(diso)
    # do something with gamelist
    ngames = len(gamelist)
    for n in range(ngames):
      gameid = gamelist[n]['id']
      homeabbr,awayabbr = gamelist[n]['home']['abbreviation'],gamelist[n]['visitor']['abbreviation']    
      gameid0 = diso + awayabbr + homeabbr
      print d,gameid,homeabbr,awayabbr
      if seasonid==gameid[0:5]: # make sure to exclude all start break!
        f.write(','.join([gameid,seasonid,gameid0,homeabbr,awayabbr]) + '\n')
  f.close()

def dateify(date_str):
  m,d,y = date_str.split('/')
  return datetime.date(int(y),int(m),int(d))

def main():
  #seasonyr = '2015'
  seasonyr = sys.argv[1]
  f = open('%s/csv/season_ranges.csv' % DATAPATH,'r')
  f.readline() # drop headers
  for r in f.readlines():
    fields = r.strip().split(',')
    if fields[1]==seasonyr: break
  write_gamelist_by_date(fields[0], dateify(fields[2]), dateify(fields[3]))
  
  #write_gamelist_by_date(seasonid, startday, stopday)

if __name__ == '__main__': 
  main()
