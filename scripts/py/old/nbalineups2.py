#!/usr/bin/python
import json
import re

def getOnFloor(gameid):
  
  ## Load JSON play-by-play and box score
  #json_path = '/var/www/data/json'
  json_path = 'json'
  game_file = open(json_path + '/si_' + gameid + '.json','r')
  game = json.loads(game_file.read())
  pbp = game['pbp']
  box = game['boxscores']
  
  ## Make dictionary matching player names to codes
  nplayersaway = len(box[0]['playerstats'])
  nplayershome = len(box[1]['playerstats'])
  player_dict = {}
  for n in range(0,nplayersaway):
    pid = box[0]['playerstats'][n]['player']['playerId']
    pname = box[0]['playerstats'][n]['player']['firstName'].lower() + '_' + box[0]['playerstats'][n]['player']['lastName'].lower()
    pname = pname.replace('.','').replace("'",'')
    player_dict[pid] = pname
  for n in range(0,nplayershome):
    pid = box[1]['playerstats'][n]['player']['playerId']
    pname = box[1]['playerstats'][n]['player']['firstName'].lower() + '_' + box[1]['playerstats'][n]['player']['lastName'].lower()
    pname = pname.replace('.','').replace("'",'')
    player_dict[pid] = pname
    
  # first 10 plays are starting lineup
  on_floor = []
  players_in = []
  for p in pbp[0:10]:
    pid = p['players'][0]['playerId']
    players_in.append(player_dict[pid])
  for n in range(0,10):
    on_floor.append([])
    for pl in players_in: on_floor[-1].append(pl)
  # Parse play-by-play to deduce who is on court
  # Play string is in format: <Name> Play
  # **UNLESS** first word is
  # 1. MISS (MISS <Name>)
  # 2. SUB: (SUB: <Name1> FOR <Name2>)
  # 3. <TEAMNAME> (<TEAM> Timeout / etc)
  # 4. Jump Ball (skip it)

  prd=1
  for p in pbp[10:]:
    # 1. Did new quarter start at play p?
    # If so, reset players_in based on upcoming play-by-play  
    if prd < p['period']:
      idx = pbp.index(p) # which play are we currently on?
      prd = p['period']
      players_in=[]
      subs=[]
      while len(players_in)<10: # look ahead for first 10 players
        idx +=1 # put this first to skip quarter change play
        if idx==len(pbp):
          while len(players_in)<10: players_in.append(u'Unknown')
          break        
        p0 = pbp[idx]
        playtext = p0['playText']
        if p0['players']:
          pid = p0['players'][0]['playerId'] # who's coming in?
          try:
            players_in.index(player_dict[pid])
          except ValueError:
            if re.match('Substitution:', playtext):                
              try:
                subs.index(player_dict[pid])
              except ValueError:
                subs.append(player_dict[pid])
              pid1 = p0['players'][1]['playerId'] # who's coming in?
              try:
                players_in.index(player_dict[pid1])
              except:
                players_in.append(player_dict[pid1])                                  
            else:
              try:                
                subs.index(player_dict[pid])
              except ValueError:
                try:
                  players_in.index(player_dict[pid])
                except ValueError:
                  players_in.append(player_dict[pid])
    # 2. Did substitution occur at play p?
    # If so, swap players
    playtext = p['playText']
    if re.match('Substitution:', playtext):
      pid0 = p['players'][0]['playerId']
      pid1 = p['players'][1]['playerId']
      players_in.remove(player_dict[pid1])
      players_in.append(player_dict[pid0])
    # Write players currently on floor to master list
    on_floor.append([])
    for pl in players_in: on_floor[-1].append(pl)
    #pbp.append(on_floor[-1]) # save to play-by-play
  
  return on_floor
  

######
## compute +/- for each player as a test
#
### Make list matching player teams to player IDs
#nplayersaway = len(box[1]['playerstats'])
#nplayershome = len(box[0]['playerstats'])
#pteams = {}
#for n in range(0,nplayersaway):
#  pid = box[1]['playerstats'][n]['player']['playerId']
#  pteams[player_dict[pid]]=0
#for n in range(0,nplayershome):
#  pid = box[0]['playerstats'][n]['player']['playerId']
#  pteams[player_dict[pid]]=1
#
## 1. start at 0
#d = {}
#homescr = 0
#awayscr = 0
#for p in player_dict.values():
#  d[p] = 0
## 2. loop over plays
##  for each scoring play, update +/-
#for idx in range(10, len(pbp)):
#  p = pbp[idx]
#  hscr = p['homeScore']
#  vscr = p['visitorScore']  
#  if hscr>homescr:
#    scr = hscr-homescr
#    for pl in on_floor[idx]:
#      if pteams[pl]:
#        d[pl]+=scr
#      else:
#        d[pl]-=scr
#  if vscr>awayscr:
#    scr = vscr-awayscr
#    for pl in on_floor[idx]:
#      if pteams[pl]:
#        d[pl]-=scr
#      else:
#        d[pl]+=scr
#  homescr = hscr
#  awayscr = vscr
#d
#
## 3. compare with real +/-
#nplayersaway = len(box[1]['playerstats'])
#nplayershome = len(box[0]['playerstats'])
#D = {}
#for n in range(0,nplayersaway):
#  D[player_dict[box[1]['playerstats'][n]['player']['playerId']]] = box[1]['playerstats'][n]['plusMinus']
#for n in range(0,nplayershome):
#  D[player_dict[box[0]['playerstats'][n]['player']['playerId']]] = box[0]['playerstats'][n]['plusMinus']
#D
#
######
## compute min played for each player as a test
#
## 0. useful function for computing differences in time
#def clockdiff(t1,t2):
#  min1,sec1 = t1.split(':')
#  min2,sec2 = t2.split(':')
#  return float(int(min1)-int(min2)) + (float(sec1)- float(sec2))/60
#
## 1. start at 0
#d = {}
#for pl in player_dict.values():
#  d[pl] = 0.0
#
## loop over plays, add time on court for each player
#last_time = '12:00'
#last_prd = 1
#for idx in range(1, len(pbp)):
#  # for each player on floor, add time since last play
#  p = pbp[idx]
#  if last_prd==p['period']:
#    new_time = str(p['time']['minutes']) + ':' + str(p['time']['seconds']).zfill(3)
#    dt = clockdiff(last_time, new_time) # diff in mins
#  else:
#    dt = 0.0
#  last_prd = p['period']
#  last_time = str(p['time']['minutes']) + ':' + str(p['time']['seconds']).zfill(3)
#  for pl in set.intersection(set(on_floor[idx]),set(on_floor[idx-1])):
#    d[pl]+=dt
#d
#
## 3. compare with real min
#nplayersaway = len(box[0]['playerstats'])
#nplayershome = len(box[1]['playerstats'])
#D = {}
#for n in range(0,nplayersaway):
#  D[player_dict[box[0]['playerstats'][n]['player']['playerId']]] = box[0]['playerstats'][n]['minutesPlayed']
#for n in range(0,nplayershome):
#  D[player_dict[box[1]['playerstats'][n]['player']['playerId']]] = box[1]['playerstats'][n]['minutesPlayed']
#D
