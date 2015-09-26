#!/usr/bin/python
import json
import re

season_code = "00214"
gamenum = "2".zfill(5)
gameid = season_code + gamenum

#[box[i]['name'] for i in range(0,13)]

## Load JSON play-by-play and box score
#json_path = '/var/www/data/json'
json_path = 'json'
pbp_file = open(json_path + '/pbp_' + gameid + '.json','r')
pbp = json.loads(pbp_file.read())['rowSet']
box_file = open(json_path + '/bs_' + gameid + '.json','r')
box = json.loads(box_file.read())

## Make dictionary matching player names to codes
# box[4] = player stats
# or each player stat (row) columns are...
# 2 = TEAM_ABBREVIATION
# 5 = PLAYER_NAME
# 6 = START_POSITION
away = box[4]['rowSet'][0][2] # first team abbrev
home = box[4]['rowSet'][-1][2] # last team abbrev
nplayers = len(box[4]['rowSet'])
player_dict = {}
players_in = []
for n in range(0,nplayers):
  tm = box[4]['rowSet'][n][2]
  name = box[4]['rowSet'][n][5]
  firstnm = name.split(' ')[0] # in case there are middle names
  lastnm = name.split(' ')[-1] # in case there are middle names
  code = (firstnm + '_' + lastnm).lower().replace("'","")
  #player_dict[firstnm[0] + lastnm + '_' + tm] = code  
  player_dict[lastnm + '_' + tm] = code
  # players with START_POSITION info are starters
  # we use this to initialize players_in
  pos = box[4]['rowSet'][n][6]
  if pos:
    players_in.append(code)

# Parse play-by-play to deduce who is on court
# Play string is in format: <Name> Play
# **UNLESS** first word is
# 1. MISS (MISS <Name>)
# 2. SUB: (SUB: <Name1> FOR <Name2>)
# 3. <TEAMNAME> (<TEAM> Timeout / etc)
# 4. Jump Ball (skip it)
on_floor = []
prd=1
for p in pbp:
  #
  # did new quarter start at play p?
  # if so, reset players_in based on upcoming play-by-play
  # 
  if prd < p[4]:  # has quarter changed?
    idx = pbp.index(p) # which play are we currently on?
    prd = p[4]
    players_in=[]
    subs=[]
    while len(players_in)<10:
      idx +=1 # put this first to skip quarter change play
      p0 = pbp[idx]
      # away team
      if p0[-3]:
        # mat = player involved
        mat = re.match('(.*?) ', p0[-3]).groups()[0]
        if mat=="MISS":
          mat = re.search('MISS (.*?) ', p0[-3]).groups()[0]
        elif mat=="SUB:":
          mat = re.search(' FOR (.+)', p0[-3]).groups()[0]
          mat2 = re.search('SUB: (.+) FOR ', p0[-3]).groups()[0]
          player_code2 = player_dict[mat2 + '_' + away]
          subs.append(player_code2) # make sure sub doesn't get counted as on the floor yet
        try:
          player_code = player_dict[mat + '_' + away]
          players_in.index(player_code)
        except ValueError:
          try: # make sure sub doesn't get counted as on the floor yet
            subs.index(player_code)
          except ValueError:
            players_in.append(player_code)
        except KeyError:
          0
      # home team
      if p0[-5]:
        mat = re.match('(.*?) ', p0[-5]).groups()[0]
        if mat=="MISS":
          mat = re.search('MISS (.*?) ', p0[-5]).groups()[0]
        elif mat=="SUB:":
          mat = re.search(' FOR (.+)', p0[-5]).groups()[0]
          mat2 = re.search('SUB: (.+) FOR ', p0[-5]).groups()[0]
          player_code2 = player_dict[mat2 + '_' + home]
          subs.append(player_code2) # make sure sub doesn't get counted as on the floor yet
        try:
          player_code = player_dict[mat + '_' + home]
          players_in.index(player_code)
        except ValueError:
          try: # make sure sub doesn't get counted as on the floor yet
            subs.index(player_code)
          except ValueError:
            players_in.append(player_code)
        except KeyError:
          0
  # did substitution occur at play p?
  if p[-3] and re.match('SUB:', p[-3]):
    mat = re.search('SUB: (.+) FOR (.+)', p[-3])
    pl0,pl1 = mat.groups()
    players_in.remove(player_dict[pl1 + '_' + away])
    players_in.append(player_dict[pl0 + '_' + away])
  if p[-5] and re.match('SUB:', p[-5]):
    mat = re.search('SUB: (.+) FOR (.+)', p[-5])
    pl0,pl1 = mat.groups()      
    players_in.remove(player_dict[pl1 + '_' + home])
    players_in.append(player_dict[pl0 + '_' + home])
  on_floor.append([])
  for pl in players_in: on_floor[-1].append(pl)
  #pbp.append(on_floor[-1]) # save to play-by-play

#####
# compute +/- for each player as a test
# 1. start at 0
player_dict0 = {v: k for k,v in player_dict.iteritems()}
d = {}
homescr = 0
awayscr = 0
for p in player_dict0.keys():
  d[p] = 0
# 2. loop over plays
#  for each scoring play, update +/-
for idx in range(1, len(pbp)):
  p = pbp[idx]
  if p[-2]: # if scoring play  
    if p[-3]:
      tm = away
      print 'away- ' + p[-3]
      print on_floor[idx]
      scr = int(p[-2].split(' - ')[0]) - awayscr
      awayscr+=scr
    elif p[-5]:
      tm = home
      print 'home- ' + p[-5]
      print on_floor[idx]
      scr = int(p[-2].split(' - ')[1]) - homescr
      homescr+=scr
    else:
      scr = 0
      tm = away
    for pl in on_floor[idx]:
      if player_dict0[pl][-3:]==tm:
        d[pl]+=scr
      else:
        d[pl]-=scr
    print str(scr)
    #print p[-5],p[-3],p[-2],str(awayscr) + ' - ' + str(homescr) # debug
d
# 3. compare with real +/-
D = {}
for n in range(0,nplayers):
  D[box[4]['rowSet'][n][5]] = box[4]['rowSet'][n][-1]
D

#####
# compute min played for each player as a test

# 0. useful function for computing differences in time
def clockdiff(t1,t2):
  min1,sec1 = t1.split(':')
  min2,sec2 = t2.split(':')
  return float(int(min1)-int(min2)) + (float(sec1)- float(sec2))/60

# 1. start at 0
player_dict0 = {v: k for k,v in player_dict.iteritems()}
d = {}
for pl in player_dict0.keys():
  d[pl] = 0.0

# loop over plays, add time on court for each player
last_time = '12:00'
last_prd = 1
for idx in range(1, len(pbp)):
  # for each player on floor, add time since last play
  p = pbp[idx]
  if last_prd==p[4]:
    dt = clockdiff(last_time, p[6]) # diff in mins
  else:
    dt = 0.0
  last_prd = p[4]
  last_time = p[6]
  for pl in set.intersection(set(on_floor[idx]),set(on_floor[idx-1])):
    d[pl]+=dt
d
# 3. compare with real min
D = {}
for n in range(0,nplayers):
  D[box[4]['rowSet'][n][5]] = box[4]['rowSet'][n][8]
D
