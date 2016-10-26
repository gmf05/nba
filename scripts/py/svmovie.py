# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 12:37:22 2016

@author: gmf
"""

#%%

import numpy as np
#import scipy.io as spio
import bb_tools as bb
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Play movie of SportVu data

gameid = '0021400001'
pbp = bb.get_pbp(gameid)
boxscore = bb.get_boxscore(gameid)
shots = bb.get_shots(gameid)

def init():
  # Draw court & zoom out slightly to give light buffer
  bb.draw_court([xmin,xmax,ymin,ymax]) 
  for i in range(3): info_text[i].set_text('')
  for i in range(10): 
    player_text[i].set_text('')
    ax.add_patch(player_circ[i])
  ax.add_patch(ball_circ)
  ax.axis('off')
  dx = 5
  plt.xlim([xmin-dx,xmax+dx]) 
  plt.ylim([ymin-dx,ymax+dx])  
  plt.title(play_description)
  return tuple(info_text) + tuple(player_text) + tuple(player_circ) + (ball_circ,)

# Animation function / loop
def animate(n):
  # 1. Draw players by team, with jersey numbers
  for i in range(10):
    if i<5:
      col='b'
    else:
      col='r'
    player_circ[i].center = (sv.iloc[n].playerx[i], sv.iloc[n].playery[i])
    player_text[i].set_text(str(sv.iloc[n].playernumber[i]))
    player_text[i].set_x(sv.iloc[n].playerx[i])
    player_text[i].set_y(sv.iloc[n].playery[i])
  # 2. Draw ball
  ball_circ.center = (sv.iloc[n].ballx, sv.iloc[n].bally)
  # Fluctuate ball radius to indicate Z position : helpful for shots
  ball_circ.radius = 1 + sv.iloc[n].ballz/17*2
  #
  # 3. Print game clock info
  info_text[0].set_text(str(sv.iloc[n].period))
  info_text[1].set_text(str(sv.iloc[n].period_remain))
  info_text[2].set_text(str(sv.iloc[n].shotclock_remain))
  #
  plt.show()
  #plt.pause(0.01) # Uncomment to watch movie as it's being made
  return tuple(info_text) + tuple(player_text) + tuple(player_circ) + (ball_circ,)

# Plotting players & ball as 2D movie!

# Event number
eventnum = '0003'
filename = 'sportvu_movie'

# Get SportVu data & downsample
sv = bb.get_sportvu_locations(gameid, eventnum)
dn = 2 # downsampling, set to 1 for all frames
sv = sv.iloc[range(0, len(sv), dn)].reset_index()

plt.close('all')
fig = plt.figure(figsize=(15,7.5))
ax = plt.gca()

# Court dimensions
xmin = 0
xmax = 100
ymin = 0
ymax = 50

# Play-by-Play data for given event num
# TO DO: DON'T GET INDEX I -- GET CLOSEST TO CURRENT TIME!!
playi = pbp.iloc[np.flatnonzero(pbp.EVENTNUM==int(eventnum))]
#treb = playi.PCTIMESTRING.values[0]
if playi.HOMEDESCRIPTION.values[0]:
  play_description = str(playi.HOMEDESCRIPTION.values[0])
else:
  play_description = str(playi.VISITORDESCRIPTION.values[0])

# Animated elements
info_text = range(3)
info_text[0] = ax.text(0, -5, '')
info_text[1] = ax.text(5, -5, '')
info_text[2] = ax.text(20, -5, '')
player_text = range(10)
player_circ = range(10)
R=2.2
for i in range(10): 
  player_text[i] = ax.text(0,0,'',color='w',ha='center',va='center')
  if i<5:
    col='b'
  else:
    col='r'
  player_circ[i] = plt.Circle((0,0), R, color=col)
ball_circ = plt.Circle((0,0), R, color=[1, 0.4, 0])

# #%% Play animation!

ani = animation.FuncAnimation(fig, animate, frames=len(sv), init_func=init, blit=True, interval=5, repeat=False)
ani.save(filename + '.mp4', fps=10, extra_args=['-vcodec', 'libx264'])
