#!/usr/bin/python
import re
import urllib2
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np

db_path = 'sql'
conn = sqlite3.connect(db_path + '/nba3.db')

##########################################
# add dropdown menu of players?
players = conn.cursor().execute("select distinct player from Shots where season=2014;").fetchall()

##########################################
# scatter plot of missed and made shots
#

# draw court
img = mpimg.imread('temp/nba_court.png')
#img[:,:,-1]=0.7 # change alpha level
implot = plt.imshow(img,extent=[-250, 250, -60, 840], zorder=0)

# search by player
#p = 'klay_thompson'
#shots = conn.cursor().execute('select x,y,made from Shots where season=2014 and player="' + p + '";').fetchall()

# search by team
t = 'ATL'
shots = conn.cursor().execute('select x,y,made from Shots where season=2014 and team="' + t + '";').fetchall()

for s in shots:
  if s[2]: # made shot
    plt.plot(s[0],s[1],'bo',zorder=1)
  else: # missed shot
    plt.plot(s[0],s[1],'rx',zorder=1)
plt.show()

##########################################
# heat map of FG%
#

# draw court
img = mpimg.imread('temp/nba_court.png')

implot = plt.imshow(img,extent=[-250, 250, -60, 840], zorder=0)

# search by player
#p = 'klay_thompson'
#shots = conn.cursor().execute('select x,y,made from Shots where season=2014 and player="' + p + '";').fetchall()

# search by team
t = 'ATL'
shots = conn.cursor().execute('select x,y,made from Shots where season=2014 and team="' + t + '";').fetchall()

# bin by space
# fill rectangles
# change alpha level? #img[:,:,-1]=0.7 # change alpha level

def colormap(N):
  C = np.zeros([N,3])
  for n in range(0,N/2):
    C[n,:] = [0,n,N/2-n]
  for n in range(N/2,N):
    C[n,:] = [n-N/2,N-n,0]
  return C*2/N

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
  
dx = 20
dy = 20
xbins = range(-250, 251, dx)
ybins = range(-50, 851, dy)
xcent = range(-250+dx/2, 251, dx)
ycent = range(-50+dy/2, 851, dy)
Rx = np.array([-1, -1, 1, 1])*dx/2
Ry = np.array([-1, 1, 1, -1])*dy/2

FGA = 0*np.meshgrid(np.array(xbins),np.array(ybins))[0]
FGM = 0*np.meshgrid(np.array(xbins),np.array(ybins))[0]
C = np.meshgrid(np.array(xcent),np.array(ycent))[0]
N = 64
colors = jet(N)
#colors = colormap(N)

for s in shots:
  x,y = s[0:2]
  j = (x - xbins[0])/dx
  i = (y - ybins[0])/dy
  FGA[i,j]+=1
  if s[2]: FGM[i,j]+=1

FGP = float(0)*FGM
for i in range(0,np.size(C,0)):
  for j in range(0,np.size(C,1)):
    if FGA[i,j]>0:
      FGP[i,j] = float(FGM[i,j])/FGA[i,j]
    else:
      FGP[i,j] = 0
    fgi = np.round(FGP[i,j]*(N-1))
    plt.fill(xcent[j]+Rx,ycent[i]+Ry,color=colors[fgi,:], zorder=1, alpha=0.7)
plt.show()