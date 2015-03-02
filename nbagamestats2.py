#!/usr/bin/python
# code to make a list of nba games between 2 dates
import datetime
import re
import urllib2
#import sys
import csv
#import json
import scipy.io as spio
import numpy 

#team_features = "date,team,o:team,points,margin,margin after the first,margin at the half,margin after the third,biggest lead,field goals attempted,field goals made,three pointers attempted,three pointers made,free throws attempted,free throws made,points in the paint,assists,steals,blocks,offensive rebounds,defensive rebounds,turnovers"
#player_features="o:team,assists,blocks,defensive rebounds,field goals attempted,field goals made,fouls,free throws attempted,free throws made,minutes,offensive rebounds,points,rebounds,steals,three pointers attempted,three pointers made,turnovers"

def getSeason(season):
  gamelist = file("gamelist_" + season + ".txt", "r")
  # get number of games
  # provide list of stats, list of rules / keys looked for in play-by-play...
  # initialize lists for storing stats
  playlist = file("playbyplay_" + season + ".txt", 'r')
  gameInd = 1
  for play in playlist.readlines():
    # get "gameID" from gm -> update gameInd if necessary
    # in general, two counters will be updated on each play
    # e.g. foul goes to one team's 'fouls' process, another team's 'ofouls' process
    # if so, add to count(s): stats[gameInd0, statInd] += 1, 2, etc
  
def saveMat(season):
  games =  numpy.asarray(getSeason(yyyy),dtype=numpy.object)
  D = {"games":games, "features":features}
  spio.matlab.savemat('NBASeason' + str(yyyy) + '.mat', D)

def main():
  season='201415'
  saveMat(season)

if __name__ == "__main__":
    main()
