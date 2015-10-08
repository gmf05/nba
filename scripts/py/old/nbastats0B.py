#!/usr/bin/python
# code to turn nba play-by-play data into point process for a particular game event
# e.g. get the sequence of shot attempts (per second) [0 0 0 0 1 0 0 0 0 0 ...]
#
#import sys
#import json
import pymongo
import sqlite3
import re
import numpy as np
import scipy.io as spio

def minGameLength(nsec):
  regSec = 2880
  diffsec = nsec - regSec
  if diffsec<=0:
    gamelength = regSec
  else:
    gamelength = regSec + 300*np.ceil(diffsec/300.0)
  return gamelength

def gameLengthPeriods(nperiods):
  if nperiods==4:
    return 2880
  elif nperiods>4:
    return 2880 + 300*(nperiods-4)
  else:
    return None

def secClockStr(period, clockStr):
  t = clockStr.split(":")
  if period<=4:
    return 720*(period-1) + 60*(11-int(t[0])) + 60-int(t[1])
  else:
    return 2880 + 300*(period-5) + 60*(4-int(t[0])) + 60-int(t[1])

def secElapsed(period, minRemain, secRemain):
  if period<=4:
    return 720*(period-1) + 60*(11-minRemain) + (60-secRemain)    
  else:
    return 2880 + (period-5)*300 + 60*(4-minRemain) + (60-secRemain)

def ppShots(gameid, team):
  #from pymongo import MongoClient
  client = pymongo.MongoClient()
  db = client.nba
  shots = db.shots.find({"GAME_ID":gameid},{"PERIOD":1, "MINUTES_REMAINING":1, "SECONDS_REMAINING":1, "LOC_X":1,"LOC_Y":1, "SHOT_TYPE":1, "SHOT_MADE_FLAG":1, "TEAM":1, "_id":0})
  for s in shots: print s

  # get s = last shot
  for s in shots: nperiods = s['PERIOD']
  NT = gameLengthPeriods(nperiods)
  pp = np.zeros([4,NT])
  opp = np.zeros([4,NT])
  for s in shots:
    nsec = secElapsed(s['PERIOD'],s['MINUTES_REMAINING'],s['SECONDS_REMAINING'])
    nsec = nsec - (nsec==2880)
    row = 2*(s['SHOT_TYPE'][0:3]=='3PT') # is shot a 3-pointer?
    if s['TEAM']==team:
      pp[row, nsec] += 1
      if s['SHOT_MADE_FLAG']: # is shot made?
        pp[row+1, nsec] += 1
    else:
      opp[row, nsec] += 1
      if s['SHOT_MADE_FLAG']: # is shot made?
        opp[row+1, nsec] += 1
  return pp,opp

def ppShots2(gameid, team):
  shotlist = c.execute("select PERIOD,MINUTES_REMAINING,SECONDS_REMAINING,LOC_X,LOC_Y,SHOT_TYPE,SHOT_MADE_FLAG,TEAM from Shots where GAME_ID='" + gameid + "';").fetchall()
  nperiods = shotlist[-1][0]
  NT = gameLengthPeriods(nperiods)
  pp = np.zeros([6,NT])
  opp = np.zeros([6,NT])
  for s in shotlist:
    nsec = secElapsed(s[0],s[1],s[2])
    nsec = nsec - (nsec==2880)
    row = 2*(s[5][0:3]=='3PT') # is shot a 3-pointer?
    if s[-1]==team:
      pp[row, nsec] += 1
      pp[4:6, nsec] = s[3:5]
      if s[-2]: # is shot made?
        pp[row+1, nsec] += 1
    else:
      opp[row, nsec] += 1
      opp[4:6, nsec] = s[3:5]
      if s[-2]: # is shot made?
        opp[row+1, nsec] += 1
  return pp,opp

def ppEtc(gameid, team, eventName):
  # eventName = '[Tt]urnover'
  #eventName = '[Rr]ebound'
  # eventName = '[Ss]teal'
  x,x,x,away,home = c.execute("select * from Games where GAME_ID='" + gameid + "';").fetchall()[0]
  isHome = (team==home)
  ind = 3 + int(isHome)
  playlist = c.execute("select PERIOD,PCTIMESTRING,SCORE,VISITORDESCRIPTION,HOMEDESCRIPTION from PlayByPlay where GAME_ID='" + gameid + "';").fetchall()
  nperiods = playlist[-1][0] # in which period does last play happen? = number of periods
  NT = gameLengthPeriods(nperiods) # how long is game in sec?
  pp = np.zeros([1,NT])
  for p in playlist:
    if p[ind] and re.search(eventName, p[ind]):
      nsec = secClockStr(p[0],p[1])
      nsec = nsec - (nsec==2880)
      pp[0, nsec] += 1
  np.sum(pp)
  return pp

def main():
  #teamCodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA', 'Vancouver Grizzlies':'VAN', 'Seattle SuperSonics':'SEA', 'Washington Bullets':'WSB'}
  #JSONPATH = '/home/gmf/Code/repos/nba/json'
  DBPATH = '/home/gmf/Code/repos/nba/'
  #conn = sqlite3.connect(DBPATH + '/nbaJSON.db')
  conn = sqlite3.connect(DBPATH + '/nbaShots.db')
  c = conn.cursor()
  # 
  season = '00214'
  team = 'ATL'
  gamelist = c.execute("select * from Games where SEASON_ID='" + season + "' and (AWAY='" + team + "' or HOME='" + team + "')").fetchall()
  pp = []
  #nprds = []
  for g in gamelist:
    gameid = g[0]
    print g[2]
    pp0,opp0 =  ppShots2(gameid, team)
    pp.append(pp0)
  spio.matlab.savemat('test.mat', {'shots':'pp','team':'team','season':'season'})

if __name__ == "__main__":
  main()



# 