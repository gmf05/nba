#!/usr/bin/python
import json
import sqlite3

JSONPATH = '/home/gmf/Code/repos/nba/json'
DBPATH = '/home/gmf/Code/repos/nba/'
teamCodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA', 'Vancouver Grizzlies':'VAN', 'Seattle SuperSonics':'SEA', 'Washington Bullets':'WSB'}
conn = sqlite3.connect(DBPATH + '/nbaJSON.db')
c = conn.cursor()

#---- make table of Games
c.execute("create table Games ( GAME_ID, SEASON_ID, GAME_CODE, AWAY, HOME )")
#gamelist = open("/home/gmf/Code/repos/nba/csv/gameid_num_all.csv","r").readlines()
gamelist = open("/home/gmf/Code/repos/nba/csv/playoffs_gameid_num_all.csv","r").readlines()

for g in gamelist:
  gameid_num = g.strip()
  print gameid_num
  seasonid = gameid_num[0:5]
  json_file = JSONPATH + '/bs_' + gameid_num + '.json'  
  bs = json.loads(open(json_file,'r').read())['resultSets']
  #bs = json.loads(open(json_file,'r').read())
  gameid = bs[0]['rowSet'][0][5].replace('/','')
  away = gameid[8:11]  
  home = gameid[11:]
  c.execute("insert into Games values (?,?,?,?,?)", [gameid_num, seasonid, gameid, away, home])

gamelist = gamelist[gamelist.index(g):]

# count games
ssn = [str(i) for i in range(96,100)] + [str(i).zfill(2) for i in range(0,14)]
for s in ssn:
  #print s, len(c.execute("select * from Games where SEASON_ID='002" + s + "';").fetchall())
  print s, len(c.execute("select * from Games where SEASON_ID='004" + s + "';").fetchall())

conn.commit()

##
##---- create tables for PlayByPlay, Box Scores, Shots
#gameid_num = '0029600001'
#json_file = JSONPATH + '/pbp_' + gameid_num + '.json'
#pbp = json.loads(open(json_file,'r').read())['resultSets'][0]
#json_file = JSONPATH + '/bs_' + gameid_num + '.json'
#bs = json.loads(open(json_file,'r').read())['resultSets']
#json_file = JSONPATH + '/shots_' + gameid_num + '.json'
#sc = json.loads(open(json_file,'r').read())['resultSets'][0]
#
#pbp['headers'].append('PLAY')
#c.execute("create table PlayByPlay (" + ','.join(pbp['headers']) + ")")
#
#sc['headers'].append('TEAM')
#c.execute("create table Shots (" + ','.join(sc['headers']) + ")")
#
#for i in range(0,len(bs)):
#  colNames = bs[i]['headers']
#  try:
#    colNames[colNames.index('TO')] = 'TOV'
#  except:
#    0
#  c.execute("create table " + bs[i]['name'] + " (" + ','.join(colNames) + ")")

# now loop over games and add data
gamelist = c.execute("select GAME_ID from Games;").fetchall()

def concat_play(playlist):
  p = ''
  for ply in playlist:
    if ply==None:
      0 # do nothing
    else:
      p = p + ply
  return p

for g in gamelist:
  gameid_num = g
  print gameid_num
  json_file = JSONPATH + '/pbp_' + gameid_num + '.json'
  pbp = json.loads(open(json_file,'r').read())['resultSets'][0]
  #pbp = json.loads(open(json_file,'r').read())
  json_file = JSONPATH + '/bs_' + gameid_num + '.json'
  bs = json.loads(open(json_file,'r').read())['resultSets']
  #bs = json.loads(open(json_file,'r').read())
  json_file = JSONPATH + '/shots_' + gameid_num + '.json'
  sc = json.loads(open(json_file,'r').read())['resultSets'][0]
  #sc = json.loads(open(json_file,'r').read())
  #json_file = JSONPATH + '/si_' + gameid + '.json'
  #si = json.loads(open(json_file,'r').read())
  #
  Ncol = len(pbp['headers']) + 1  # adding PLAY
  for p in pbp['rowSet']:
    p.append(concat_play(p[7:10]))
    c.execute('insert into PlayByPlay values (' + ','.join(['?' for j in range(0,Ncol)]) + ')', tuple(p))
  
  Ncol = len(sc['headers']) + 1 # adding TEAM
  for s in sc['rowSet']:
    s.append(teamCodes[s[6]])
    c.execute('insert into Shots values (' + ','.join(['?' for j in range(0,Ncol)]) + ')', tuple(s))
    
  
  for i in range(0,len(bs)):
    tableName = bs[i]['name']
    Ncol = len(bs[i]['headers'])
    for b in bs[i]['rowSet']:
      c.execute('insert into ' + tableName + ' values (' + ','.join(['?' for j in range(0,Ncol)]) + ')', tuple(b))

gamelist = gamelist[gamelist.index(g):]  

  #for i in range(0,len(bs)):
  #  print bs[i]['name']
  
conn.commit() # commit changes
conn.close() # close SQLite connection