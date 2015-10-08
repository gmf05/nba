# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 01:25:31 2015

@author: gmf
"""
import re
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from mpl_toolkits.mplot3d import Axes3D
#import pp_tools as pp

team_list = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']
USERHOME = '/home/gmf' # Thinkpad
#USERHOME = '/home/gfiddy' # Office
NBAHOME = USERHOME + '/Code/git/nba'
DATAPATH = USERHOME + '/unsynced/nba/data' # Thinkpad
#DATAPATH = USERHOME + '/External/Code/git/nba'
gameid = '0021400001'

def get_boxscore(gameid):
  J = json.load( open( '%s/json/bs_%s.json' % (DATAPATH,gameid), 'r' ) )
  return [pd.DataFrame(data=j['rowSet'],columns=j['headers']) for j in J]

def get_pbp(gameid):
  J = json.load( open( '%s/json/pbp_%s.json' % (DATAPATH,gameid), 'r' ) )
  return pd.DataFrame(data=J['rowSet'],columns=J['headers'])

def get_shots(gameid):
  J = json.load( open( '%s/json/shots_%s.json' % (DATAPATH,gameid), 'r' ) )
  return pd.DataFrame(data=J['rowSet'],columns=J['headers'])

def get_jersey(J, playerid):
  0

def get_sportvu(gameid,eventnum):
  #
  # Important to remember: Event number indexing in play-by-play begins at 1!
  if eventnum==0:
    print 'Warning: Event Num = 0 passed. Switching to event number 1.'
    eventnum+=1
  #
  J = json.load( open( '%s/json/sv_%s_%s.json' % (DATAPATH,gameid,str(eventnum).zfill(4)), 'r' ) )
  #player_headers = J['home']['players'][0].keys()
  #home_team = pd.DataFrame(data=[J['home']['players'][i].values() for i in range(len(J['home']['players']))], columns=player_headers)
  #away_team = pd.DataFrame(data=[J['visitor']['players'][i].values() for i in range(len(J['visitor']['players']))], columns=player_headers)
  home_jerseys = dict([(J['home']['players'][k]['playerid'], J['home']['players'][k]['jersey']) for k in range(len(J['home']['players']))])
  away_jerseys = dict([(J['visitor']['players'][k]['playerid'], J['visitor']['players'][k]['jersey']) for k in range(len(J['visitor']['players']))])
  jerseys = dict(home_jerseys, **away_jerseys)
  moments = J['moments']
  #  
  # SHOULD WE DOWNSAMPLE THE NUMBER OF MOMENTS CHOSEN????
  # 
  num_moments = len(moments)
  playerx = range(num_moments)
  playery = range(num_moments)
  playerid = range(num_moments)
  playernum = range(num_moments)
  ballx = range(num_moments)
  bally = range(num_moments)
  ballz = range(num_moments)
  shotclock_remain = range(num_moments)
  sec_remain = range(num_moments)
  momentid = range(num_moments)
  period = range(num_moments)
  # for loop over moments  
  for i in range(num_moments):
    period[i], momentid[i], sec_remain[i], shotclock_remain[i]  = moments[i][0:4]    
    ballx[i],bally[i],ballz[i] = moments[i][-1][0][2:5]
    playerid[i] = range(10)
    playerx[i] = range(10)
    playery[i] = range(10)
    playernum[i] = range(10)
    # for loop over players
    for j in range(10):
      playerid[i][j] = moments[i][-1][j+1][1] # +1 bc ball is row 0!
      playerx[i][j], playery[i][j] = moments[i][-1][j+1][2:4] # +1 bc ball is row 0!
      playernum[i][j] = jerseys[playerid[i][j]]
  D = {'momentid':momentid, 'period':period, 'sec_remain':sec_remain, 'shotclock_remain':shotclock_remain, 'ballx':ballx, 'bally':bally, 'ballz':ballz, 'playerx':playerx, 'playery':playery, 'playerid':playerid, 'playernum':playernum}
  return pd.DataFrame(D)

def remap_sv_coord(x,y):
  x0 = y
  y0 = x
  return x0,y0

#gameid = '0021200705' # TEST LOADING FUNCTIONS
shots = get_shots(gameid)
boxscore = get_boxscore(gameid)
pbp = get_pbp(gameid)

def get_reb_eventnum(gameid):
  pbp = get_pbp(gameid)
  homereb = []
  awayreb = []
  for i,p in pbp.iterrows():
    if p.HOMEDESCRIPTION and re.search('REBOUND', p.HOMEDESCRIPTION):
      homereb.append(p)
    if p.VISITORDESCRIPTION and re.search('REBOUND', p.VISITORDESCRIPTION):
      awayreb.append(p)
  i0 = [a.EVENTNUM for a in homereb]
  i1 = [a.EVENTNUM for a in awayreb]
  #i2 = np.union1d(i0,i1)
  return i0,i1

def get_team_games(team, seasonid='00214'):
  games = open('%s/csv/games_00-14.csv' % DATAPATH, 'r')
  G = games.readlines()
  headers = G[0].strip().split(',')
  G.remove(G[0])
  G = [g.strip().split(',') for g in G]
  D = pd.DataFrame(data=G, columns=headers)
  D = D.iloc[np.where(D.seasonid==seasonid)] # Get just season of interest
  #gameids = np.union1d(np.flatnonzero(D.home==team), np.flatnonzero(D.away==team))
  gameids = np.concatenate((np.flatnonzero(D.home==team), np.flatnonzero(D.away==team)))
  return D.gameid_num.iloc[gameids].values

# Helper function to draw circles
theta = np.arange(0,2*np.pi,0.3)
def draw_circ(x0, y0, color='b'):
  R = 1.8
  xs = x0 + R*np.cos(theta)
  ys = y0 + R*np.sin(theta)
  plt.fill(xs,ys,color=color)
  return xs, ys

# draw court
def draw_court(axis):
  # SIMPLE VERSION, IMAGE BASED
  img = mpimg.imread(NBAHOME + '/image/nba_court_T.png')
  implot = plt.imshow(img,extent=axis, zorder=0)
  # add border
  #
# given gameid, get pp rebounds for that game ...?  
#get_reb_pp(gameid):
#  0    
  
#%% PLOT BALL MOVEMENT IN 3D!
sv = get_sportvu(gameid, 1)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
plt.plot(sv.ballx, sv.bally, sv.ballz)

#%% Find all rebound events, metadata
pbp = get_pbp(gameid)
homereb = []
awayreb = []
for i,p in pbp.iterrows():
  if p.HOMEDESCRIPTION and re.search('REBOUND', p.HOMEDESCRIPTION):
    homereb.append(p)
  if p.VISITORDESCRIPTION and re.search('REBOUND', p.VISITORDESCRIPTION):
    awayreb.append(p)

i0 = [a.EVENTNUM for a in homereb]
i1 = [a.EVENTNUM for a in awayreb]
i2 = np.union1d(i0,i1)

### DEBUG: Print event information
#for i in i2:
#  try:
#    sv = get_sportvu(gameid, i)
#    qtr = playi.PERIOD.values[0]
#    tstart = sv.sec_remain.iloc[0]
#    tend =sv.sec_remain.iloc[-1]
#    playi = pbp.iloc[np.flatnonzero(pbp.EVENTNUM==i)]
#    if playi.HOMEDESCRIPTION.values[0]:
#      play_description = str(playi.HOMEDESCRIPTION.values[0])
#    else:
#      play_description = str(playi.VISITORDESCRIPTION.values[0])
#    treb = playi.PCTIMESTRING.values[0]
#    print 'Event number %i. Quarter: %d. Start time: %d. End time: %d. Rebound time: %s.' % (i,qtr,tstart,tend,treb)
#    print play_description
#  except:
#    print 'Problem on event number %i' % i
#  print ''
  
# Plotting the ball in 3D for multiple rebounds!
fig = plt.figure()
count=1
for i in i2[0:6]:
  sv = get_sportvu(gameid, i)
  ax = fig.add_subplot('23%i' % count, projection='3d')
  count+=1
  plt.plot(sv.ballx, sv.bally, sv.ballz)

#%% Plotting players & ball as 2D movie!

plt.close('all')

# Court dimensions
xmin = 0
xmax = 100
ymin = 0
ymax = 50

# Radius & angle of filled circles for ball, players
r=1.8
theta = np.arange(0,2*np.pi,0.05)

# Event number
i0,i1 = get_reb_eventnum(gameid)
i2 = np.union1d(i0,i1)
#eventnum=i2[0]

# SportVu start & stop times for given event num
sv = get_sportvu(gameid, eventnum)
tstart = sv.sec_remain.iloc[0]
tend =sv.sec_remain.iloc[-1]

# Play-by-Play data for given event num
# TO DO: DON'T GET INDEX I -- GET CLOSEST TO CURRENT TIME!!
playi = pbp.iloc[np.flatnonzero(pbp.EVENTNUM==eventnum)]
treb = playi.PCTIMESTRING.values[0]
qtr = playi.PERIOD.values[0]
if playi.HOMEDESCRIPTION.values[0]:
  play_description = str(playi.HOMEDESCRIPTION.values[0])
else:
  play_description = str(playi.VISITORDESCRIPTION.values[0])

## Shot information for given event???
#shots = get_shots(gameid)
#shots_missed = shots.iloc[ np.flatnonzero( 1 - shots.SHOT_MADE_FLAG ) ]
## for any play-by-play rebound event, get nearest preceding miss!
## NOTE: need to modify GAME_EVENT_ID : should not be equal to i!
## should be last number that's < i!
#shot = shots_missed.iloc[ np.flatnonzero(shots_missed.GAME_EVENT_ID == i) ]
##

nsec = tend - tstart
time = np.linspace(0,nsec,num=len(sv))
nbins = len(time)

#plt.figure()
fig = plt.figure(figsize=(15,7.5))
#ax = fig.gca()

# Draw court & zoom out slightly to give light buffer
draw_court([xmin,xmax,ymin,ymax])
dx = 5
plt.xlim([xmin-dx,xmax+dx]) 
plt.ylim([ymin-dx,ymax+dx])
plt.title(play_description)
plt.gca().axis('off')

# Animation function / loop
def animate(n):
  # 1. Draw players by team, with jersey numbers
  for i in range(10):
    if i<5:
      col='b'
    else:
      col='r'
    draw_circ(sv.iloc[n].playerx[i], sv.iloc[n].playery[i], col)  
    plt.text(sv.iloc[n].playerx[i], sv.iloc[n].playery[i], sv.iloc[n].playernum[i], color='w', ha='center', va='center')
  # 2. Draw ball
  draw_circ(sv.iloc[n].ballx, sv.iloc[n].bally, [1, 0.4, 0])
  # Also Draw circle within ball to indicate Z position???
  #
  # 3. Print game clock info
  plt.text(0,-5,str(sv.iloc[n].period))
  plt.text(5,-5,str(sv.iloc[n].sec_remain))
  plt.text(20,-5,str(sv.iloc[n].shotclock_remain))
  #  
  # Refresh axis for next frame
  #I = plt.gca().patches
  #I.append(plt.gca().texts)
  plt.show()
  plt.pause(0.01)
  fig.gca().patches = []
  fig.gca().texts = []
  return []

dn = 5 # downsampling, 1 for all frames
sv = sv.iloc[range(0, len(sv), dn)]
for n in range(len(sv)): animate(n)

import matplotlib.animation as animation
#anim = manimation.FuncAnimation(fig, animate, frames=20, blit=False, repeat=False, interval=2)
anim = animation.FuncAnimation(fig, animate, frames=20, blit=True, repeat=False, interval=2)
anim.save('/home/gmf/rebound1.mp4', fps=10, extra_args=['-vcodec', 'libx264'])

#%%

# GSW rebounding
# vs
# BOS rebounding

team_list = ['ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']

reb_list = dict()
for t in team_list:
  print t
  team_games = get_team_games(t)
  
  nreb_team = 0
  nreb_opp = 0
  # HOME GAMES
  for gameid in team_games[0:41]:
    team_reb,opp_reb = get_reb_eventnum(gameid)
    nreb_team += len(team_reb)
    nreb_opp += len(opp_reb)
  
  # AWAY GAMES
  for gameid in team_games[41:82]:
    opp_reb,team_reb = get_reb_eventnum(gameid)
    nreb_team += len(team_reb)
    nreb_opp += len(opp_reb)
    # gsw_reb are i0 or i1??
  reb_pct = np.float(nreb_team)/(nreb_team+nreb_opp)  
  #print t, reb_pct
  #reb_list[t] = reb_pct
  
  reb_totals[t] = nreb_team
  
#%% Bar plot of rebounding success rates
fig = plt.figure()
ax1 = fig.gca()
ax1.set_xticks(np.arange(0.25,30.25))
ax1.set_xticklabels(team_list)
plt.bar(range(30),reb_list.values())
plt.ylim([0.47,0.53])
plt.ylabel('REB success rate')
plt.xlabel('Team')