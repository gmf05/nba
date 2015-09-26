#!/usr/bin/python
import json
import numpy as np
import matplotlib.pyplot as plt
#import matplotlib
#from matplotlib import animation

gameid = '0021400001'
JSONPATH = '/home/gmf/Code/repos/nba/json'
pbp = json.loads(open(JSONPATH + '/pbp_' + gameid + '.json','r').read())['rowSet']

# get other gameid -> SI data is accessible
#game = json.loads(open(JSONPATH + '/si_' + gameid + '.json','r').read())
#pbp = game['pbp']
#box = game['boxscores']

j=11
play = pbp[j]
eventid = str(play[1]).zfill(4)
sv = json.loads(open(JSONPATH + '/sv_' + gameid + '_' + eventid + '.json', 'r').read())
mos = sv['moments']

print 'Time start: ' + str(mos[0][2]) + ' sec'
print play[-3],play[-5]
print 'Time end: ' + str(mos[-1][2]) + ' sec'

T = len(mos)
x = np.zeros([10,T])
y = np.zeros([10,T])
b = np.zeros([2,T])
for t in range(0,T):
  xt = [mos[t][-1][n+1][2] for n in range(0,10)]
  yt = [mos[t][-1][n+1][3] for n in range(0,10)]
  x[:,t] = xt
  y[:,t] = yt
  b[0,t] = mos[t][-1][0][2]
  b[1,t] = mos[t][-1][0][3]

for i in range(0,10):
  plt.plot(x[i,:],y[i,:])


##
pname = 'Anthony Davis'
pid = 203076

from pylab import *
plt.ion()

for j in range(1,len(pbp)):
  play = pbp[j]
  if play[-3]==None and play[-5]==None:
    continue
  eventid = str(play[1]).zfill(4)
  sv = json.loads(open(JSONPATH + '/sv_' + gameid + '_' + eventid + '.json', 'r').read())
  mos = sv['moments']
  print 'Time start: ' + str(mos[0][2]) + ' sec.  Time end: ' + str(mos[-1][2]) + ' sec.'
  print play[-3],play[-5]
  print ''
  T = len(mos)
  x = np.zeros([10,T])
  y = np.zeros([10,T])
  b = np.zeros([2,T])
  for t in range(0,T):
    xt = [mos[t][-1][n][2] for n in range(0,len(mos[t][-1]))]
    yt = [mos[t][-1][n][3] for n in range(0,len(mos[t][-1]))]
    pids = [mos[t][-1][n][1] for n in range(0,len(mos[t][-1]))]
    try:
      idx = pids.index(-1)
      pids.remove(-1)
      xt.remove(xt[idx])
      yt.remove(yt[idx])
      while len(xt)<10: xt.append(0)
      while len(yt)<10: yt.append(0)
    except:
      0
    x[:,t] = xt
    y[:,t] = yt
    b[0,t] = mos[t][-1][0][2]
    b[1,t] = mos[t][-1][0][3]
  try:  
    i = pids.index(pid)
    plt.plot(x[i,:],y[i,:],'r')
    plt.pause(1)
    plt.plot(x[i,:],y[i,:],'b')
  except:
    0
