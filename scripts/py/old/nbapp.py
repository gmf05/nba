#!/usr/bin/python
# nbapp.py
# Convert nba play-by-play into point process data
#
import re
import numpy as np
import scipy.io as spio

delim = ','

# function to compute number of seconds elapsed in a game given
#  quarter number (ot = 5, 2ot = 6, etc.) and clock time
def secElapsed(prd, clockmin, clocksec):
  if prd<=4: # if in regulation
    return (prd-1)*720 + (12 - clockmin)*60 + (0 - clocksec)
  else: # else in overtime
    return 2880 + (prd-5)*300 + (5 - clockmin)*60 + (0 - clocksec)

#################################
# one approach based on NBA play-by-play
fr = open('csv/plays_nba_all.csv','r')
#fw = open('csv/pp_test.csv','w')
fr.readline() # drop headers

# initialize numpy array
# start time counter, game pointer

pp = np.zeros([4,2880])  # 3pa,3pm,2pa,2pm

r = fr.readline()

for r in fr.readline():
  gameid,season,a,prd,a,a,team,vtms,htms,clock,a,play = r.strip().split(delim)
  date = gameid[0:8]
  away = gameid[8:11]
  home = gameid[11:14]
  if gameid=='20141029ATLTOR' and team=='ATL':    
    clockmin,clocksec = [int(t) for t in clock.split(':')]
    numsec = secElapsed(int(prd), clockmin, clocksec)  
    # parse play to find shot point value, is made or not?
    mat = re.search('(.+) [Ss]hot: (.+)', play.split('(')[0])
    if mat: # if play is a shot, parse further
      is3pt = bool(re.search('3pt', mat.groups()[0]))
      isMade = bool(re.search('[Mm]ade', mat.groups()[1]))
      # add shot attempt and make, if made
      row = 2*is3pt
      pp[row,numsec] +=1 # add attempt
      if isMade: pp[row+1,numsec] += 1 # add make if made
      # debug:    
      #if made=='1':
      #  print 'Made ' + dist + 'ft ' + pts + ' pt shot ' + clock + ' in ' + prd
      #else:
      #  print 'Miss ' + dist + 'ft ' + pts + ' pt shot ' + clock + ' in ' + prd
      #print str(row), made, row+int(made=='1'), str(sum(pp.T))
      #

spio.matlab.savemat('matlab/test.mat',{'pp':pp})

  
#################################
# another approach
# based on NBA.com shot charts

############################################################
myTeam = 'BKN'
# for each game, get number of periods
fr = open('csv/shots_00214.csv','r')
fr.readline()
fw = open("csv/gamelengths_00214.csv","w")
fw.write(delim.join(['gameid', 'away', 'home', 'nprds']) + '\n')
gameid = fr.readline().strip().split(delim)[0]
gameidlast = gameid
prdlast = str(1)
# cycle to end of most recent game, get period, go to next line & start new game
for r in fr.readlines():
  gameid,a,a,a,prd,a,a,a,a,a,a,a = r.strip().split(delim)
  if gameid!=gameidlast:
    fw.write(delim.join([gameidlast, gameidlast[8:11], gameidlast[11:15], prdlast]) + '\n')
  prdlast = prd
  gameidlast = gameid
fw.close()
fr0 = open('csv/gamelengths_00214.csv','r')
fr0.readline()
# get number of seconds on the season for myTeam
teamgames = []
nsecs = [0]
for r in fr0.readlines():
  gameid,away,home,nprd = r.strip().split(delim)
  if away==myTeam or home==myTeam:
    teamgames.append(gameid)
    nprd = int(nprd)
    nsecs.append(2880 + (nprd-4)*300)
nsecs = np.cumsum(np.array(nsecs))
totsecs = nsecs[-1]

#pp = np.zeros([4,totsecs])  # 3pa,3pm,2pa,2pm
pp = np.zeros([7,totsecs])  # 3pa,3pm,2pa,2pm,x,y,dist

fr = open('csv/shots_00214.csv','r')
fr.readline()

r = fr.readline()
for r in fr.readlines():
  gameid,a,player_code,team,prd,min_remain,sec_remain,pts,dist,x,y,made = r.strip().split(delim)
  #if (gameid[8:11]==myTeam or gameid[11:15]==myTeam) and team!=myTeam: # get opponent shots
  if team==myTeam: # get team shots
    gamenum=teamgames.index(gameid)
    numsec = secElapsed(int(prd), int(min_remain), int(sec_remain)) + nsecs[gamenum]
    # add shot attempt and make, if made
    # row 0 = 2pa, row 1 = 2pm
    # row 2 = 3pa, row 3 = 3pm
    row = 2*int(pts=='3')
    pp[row,numsec] +=1 # add attempt
    if made=='1': pp[row+1,numsec] += 1 # add make if made
    # debug:    
    #if made=='1':
    #  print 'Made ' + dist + 'ft ' + pts + ' pt shot ' + clock + ' in ' + prd
    #else:
    #  print 'Miss ' + dist + 'ft ' + pts + ' pt shot ' + clock + ' in ' + prd
    #print str(row), made, row+int(made=='1'), str(sum(pp.T))
    #
    pp[4,numsec] = int(x)
    pp[5,numsec] = int(y)
    pp[6,numsec] = int(dist)

#spio.matlab.savemat('matlab/' + myTeam + 'oshots2014.mat',{'pp':pp, 'nsecs':nsecs})
spio.matlab.savemat('matlab/klay37pts.mat',{'pp':pp, 'nsecs':nsecs})
############################################################


###### DEBUG ######

