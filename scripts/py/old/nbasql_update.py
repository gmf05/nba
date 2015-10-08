#!/usr/bin/python
import json
import sqlite3

def concat_play(playlist):
  p = ''
  for ply in playlist:
    if ply==None:
      0 # do nothing
    else:
      p = p + ply
  return p

JSONPATH = '/home/gmf/Code/repos/nba/json'
DBPATH = '/home/gmf/Code/repos/nba/'
teamCodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA', 'Vancouver Grizzlies':'VAN', 'Seattle SuperSonics':'SEA', 'Washington Bullets':'WSB'}

#---- update list of games:
# nbaGames.db:
conn = sqlite3.connect(DBPATH + '/nbaGames.db')
c = conn.cursor()

gamelist = open("/home/gmf/Code/repos/nba/csv/playoffs_gameid_num_all.csv","r").readlines()
newgamelist = open("/home/gmf/Code/repos/nba/csv/playoffs_gameid_num_all.csv","r").readlines()
#newgamelist = []
for g in gamelist:
  gameid_num = g.strip()
  print gameid_num
  seasonid = gameid_num[0:5]
  json_file = JSONPATH + '/bs_' + gameid_num + '.json'  
  #bs = json.loads(open(json_file,'r').read())['resultSets']
  bs = json.loads(open(json_file,'r').read())
  gameid = bs[0]['rowSet'][0][5].replace('/','')
  away = gameid[8:11]  
  home = gameid[11:]
  # make sure game not in DB already, if not add to list newgames
  c.execute("insert into Games values (?,?,?,?,?)", [gameid_num, seasonid, gameid, away, home])

conn.commit()
conn.close() # close SQLite connection

# loop over new games and add data:

# update nbaJSON.db:
conn = sqlite3.connect(DBPATH + '/nbaJSON.db')
c = conn.cursor()

for g in newgamelist:
  gameid_num = g.strip()
  print gameid_num
  json_file = JSONPATH + '/pbp_' + gameid_num + '.json'
  #pbp = json.loads(open(json_file,'r').read())['resultSets'][0]
  pbp = json.loads(open(json_file,'r').read())
  json_file = JSONPATH + '/bs_' + gameid_num + '.json'
  #bs = json.loads(open(json_file,'r').read())['resultSets']
  bs = json.loads(open(json_file,'r').read())
  json_file = JSONPATH + '/shots_' + gameid_num + '.json'
  #sc = json.loads(open(json_file,'r').read())['resultSets'][0]
  sc = json.loads(open(json_file,'r').read())

  Ncol = len(sc['headers']) + 1 # adding TEAM
  for s in sc['rowSet']:
    s.append(teamCodes[s[6]])
    c.execute('insert into Shots values (' + ','.join(['?' for j in range(0,Ncol)]) + ')', tuple(s))
    
  Ncol = len(pbp['headers']) + 1  # adding PLAY
  for p in pbp['rowSet']:
    p.append(concat_play(p[7:10]))
    c.execute('insert into PlayByPlay values (' + ','.join(['?' for j in range(0,Ncol)]) + ')', tuple(p))
  
  for i in range(0,len(bs)):
    tableName = bs[i]['name']
    Ncol = len(bs[i]['headers'])
    for b in bs[i]['rowSet']:
      c.execute('insert into ' + tableName + ' values (' + ','.join(['?' for j in range(0,Ncol)]) + ')', tuple(b))

conn.commit() # commit changes
conn.close() # close SQLite connection

# update nbaShots.db:
conn = sqlite3.connect(DBPATH + '/nbaShots.db')
c = conn.cursor()

for g in newgamelist:
  gameid_num = g.strip()
  print gameid_num
  #sc = json.loads(open(json_file,'r').read())['resultSets'][0]
  sc = json.loads(open(json_file,'r').read())
  #json_file = JSONPATH + '/si_' + gameid + '.json'
  #si = json.loads(open(json_file,'r').read())
  #
  Ncol = len(sc['headers']) + 1 # adding TEAM
  for s in sc['rowSet']:
    s.append(teamCodes[s[6]])
    c.execute('insert into Shots values (' + ','.join(['?' for j in range(0,Ncol)]) + ')', tuple(s))
 
conn.commit() # commit changes
conn.close() # close SQLite connection