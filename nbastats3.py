#!/usr/bin/python
# code to turn nba play-by-play data into point process for a particular game event
# e.g. get the sequence of shot attempts (per second) [0 0 0 0 1 0 0 0 0 0 ...]
#
import sys
import re
import numpy
import scipy.io as spio

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
    if re.match(r"[Mm]ade",S2):
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
    if re.search(team,gameID):
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
          opp = re.match('\[[A-Z]{3}',play).group().split("[")[1]
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
    if re.search(team,gameID):
      play = l[-1]
      playTime = playTimeSec(l[2])
      if re.search("[Ff]oul",play):
        isTeam = bool(re.search(team,play))
        if isTeam:
          fouls.append([gameID,playTime])
          print gameID + " " + str(playTime) + " " + team + " Foul" 
        else:
          ofouls.append([gameID,playTime])
	  try:
            opp = re.match('\[[A-Z]{3}',play).group().split("[")[1]
            print gameID + " " + str(playTime) + " " + opp + " Foul"
	  except:
	    print play
            wait = input('PRESS ENTER TO CONTINUE.')
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
    if re.search(team,gameID):
      play = l[-1]
      playTime = playTimeSec(l[2])
      if re.search("[Tt]urnover",play):
        isTeam = bool(re.search(team,play))
        if isTeam:
          tos.append([gameID,playTime])
          print gameID + " " + str(playTime) + " " + team + " Turnover" 
        else:
          otos.append([gameID,playTime])
	  try:
            opp = re.match('\[[A-Z]{3}?',play).group().split("[")[1]
            print gameID + " " + str(playTime) + " " + opp + " Turnover"
	  except:
	    print play
            # for some reason fails for
  	    # plays like: (12:00) [OKC] Team 5 Sec Inbound Turnover :
            wait = input('PRESS ENTER TO CONTINUE.')
  return tos,otos

def ppList(myList):
  games = [myList[0][0]]
  for s in myList:
    if s[0]!=games[-1]:
      games.append(s[0])
  Ngames = len(games)
  secPerGame = 48*60
  Nsec = secPerGame*Ngames
  pp = numpy.zeros([1,Nsec])

  for s in myList:
    game = games.index(s[0])
    t = game*secPerGame+s[1]-1
    pp[0][t] = 1
  return pp


def saveMat(team,season):
  (shotList,oshotList) = getShots(team,season)
  (foulList, ofoulList) = getFouls(team,season)
  (toList,otoList) = getTOs(team,season)
  games = [shotList[0][0]]
  for s in shotList:
    if s[0]!=games[-1]:
      games.append(s[0])
  Ngames = len(games)
  secPerGame = 48*60
  Nsec = secPerGame*Ngames
  shots = numpy.zeros([4,Nsec])
  oshots = numpy.zeros([4,Nsec])
  fouls = ppList(foulList)
  ofouls = ppList(ofoulList)
  tos = ppList(toList)
  otos = ppList(otoList)
  for s in shotList:
    game = games.index(s[0])
    ind = 2*(s[2]==3)
    t = game*secPerGame+s[1]-1
    shots[ind,t] = 1
    if s[3]:      
      shots[ind+1,t] = 1
  for s in oshotList:
    game = games.index(s[0])
    ind = 2*(s[2]==3) 
    t = game*secPerGame+s[1]-1
    oshots[ind,t] = 1
    if s[3]:
      oshots[ind+1,t] = 1
  D = {"shots":shots,"oshots":oshots,"games":games,"Ngames":Ngames,"tos":tos,"otos":otos,"fouls":fouls,"ofouls":ofouls}
  matfile = team + season + ".mat"
  spio.matlab.savemat(matfile,D)

def main():
  team = sys.argv[1]
  season = "201415"
  saveMat(team,season)

if __name__ == "__main__":
  main()
