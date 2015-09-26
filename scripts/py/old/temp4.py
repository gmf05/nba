#!/usr/bin/python
gameid = '20141207DENATL'
#json_path = '/var/www/data/json'
json_path = 'json'
game_file = open(json_path + '/si_' + gameid + '.json','r')
game = json.loads(game_file.read())
pbp = game['pbp']
box = game['boxscores']
on_floor = getOnFloor(gameid)

#####
# compute +/- for each player as a test

## Make list matching player teams to player IDs
nplayersaway = len(box[1]['playerstats'])
nplayershome = len(box[0]['playerstats'])
pteams = {}
for n in range(0,nplayersaway):
  pid = box[1]['playerstats'][n]['player']['playerId']
  pteams[player_dict[pid]]=0
for n in range(0,nplayershome):
  pid = box[0]['playerstats'][n]['player']['playerId']
  pteams[player_dict[pid]]=1

# 1. start at 0
d = {}
homescr = 0
awayscr = 0
for p in player_dict.values():
  d[p] = 0
# 2. loop over plays
#  for each scoring play, update +/-
for idx in range(10, len(pbp)):
  p = pbp[idx]
  hscr = p['homeScore']
  vscr = p['visitorScore']  
  if hscr>homescr:
    scr = hscr-homescr
    for pl in on_floor[idx]:
      if pteams[pl]:
        d[pl]+=scr
      else:
        d[pl]-=scr
  if vscr>awayscr:
    scr = vscr-awayscr
    for pl in on_floor[idx]:
      if pteams[pl]:
        d[pl]-=scr
      else:
        d[pl]+=scr
  homescr = hscr
  awayscr = vscr
d

# 3. compare with real +/-
nplayersaway = len(box[1]['playerstats'])
nplayershome = len(box[0]['playerstats'])
D = {}
for n in range(0,nplayersaway):
  D[player_dict[box[1]['playerstats'][n]['player']['playerId']]] = box[1]['playerstats'][n]['plusMinus']
for n in range(0,nplayershome):
  D[player_dict[box[0]['playerstats'][n]['player']['playerId']]] = box[0]['playerstats'][n]['plusMinus']
D

#####
# compute min played for each player as a test

# 0. useful function for computing differences in time
def clockdiff(t1,t2):
  min1,sec1 = t1.split(':')
  min2,sec2 = t2.split(':')
  return float(int(min1)-int(min2)) + (float(sec1)- float(sec2))/60

# 1. start at 0
d = {}
for pl in player_dict.values():
  d[pl] = 0.0

# loop over plays, add time on court for each player
last_time = '12:00'
last_prd = 1
for idx in range(1, len(pbp)):
  # for each player on floor, add time since last play
  p = pbp[idx]
  if last_prd==p['period']:
    new_time = str(p['time']['minutes']) + ':' + str(p['time']['seconds']).zfill(3)
    dt = clockdiff(last_time, new_time) # diff in mins
  else:
    dt = 0.0
  last_prd = p['period']
  last_time = str(p['time']['minutes']) + ':' + str(p['time']['seconds']).zfill(3)
  for pl in set.intersection(set(on_floor[idx]),set(on_floor[idx-1])):
    d[pl]+=dt
d

# 3. compare with real min
nplayersaway = len(box[0]['playerstats'])
nplayershome = len(box[1]['playerstats'])
D = {}
for n in range(0,nplayersaway):
  D[player_dict[box[0]['playerstats'][n]['player']['playerId']]] = box[0]['playerstats'][n]['minutesPlayed']
for n in range(0,nplayershome):
  D[player_dict[box[1]['playerstats'][n]['player']['playerId']]] = box[1]['playerstats'][n]['minutesPlayed']
D

##### playing with sportvu data #################
import urllib2 # query web
import json # parse json
import re # regular expressions

gameid = '0021400001'
sv_url = 'http://stats.nba.com/stats/locations_getmoments/?eventid=*EVENTID*&gameid=*GAMEID*'
fw = open("sv_out.csv","w")

for eventnum in range(1,30):
  eventid = str(eventnum)
  print eventid
  try:
    j = json.loads(urllib2.urlopen(sv_url.replace('*EVENTID*',eventid).replace('*GAMEID*', gameid)).read())
    for m in j['moments']:
      #fw.write(','.join([str(m[2]),str(m[3])]) + '\n')
      #fw.write(','.join([str(m[5][0][2]),str(m[5][0][3])]) + '\n')
      #
      # track specific player
      pids = [m[5][n][1] for n in range(1,11)]
      try:
        i = pids.index(203076) # anthony davis
        fw.write(','.join([str(m[5][i][2]),str(m[5][i][3])]) + '\n')
      except urllib2.HTTPError:
        0
  except:
    0
fw.close()


####### get sportvu data for full game
#!/usr/bin/python
import urllib2 # query web
import json # parse json

if __name__ == '__main__':

  json_path = 'json'
  
  for gamenum in range(1, 10):
    gameid = '00214' + str(gamenum).zfill(5)
    pbp_file = open(json_path + '/pbp_' + gameid + '.json','r')
    pbp = json.loads(pbp_file.read())['rowSet']
    sv_url = 'http://stats.nba.com/stats/locations_getmoments/?eventid=*EVENTID*&gameid=*GAMEID*'
    
    eventids = []
    for p in pbp[1:]:
      eventids.append(p[1])
    print "Number of events: " + str(len(eventids))
    
    # initialize object with sportvu data
    j = json.loads(urllib2.urlopen(sv_url.replace('*EVENTID*','1').replace('*GAMEID*', gameid)).read())
    J = {}
    J['moments'] = []
    J['visitor'] = j['visitor']
    J['gamedate'] = j['gamedate']
    J['gameid'] = j['gameid']
    J['home'] = j['home']

    # loop over all events, get sport vu data for each    
    for eventid in eventids:
      eventid_str = str(eventid)
      print gameid, eventid_str # debug
      J['moments'].append(json.loads(urllib2.urlopen(sv_url.replace('*EVENTID*',eventid_str).replace('*GAMEID*', gameid)).read())['moments'])
      
    # save concatenated json data
    fw = open("json/sv_" + gameid + ".json","w")
    json.dump(J, fw)
    fw.close()
    
    
### TRYING TOR CONNECTION ###
import socket
import socks
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

def connectTor():
## Connect to Tor for privacy purposes
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9150, True)
    socket.socket = socks.socksocket
    print "connected to Tor!"

connectTor()
gameid = '0021400001'
sv_url = 'http://stats.nba.com/stats/locations_getmoments/?eventid=*EVENTID*&gameid=*GAMEID*'
url = sv_url.replace('*EVENTID*','1').replace('*GAMEID*', gameid)
driver = webdriver.Chrome()
driver.get(url)


####
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

fw = open("ATLBKN_shots.csv","w")
for gamenum in range(101, 105):
  gameid = '00414' + str(gamenum).zfill(5) # HAWKS-NETS PLAYOFFS
  print gameid
  JSONPATH = '/home/gmf/Code/repos/nba/json'
  json_file = JSONPATH + '/sc_' + gameid + '.json'
  sc = json.loads(open(json_file,'r').read())['rowSet']
  for s in sc:
    x,y,made=s[17],s[18],s[20]
    tm = int(s[6]=='Atlanta Hawks')
    fw.write(','.join([str(x),str(y),str(made),str(tm)]) + '\n')
fw.close()

##

# for all games, go through playbyplay and add team

# code to turn nba play-by-play data into point process for a particular game event
# e.g. get the sequence of shot attempts (per second) [0 0 0 0 1 0 0 0 0 0 ...]
#
#import sys
#import json
import sqlite3
#teamCodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA', 'Vancouver Grizzlies':'VAN', 'Seattle SuperSonics':'SEA', 'Washington Bullets':'WSB'}
DBPATH = '/home/gmf/Code/repos/nba/'
conn = sqlite3.connect(DBPATH + '/nbaJSON.db')
#conn = sqlite3.connect(DBPATH + '/nbaShots.db')
c = conn.cursor()
c.execute('alter table PlayByPlay add TEAM')

gamelist = c.execute('select * from Games;').fetchall()
for g in gamelist:
  gameid_num,seasonid,gameid,away,home = g
  print gameid
  playlist = c.execute("select * from PlayByPlay where GAME_ID='" + gameid_num + "';").fetchall()
  for p in playlist:
    # which team?
    if p[7]==None and not p[9]==None:
      # team is home
      0 
    elif p[9]==None and not p[7]==None:
      # team is away
      0
    elif not p[7]==None and not p[9]==None:
      print p[-1]
      # team is both
    # add info


#### try printing json in better format

#!/usr/bin/python
import json
import sqlite3

JSONPATH = '/home/gmf/Code/repos/nba/json'
DBPATH = '/home/gmf/Code/repos/nba/'
conn = sqlite3.connect(DBPATH + '/nbaGames.db')
c = conn.cursor()
gamelist = c.execute("select GAME_ID from Games;").fetchall()

#json_file = JSONPATH + '/pbp_' + gameid_num + '.json'
#pbp = json.loads(open(json_file,'r').read())['resultSets'][0]
#json_file = JSONPATH + '/bs_' + gameid_num + '.json'
#bs = json.loads(open(json_file,'r').read())['resultSets']

for g in gamelist:
  gameid_num = g[0]
  print gameid_num
  json_file = JSONPATH + '/shots_' + gameid_num + '.json'
  sc = json.loads(open(json_file,'r').read())['resultSets'][0]
  #sc = json.loads(open(json_file,'r').read())
  headers = sc['headers']
  N = len(headers)
  shots = sc['rowSet']
  
  fw = open(JSONPATH + '/shots2_' + gameid_num + '.json','w')
  fw.write('[\n'))
  for s in shots:
    fw.write('\t{\n')
    for n in range(0,N):
      try: # for strings
        if n<N-1:
          fw.write('\t\t"' + headers[n] + '": "' + s[n] + '",\n')
        else:
          fw.write('\t\t"' + headers[n] + '": "' + s[n] + '"\n')
      except: # for numbers
        if n<N-1:
          fw.write('\t\t"' + headers[n] + '": ' + str(s[n]) + ',\n')
        else:
          fw.write('\t\t"' + headers[n] + '": ' + str(s[n]) + '\n')
    fw.write('\t},\n')
  fw.write(']\n')
  fw.close()

#-