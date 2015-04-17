#!/usr/bin/python
# code to turn nba play-by-play data into point process for a particular game event
# e.g. get the sequence of shot attempts (per second) [0 0 0 0 1 0 0 0 0 0 ...]
#
import sys
import re
import numpy as np
import scipy.io as spio

# LEAVING HERE FOR FUTURE IMPLEMENTATION:
# each feature will need a specific function(s) in order to (1) specify search string in play-by-play
# and (2) declare how to count / form processes, e.g. shot processes depend on shot type (2 vs 3 pointer) and miss/made status
#
#team_features = "date,team,o:team,points,margin,margin after the first,margin at the half,margin after the third,biggest lead,field goals attempted,field goals made,three pointers attempted,three pointers made,free throws attempted,free throws made,points in the paint,assists,steals,blocks,offensive rebounds,defensive rebounds,turnovers"
#player_features="o:team,assists,blocks,defensive rebounds,field goals attempted,field goals made,fouls,free throws attempted,free throws made,minutes,offensive rebounds,points,rebounds,steals,three pointers attempted,three pointers made,turnovers"

def playTimeSec(clockStr):
  t = clockStr.split(":")
  if t[0][0] is "-":
    playTime = 48*60 + 60*int(t[1]) + int(t[2])
  else:
    playTime = 60*(47-int(t[1]))+60-int(t[2])
  return playTime

def shotStatus(play):
  isShot = bool(re.search("[Ss]hot",play))
  if isShot:
    S1 = play.split(" [Ss]hot")[0]    
    S2 = play.split(": ")[1]
    if re.search("3pt",S1):
      pts = 3
    else:
      pts = 2
    if re.search(r"[Mm]ade",S2):
      isMade = True
    else:
      isMade = False
  else:
    pts = 0
    isMade = False
  return isShot,isMade,pts

def getShots(team,season):
  delim = "\t"
  playfile = "playbyplay_" + season + ".txt"
  f = open(playfile,'r')
  features = f.readline()
  shots = []
  oshots = []
  for l in f.readlines():
    l = l.split(delim)
    gameID = l[0]
    # note we match gameID sections explicitly because global match can be problematic:
    # i.e. ORL is a substring of PORLAC
    if re.match(team,gameID[8:11]) or re.match(team,gameID[11::]):
      play = l[-1]
      (isShot,isMade,pts) = shotStatus(play)
      shotTime = playTimeSec(l[2])
      if isShot:
        isTeam = bool(re.search(team,play))
        if isTeam:
          shots.append([gameID,shotTime,pts,isMade])
          print gameID + " " + str(shotTime) + " sec: " + team + " " + str(pts) + "pt shot: " + str(isMade)
        else:
          oshots.append([gameID,shotTime,pts,isMade])
          # note: we want re.search rather than re.match (which starts at string beginning)
          opp = re.search('\[[A-Z]{3}',play).group().split("[")[1]
          print gameID + " " + str(shotTime) + " sec: " + opp + " " + str(pts) + "pt shot: " + str(isMade)
  return shots,oshots

def getFouls(team,season):
  delim = "\t"
  playfile = "playbyplay_" + season + ".txt"
  f = open(playfile,'r')
  features = f.readline()
  fouls = []
  ofouls = []
  for l in f.readlines():
    l = l.split(delim)
    gameID = l[0]
    # note we match gameID sections explicitly because global match can be problematic:
    # i.e. ORL is a substring of PORLAC
    if re.match(team,gameID[8:11]) or re.match(team,gameID[11::]):
      play = l[-1]
      playTime = playTimeSec(l[2])
      if re.search("[Ff]oul",play):
        isTeam = bool(re.search(team,play))
        if isTeam:
          fouls.append([gameID,playTime])
          print gameID + " " + str(playTime) + " " + team + " Foul" 
        else:
          ofouls.append([gameID,playTime])
          # note: we want re.search rather than re.match (which starts at string beginning)
          opp = re.search('\[[A-Z]{3}',play).group().split("[")[1]
          print gameID + " " + str(playTime) + " " + opp + " Foul"
  return fouls,ofouls

def getTOs(team,season):
  delim = "\t"
  playfile = "playbyplay_" + season + ".txt"
  f = open(playfile,'r')
  features = f.readline()
  tos = []
  otos = []
  for l in f.readlines():
    l = l.split(delim)
    gameID = l[0]
    # note we match gameID sections explicitly because global match can be problematic:
    # i.e. ORL is a substring of PORLAC
    if re.match(team,gameID[8:11]) or re.match(team,gameID[11::]):
      play = l[-1]
      playTime = playTimeSec(l[2])
      if re.search("[Tt]urnover",play):
        isTeam = bool(re.search(team,play))
        if isTeam:
          tos.append([gameID,playTime])
          print gameID + " " + str(playTime) + " " + team + " Turnover" 
        else:
          otos.append([gameID,playTime])
          # note: we want re.search rather than re.match (which starts at string beginning)
          opp = re.search('\[[A-Z]{3}?',play).group().split("[")[1]
          print gameID + " " + str(playTime) + " " + opp + " Turnover"
  return tos,otos

#
# NOTE: Want to modify this to distinguish between offensive & defensive rebounds
#
# maybe search instead for missed shots -> assign each one a rebound?
#
def getRebounds(team,season):
  delim = "\t"
  playfile = "playbyplay_" + season + ".txt"
  f = open(playfile,'r')
  features = f.readline()
#  offreb = []
#  defreb = []
#  ooffreb = []
#  odefreb = []
  reb = []
  oreb = []
  for l in f.readlines():
    l = l.split(delim)
    gameID = l[0]
    # note we match gameID sections explicitly because global match can be problematic:
    # i.e. ORL is a substring of PORLAC
    if re.match(team,gameID[8:11]) or re.match(team,gameID[11::]):
      play = l[-1]
      playTime = playTimeSec(l[2])
      if re.search("[Rr]ebound",play):
        isTeam = bool(re.search(team,play))
        if isTeam:
          reb.append([gameID,playTime])
          print gameID + " " + str(playTime) + " " + team + " Rebound" 
        else:
          oreb.append([gameID,playTime])
          # note: we want re.search rather than re.match (which starts at string beginning)
          opp = re.search('\[[A-Z]{3}?',play).group().split("[")[1]
          print gameID + " " + str(playTime) + " " + opp + " Rebound"
  return reb,oreb

# NOTE: Still needs work
def getPossesion(team,season):
  delim = "\t"
  playfile = "playbyplay_" + season + ".txt"
  f = open(playfile,'r')
  features = f.readline()
  possStart = []
  possStop = []
  opossStart = []
  opossStop = []
  for l in f.readlines():
    l = l.split(delim)
    gameID = l[0]
#    # note we match gameID sections explicitly because global match can be problematic:
#    # i.e. ORL is a substring of PORLAC
#    if re.match(team,gameID[8:11]) or re.match(team,gameID[11::]):
#      play = l[-1]
#      playTime = playTimeSec(l[2])
#  	# depending on play, assign prev history of possession...?
#	# 
#
#
# 
# 
  return poss,oposs

def minGameLength(nsec):
  regSec = 2880
  diffsec = nsec - regSec
  if diffsec<=0:
    gamelength = regSec
  else:
    gamelength = regSec + 300*np.ceil(diffsec/300.0)
  return gamelength

def ppList(myList,games,secPerGame):
  sumSec = np.append(0, np.cumsum(secPerGame))
  Nsec = sumSec[-1]
  pp = np.zeros([1,Nsec])
  for s in myList:
    game = games.index(s[0])
    t = sumSec[game]+s[1]-1
    pp[0][t] = 1
  return pp

def saveMat(team,season):
  (shotList,oshotList) = getShots(team,season)
  (foulList, ofoulList) = getFouls(team,season)
  (toList,otoList) = getTOs(team,season)
  (rebList,orebList) = getRebounds(team,season)
  games = [shotList[0][0]]
  secPerGame = []
  for s in shotList:
    # if this shot starts new game, save name of new game & length of game that just ended
    if s[0]!=games[-1]:
      games.append(s[0]) # save name of new game
      # what is expected length of game given time of the final shot?
      s0 = shotList[shotList.index(s)-1]
      gamesec = minGameLength(s0[1])
      secPerGame.append(gamesec)
  # add length of final game
  s0=shotList[-1] # final shot of final game
  secPerGame.append(minGameLength(s0[1])) # how long was final game?
  secPerGame = np.array(secPerGame)
  Nsec = np.sum(secPerGame)
  sumSec = np.append(0, np.cumsum(secPerGame))
  Ngames = len(games)
  shots = np.zeros([4,Nsec])
  oshots = np.zeros([4,Nsec])
  for s in shotList:
    game = games.index(s[0])
    ind = 2*(s[2]==3)
    t = sumSec[game]+s[1]-1
    shots[ind,t] = 1
    if s[3]:      
      shots[ind+1,t] = 1
  for s in oshotList:
    game = games.index(s[0])
    ind = 2*(s[2]==3) 
    t = sumSec[game]+s[1]-1
    oshots[ind,t] = 1
    if s[3]:
      oshots[ind+1,t] = 1
  fouls = ppList(foulList,games,secPerGame)
  ofouls = ppList(ofoulList,games,secPerGame)
  tos = ppList(toList,games,secPerGame)
  otos = ppList(otoList,games,secPerGame)
  rebs = ppList(rebList,games,secPerGame)
  orebs = ppList(orebList,games,secPerGame)
  # NOW PARSE POSSESSION BASED ON THE OTHER LISTS????
  D = {"shots":shots, "oshots":oshots, "rebs":rebs, "orebs":orebs, "games":games, "Ngames":Ngames, "tos":tos, "otos":otos, "fouls":fouls, "ofouls":ofouls, "secPerGame":secPerGame}
  matfile = "stats2_" + season + "_" + team + ".mat"
  spio.matlab.savemat(matfile,D)

def main():
  team = sys.argv[1]
  season = "201415"
  saveMat(team,season)

if __name__ == "__main__":
  main()
