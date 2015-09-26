#!/usr/bin/python
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
#import matplotlib
#from matplotlib import animation
#from pylab import *
#plt.ion()

gameid = '0021400001'
gameid = '0021400008'
gameid = '0041400104' # PLAYOFFS GAME 1
JSONPATH = '/home/gmf/Code/repos/nba/json'
json_file = JSONPATH + '/pbp_' + gameid + '.json'
pbp = json.loads(open(json_file,'r').read())['rowSet']
json_file = JSONPATH + '/bs_' + gameid + '.json'
bs = json.loads(open(json_file,'r').read())

# get other gameid -> SI data is accessible
#json_file = JSONPATH + '/si_' + gameid + '.json'
#game = json.loads(open(json_file,'r').read())
#pbp = game['pbp']
#box = game['boxscores']

# intialize arrays
NT = 3180*25
x = np.zeros([10,NT])
y = np.zeros([10,NT])
b = np.zeros([2,NT])
p = np.zeros([10,NT])
count=0
lastprd=1
lastclock=721

# piece game together, looping over plays (in PBP) and moments (in SportVu)
for j in range(1,len(pbp)):
  play = pbp[j]
  if play[-3]==None and play[-5]==None:
    continue
  play = pbp[j]
  eventid = str(play[1]).zfill(4)
  sv = json.loads(open(JSONPATH + '/sv_' + gameid + '_' + eventid + '.json', 'r').read())
  mos = sv['moments']  
  T = len(mos)
  #print 'Time start: ' + str(mos[0][2]) + ' sec. Time end: ' + str(mos[-1][2]) + ' sec'
  #print play[-3],play[-5],'\n'
  
  for t in range(0,T):
    # if we're not at most recent time, continue
    if lastprd>mos[t][0] or (lastprd==mos[t][0] and lastclock<mos[t][2]):
      continue
    yt = [mos[t][-1][n][2] for n in range(0,len(mos[t][-1]))]
    xt = [mos[t][-1][n][3] for n in range(0,len(mos[t][-1]))]
    pids = [mos[t][-1][n][1] for n in range(0,len(mos[t][-1]))]
    try:
      idx = pids.index(-1)
      pids.remove(-1)
      yt.remove(yt[idx])
      xt.remove(xt[idx])
      while len(yt)<10: yt.append(0)
      while len(xt)<10: xt.append(0)
      while len(pids)<10: pids.append(None)
    except:
      0
    y[:,count] = yt
    x[:,count] = xt
    b[0,count] = mos[t][-1][0][2]
    b[1,count] = mos[t][-1][0][3]
    p[:,count] = pids
    count+=1
    lastprd = mos[t][0]
    lastclock = mos[t][2]

# trim extra zeros
y = np.delete(y,range(count,NT),axis=1)
x = np.delete(x,range(count,NT),axis=1)
b = np.delete(b,range(count,NT),axis=1)
p = np.delete(p,range(count,NT),axis=1)
NT = np.size(x,1)

# get movements for a specific player
pname = 'Anthony Davis'
pid = 203076
ys = []
xs = []
for t in range(0,NT):
  try:
    i = find(p[:,t]==pid)[0]
    ys.append(y[i,t])
    xs.append(x[i,t])
  except:
    0
plt.plot(xs,ys)


# bin player position for game by location

def jet(N):
  C = np.zeros([N,3])
  M = np.floor(N/4)
  dN = 1/M
  C[0,2] = (M/2+1)/M
  i=1
  for j in range(1,int(M/2)):
    C[i,:] = C[i-1,:]
    C[i,2] += dN
    i+=1
  for j in range(0, int(M)):
    C[i,:] = C[i-1,:]
    C[i,1] += dN
    i+=1
  for j in range(0, int(M)):
    C[i,:] = C[i-1,:]
    C[i,0] += dN
    C[i,2] -= dN
    i+=1
  for j in range(0, int(M)):
    C[i,:] = C[i-1,:]
    C[i,1] -= dN
    i+=1
  for j in range(0,int(M/2)):
    C[i,:] = C[i-1,:]
    C[i,0] -= dN
    i+=1
  return C
  
# bin space
x0 = 10*np.array(xs)-250
y0 = 9*np.array(ys)
dx = 50
dy = 50
minx = -250
maxx = 250
miny = -50
maxy = 850

img = mpimg.imread('temp/nba_court.png')
implot = plt.imshow(img,extent=[minx, maxx, miny, maxy], zorder=0)

xbins = range(minx, maxx+1, dx)
ybins = range(miny, maxy+1, dy)
xcent = range(minx+dx/2, maxx+1, dx)
ycent = range(miny+dy/2, maxy+1, dy)
Rx = np.array([-1, -1, 1, 1])*dx/2
Ry = np.array([-1, 1, 1, -1])*dy/2

pos = 0*np.meshgrid(np.array(xbins),np.array(ybins))[0]
C = np.meshgrid(np.array(xcent),np.array(ycent))[0]
N = 64
colors = jet(N)
#colors = colormap(N)

for t in range(0,len(xs)):
  xt,yt = x0[t],y0[t]
  j = (xt - xbins[0])/dx
  i = (yt - ybins[0])/dy
  pos[i,j]+=1

pos0 = np.round(pos/float(np.max(pos)) * (N-1))
for i in range(0,np.size(C,0)):
  for j in range(0,np.size(C,1)):
    fgi = pos0[i,j]
    plt.fill(xcent[j]+Rx,ycent[i]+Ry,color=colors[fgi,:], zorder=1, alpha=0.7)
plt.show()