#!/usr/bin/python
import json
import re

def getOnFloor(gameid):
  
  ## Load JSON play-by-play and box score
  #json_path = '/var/www/data/json'
  json_path = 'json'
  pbp_file = open(json_path + '/pbp_' + gameid + '.json','r')
  pbp = json.loads(pbp_file.read())['rowSet']
  box_file = open(json_path + '/bs_' + gameid + '.json','r')
  box = json.loads(box_file.read())
  
  ## Make dictionary matching player names to codes 
  ## Initialize list of players on court with starters
  #
  # box[4] = player stats
  # or each player stat (row) columns are...
  # 2 = TEAM_ABBREVIATION
  # 5 = PLAYER_NAME
  # 6 = START_POSITION
  #
  away = box[4]['rowSet'][0][2] # first team abbrev
  awaylong = box[3]['rowSet'][0][10]
  home = box[4]['rowSet'][-1][2] # last team abbrev
  homelong = box[3]['rowSet'][0][5] # first team name
  nplayers = len(box[4]['rowSet'])
  player_dict = {}
  players_in = []
  for n in range(0,nplayers):
    tm = box[4]['rowSet'][n][2]
    name = box[4]['rowSet'][n][5]
    code = name.lower().replace("'","").replace('.','').replace(' ','_')
    pbp_plyr_code = name.split(' ')[1] + '_' + tm
    #player_dict[firstnm[0] + lastnm + '_' + tm] = code  
    player_dict[pbp_plyr_code] = code
    # players with START_POSITION [6] info are starters
    if box[4]['rowSet'][n][6]:
      players_in.append(code)

  ## Modify player_dict as necessary to accomodate, 
  # e.g. Hardaway Jr. or Marc Morris as pbp names
  #
  #

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
    # 1. Did new quarter start at play p?
    # If so, reset players_in based on upcoming play-by-play  
    if prd < p[4]:
      idx = pbp.index(p) # which play are we currently on?
      prd = p[4]
      players_in=[]
      subs=[]
      while len(players_in)<10: # look ahead for first 10 players
        idx +=1 # put this first to skip quarter change play
        if idx==len(pbp):
          while len(players_in)<10: players_in.append(u'Unknown')
          break
        p0 = pbp[idx]
        homeplay = p0[7]
        awayplay = p0[9]
        # away team
        if awayplay:
          mat = re.match('(.*?) ', awayplay).groups()[0] # player involved
          #print mat, mat.upper()          
          if mat=="MISS":
            mat = re.search('MISS (.*?) ', awayplay).groups()[0]
          elif mat=="SUB:":
            mat = re.search(' FOR (.+)', awayplay).groups()[0]
            mat2 = re.search('SUB: (.+) FOR ', awayplay).groups()[0]
            player_code2 = player_dict[mat2 + '_' + away]
            subs.append(player_code2) # make sure sub doesn't get counted as on the floor yet
          elif mat=="Jump":
            mat2,mat = re.search("Jump Ball (.*?) vs. (.*?)", homeplay).groups()
          if mat==awaylong or mat==awaylong.upper():
            0 # do nothing
          else:
            try:
              player_code = player_dict[mat + '_' + away]
              players_in.index(player_code)
            except ValueError:
              try: # make sure sub doesn't get counted as on the floor yet
                subs.index(player_code)
              except ValueError:
                players_in.append(player_code)
            except KeyError:
              print mat
        # home team
        if homeplay:
          mat = re.match('(.*?) ', homeplay).groups()[0] # player involved
          #print mat, mat.upper()
          if mat=="MISS":
            mat = re.search('MISS (.*?) ', homeplay).groups()[0]
          elif mat=="SUB:":
            mat = re.search(' FOR (.+)', homeplay).groups()[0]
            mat2 = re.search('SUB: (.+) FOR ', homeplay).groups()[0]
            player_code2 = player_dict[mat2 + '_' + home]
            subs.append(player_code2) # make sure sub doesn't get counted as on the floor yet
          elif mat=="Jump":
            mat,mat2 = re.search("Jump Ball (.*?) vs. (.*?)", homeplay).groups()
          if mat==homelong or mat==homelong.upper():
            0
          else:
            try:
              player_code = player_dict[mat + '_' + home]
              players_in.index(player_code)
            except ValueError:
              try: # make sure sub doesn't get counted as on the floor yet
                subs.index(player_code)
              except ValueError:
                players_in.append(player_code)
            except KeyError:
              print mat
          #  0
    # 2. Did substitution occur at play p?
    # If so, swap players              
    homeplay = p[7]
    awayplay = p[9]
    if awayplay and re.match('SUB:', awayplay):
      mat = re.search('SUB: (.+) FOR (.+)', awayplay)
      pl0,pl1 = mat.groups()
      players_in.remove(player_dict[pl1 + '_' + away])
      players_in.append(player_dict[pl0 + '_' + away])
    if homeplay and re.match('SUB:', homeplay):
      mat = re.search('SUB: (.+) FOR (.+)', homeplay)
      pl0,pl1 = mat.groups()      
      players_in.remove(player_dict[pl1 + '_' + home])
      players_in.append(player_dict[pl0 + '_' + home])
    # Write players currently on floor to master list
    on_floor.append([])
    for pl in players_in: on_floor[-1].append(pl)
    #pbp.append(on_floor[-1]) # save to play-by-play
    
  return on_floor