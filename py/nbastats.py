#!/usr/bin/python
# code to turn nba play-by-play data into point process for a particular game event
# e.g. get the sequence of shot attempts (per second) [0 0 0 0 1 0 0 0 0 0 ...]
#
global VERBOSE
VERBOSE = False

import sys
import re
import numpy as np
import scipy.io as spio

# LEAVING HERE FOR FUTURE IMPLEMENTATION:
#
# Add functions to parse start/end of quarters???
#
# each feature will need a specific function(s) in order to (1) specify search string in play-by-play
# and (2) declare how to count / form processes, e.g. shot processes depend on shot type (2 vs 3 pointer) and miss/made status
#
#team_features = "date,team,o:team,points,margin,margin after the first,margin at the half,margin after the third,biggest lead,field goals attempted,field goals made,three pointers attempted,three pointers made,free throws attempted,free throws made,points in the paint,assists,steals,blocks,offensive rebounds,defensive rebounds,turnovers"
#player_features="o:team,assists,blocks,defensive rebounds,field goals attempted,field goals made,fouls,free throws attempted,free throws made,minutes,offensive rebounds,points,rebounds,steals,three pointers attempted,three pointers made,turnovers"

def minGameLength(nsec): # what is the minimum game length at this point?
  if nsec < 2880: # if game time < 2880 no overtime yet
    gamelength = 2880
  else: # game has overtime!
    gamelength = 2880 + 300*np.ceil((nsec - 2880)/300.0) # add 300 sec per overtime
  return gamelength

def numSecElapsed(qtr,minRemain,secRemain): # translate time remaining into time elapsed
  if type(qtr) is str:
    qtr = int(qtr)
  if type(minRemain) is str:
    minRemain = int(minRemain)
  if type(secRemain) is str:
    secRemain = float(secRemain)
  if qtr>4: # in overtime, add 300 sec per overtime
    secElapsed = 2880 + (qtr-5)*300 + (4-minRemain)*60 + 60 - secRemain
  else: # in regulation, add 720 sec per quarter
    secElapsed = (qtr-1)*720 + (11-minRemain)*60 + 60 - secRemain
  return secElapsed

def getEvents(team,season,eventName):
  # works for finding simple events distinguished by one word in the play-by-play text
  # e.g. if the regexp match for assist is "[Aa]ssist"
  # this should NOT be used for parsing shots; use getShots instead
  delim = "\t"
  #delim = ","
  searchString = "[" + str.upper(eventName[0]) + str.lower(eventName[0]) + "]" + eventName[1::] # e.g. Assist -> [Aa]ssist
  playfile = "playbyplay_" + season + ".txt"
  f = open(playfile,'r')
  features = f.readline()
  events = []
  oevents = []
  # cycle over plays, search for searchString, and decide if events occurs for team or for opponent 
  for l in f.readlines():
    l = l.split(delim)
    gameID = l[1]
    # note we match gameID sections explicitly because global match can be problematic:
    # i.e. ORL is a substring of PORLAC
    if re.match(team,gameID[8:11]) or re.match(team,gameID[11::]):
      play = l[-1]
      if re.search(searchString,play):
        playTime = numSecElapsed(l[2], l[3], l[4]) # qtr, minRemain, secRemain
        isTeam = bool(re.search(team,play))
        if isTeam:
          events.append([gameID,playTime])
          eventTeam = team
        else:
          oevents.append([gameID,playTime])
          # note: we want re.search rather than re.match (which starts at string beginning)
          opp = re.search('\[[A-Z]{3}',play).group().split("[")[1]
          eventTeam = opp
        if VERBOSE:
          print gameID + " " + str(playTime) + " " + eventTeam + " " + eventName          
  return events,oevents

def shotStatus(play):
  # 
  #
  # see if "shot" appears in play (and *not* "shot clock turnover"!):
  isShot = bool(re.search("[Ss]hot(?! [Cc]lock [Tt]urnover)",play))
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
  
def ftStatus(play):
    isFT = bool(re.search("[Ff]ree [Tt]hrow",play))
    ftNum = 0
    isMade = False
    isTech = bool(re.search("[Tt]echnical", play))
    isClearPath = bool(re.search("[Cc]lear [Pp]ath", play))
    if isFT:      
        checkDigits = re.search("(\d) of (\d)",play)
        if checkDigits:       
            ftNum = map(int,checkDigits.groups())
        else:
            ftNum = [1, 1]
            if VERBOSE:            
              print "Technical?" # debug
        S1 = play.split(" [Ff]ree [Tt]hrow")[0]    
        if re.search("[Mm]issed",S1):
            isMade = False
        else:
            isMade = True
    return isFT,ftNum,isMade,isTech,isClearPath

def getShots(team,season):
  delim = "\t"
  #delim = ","
  playfile = "playbyplay_" + season + ".txt"
  f = open(playfile,'r')
  features = f.readline()
  shots = []
  oshots = []
  for l in f.readlines():
    l = l.split(delim)
    gameID = l[1]
    # note we match gameID sections explicitly because global match can be problematic:
    # i.e. ORL is a substring of PORLAC
    if re.match(team,gameID[8:11]) or re.match(team,gameID[11::]):
      play = l[-1]
      (isShot,isMade,pts) = shotStatus(play)
      if isShot:
        shotTime = numSecElapsed(l[2], l[3], l[4]) # qtr, minRemain, secRemain
        isTeam = bool(re.search(team,play))
        if isTeam:
          shots.append([gameID,shotTime,pts,isMade])
          eventTeam = team
        else:
          oshots.append([gameID,shotTime,pts,isMade])
          # note: we want re.search rather than re.match (which starts at string beginning)
          opp = re.search('\[[A-Z]{3}',play).group().split("[")[1]
          eventTeam = opp
        if VERBOSE:
          print gameID + " " + str(shotTime) + " sec: " + eventTeam + " " + str(pts) + "pt shot: " + str(isMade)
  return shots,oshots
  
def getFTs(team,season):
  delim = "\t"
  #delim = ","
  playfile = "playbyplay_" + season + ".txt"
  f = open(playfile,'r')
  features = f.readline()
  fts = []
  ofts = []
  for l in f.readlines():
    l = l.split(delim)
    gameID = l[1]
    # note we match gameID sections explicitly because global match can be problematic:
    # i.e. ORL is a substring of PORLAC
    if re.match(team,gameID[8:11]) or re.match(team,gameID[11::]):
      play = l[-1]
      (isFT,ftNum,isMade,isTech,isClearPath) = ftStatus(play)
      if isFT:
        ftTime = numSecElapsed(l[2], l[3], l[4]) # qtr, minRemain, secRemain
        isTeam = bool(re.search(team,play))
        if isTeam:
          fts.append([gameID,ftTime,ftNum,isMade])
          eventTeam = team
        else:
          ofts.append([gameID,ftTime,ftNum,isMade])
          # note: we want re.search rather than re.match (which starts at string beginning)
          opp = re.search('\[[A-Z]{3}',play).group().split("[")[1]
          eventTeam = opp
        if VERBOSE:
          print gameID + " " + str(ftTime) + " sec: " + eventTeam + " Free throw " + str(ftNum[0]) + " of " + str(ftNum[1]) + " : " + str(isMade)
  return fts,ofts

def getFinalFTs(team,season):
  delim = "\t"
  #delim = ","
  playfile = "playbyplay_" + season + ".txt"
  f = open(playfile,'r')
  features = f.readline()
  fts = []
  ofts = []
  for l in f.readlines():
    l = l.split(delim)
    gameID = l[1]
    # note we match gameID sections explicitly because global match can be problematic:
    # i.e. ORL is a substring of PORLAC
    if re.match(team,gameID[8:11]) or re.match(team,gameID[11::]):
      play = l[-1]
      (isFT,ftNum,isMade,isTech,isClearPath) = ftStatus(play)
      if isFT and not isTech and not isClearPath and ftNum[0]==ftNum[1]:
        ftTime = numSecElapsed(l[2], l[3], l[4]) # qtr, minRemain, secRemain
        isTeam = bool(re.search(team,play))
        if isTeam:
          fts.append([gameID,ftTime,ftNum,isMade])
          eventTeam = team
        else:
          ofts.append([gameID,ftTime,ftNum,isMade]) 
          # note: we want re.search rather than re.match (which starts at string beginning)
          opp = re.search('\[[A-Z]{3}',play).group().split("[")[1]
          eventTeam = opp
        if VERBOSE:
          print gameID + " " + str(ftTime) + " sec: " + eventTeam + " Free throw " + str(ftNum[0]) + " of " + str(ftNum[1]) + " : " + str(isMade)
  return fts,ofts

def ppList(myList,games,secPerGame):
  sumSec = np.append(0, np.cumsum(secPerGame))
  Nsec = sumSec[-1]
  pp = np.zeros([1,Nsec])
  for s in myList:
    game = games.index(s[0])
    t = sumSec[game]+s[1]-1
    pp[0][t] = 1
  return pp

def ppShots(shotList,games,secPerGame):
  sumSec = np.append(0, np.cumsum(secPerGame))
  Nsec = sumSec[-1]
  shots = np.zeros([4,Nsec])
  for s in shotList:
    game = games.index(s[0])
    ind = 2*(s[2]==3)
    t = sumSec[game]+s[1]-1
    shots[ind,t] = 1
    if s[3]:
      shots[ind+1,t] = 1
  return shots

def ppFTs(ftList,games,secPerGame):
  sumSec = np.append(0, np.cumsum(secPerGame))
  Nsec = sumSec[-1]
  fts = np.zeros([2,Nsec])
  for s in ftList:
    game = games.index(s[0])
    t = sumSec[game]+s[1]-1
    #fts[0][t] = s[2][1] # how many fts taken in this trip?
    fts[0][t] += 1 # how many fts taken in this trip?
    fts[1][t] += s[3] # count number fts made
  return fts
  
def getGames(team,season):
  gamelist = "gamelist_" + season + ".txt" # list of games
  delim = "\t"  
  #delim = ","
  f = open(gamelist,"r") 
  games = []
  for l in f.readlines():
    l = l.replace('\n','').split(delim)
    if l[1]==team or l[2]==team:
      games.append("".join(l))
  return games

def saveMat(team,season):
  # parse play-by-play for lists of event times
  (shotList,oshotList) = getShots(team,season)
  (foulList,ofoulList) = getEvents(team,season,"Foul")
  (toList,otoList) = getEvents(team,season,"Turnover")
  (ostealList,stealList) = getEvents(team,season,"Steal") # NOTE: opponent/team order is reversed for steals
  (rebList,orebList) = getEvents(team,season,"Rebound")
  (asstList,oasstList) = getEvents(team,season,"Assist")
  (ftList,oftList) = getFTs(team,season)
  # need to know how long each game is to make point process data
  games = getGames(team, season)
  secPerGame = []
  g = games[0]
  for s in shotList:
    # if this shot starts new game, save name of new game & length of game that just ended
    if not g==s[0]:
      g = s[0]
      gamesec = minGameLength(shotList[shotList.index(s)-1][1])
      secPerGame.append(gamesec)
  secPerGame.append(minGameLength(shotList[-1][1])) # add length of final game
  secPerGame = np.array(secPerGame)
  # process event lists into point process data:
  shots = ppShots(shotList,games,secPerGame)
  oshots = ppShots(oshotList,games,secPerGame)
  fouls = ppList(foulList,games,secPerGame)
  ofouls = ppList(ofoulList,games,secPerGame)
  tos = ppList(toList,games,secPerGame)
  otos = ppList(otoList,games,secPerGame)
  rebs = ppList(rebList,games,secPerGame)
  orebs = ppList(orebList,games,secPerGame)
  assts = ppList(asstList,games,secPerGame)
  oassts = ppList(oasstList,games,secPerGame)
  fts = ppFTs(ftList,games,secPerGame)
  ofts = ppFTs(oftList,games,secPerGame)
  (finalftList,finaloftList) = getFinalFTs(team,season)
  finalfts = ppFTs(finalftList,games,secPerGame)
  finalofts = ppFTs(finaloftList,games,secPerGame)
  D = {"shots":shots, "oshots":oshots, "rebs":rebs, "orebs":orebs, "assts":assts, "oassts":oassts, "games":games, "tos":tos, "otos":otos, "fouls":fouls, "ofouls":ofouls, "fts":fts, "ofts":ofts, "finalfts":finalfts, "finalofts":finalofts, "secPerGame":secPerGame}
  matfile = "stats_" + season + "_" + team + ".mat"
  spio.matlab.savemat(matfile,D)

def main():
  team = sys.argv[1]
  season = "201415"
  saveMat(team,season)

if __name__ == "__main__":
  main()
