#!/usr/bin/python
import json
import re

def secElapsed(prd, pclock):
  p = pclock.strip().split(':')
  mins = int(p[0])
  secs = int(p[1])
  if prd<5: # regulation
    return (prd-1)*720 + (11-mins)*60 + (60-secs)
  else: # overtime
    return 2880 + (prd-5)*300 + (5-mins)*60 + (60-secs)

def getPoss(gameid):
  
  ## Load JSON play-by-play and box score
  #json_path = '/var/www/data/json'
  json_path = 'json'
  pbp_file = open(json_path + '/pbp_' + gameid + '.json','r')
  pbp = json.loads(pbp_file.read())['rowSet']
  box_file = open(json_path + '/bs_' + gameid + '.json','r')
  box = json.loads(box_file.read())
  
  away = box[4]['rowSet'][0][2] # first team abbrev
  awaylong = box[3]['rowSet'][0][10]
  home = box[4]['rowSet'][-1][2] # last team abbrev
  homelong = box[3]['rowSet'][0][5] # first team name

  awayposs = []
  homeposs = []
  times = []
  prd=1
  for p in pbp:
    # Decide who has ball at this time by looking ahead?
    # 1. Did new quarter start at play p?
    #if prd < p[4]:
    #  idx = pbp.index(p) # which play are we currently on?
    #  prd = p[4]
    homeplay = p[7]
    awayplay = p[9]
    if True:
      awayposs.append(1)
      homeposs.append(0)
    else:
      awayposs.append(0)
      homeposs.append(1)
    pclock = p[6]    
    times.append(secElapsed(prd, pclock))
    
  return awayposs,homeposs,times
  
# debug
#a,b,times = getPoss(gameid)
#for i in range(0,len(pbp)):
#  print str(pbp[i][4]),pbp[i][6],pbp[i][7],pbp[i][9],str(times[i])
