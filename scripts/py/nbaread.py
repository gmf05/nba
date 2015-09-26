#!/usr/bin/python
# code to turn a list of nba games into play-by-play data
import sys
import re
import urllib2

def parseGameInfo(date, teams):
  urlroot = "http://www.nba.com/games/"
  date = date.replace("-","")
  teamID = "".join(teams)
  gameID = date + teamID
  url = urlroot + date + "/" + teamID + "/gameinfo.html"
  f = urllib2.urlopen(url)
  html = f.read()
  f.close()
  # parse away & home teams
  # parse game location
  # parse number of quarters / OTs [prd]
  # parse quarter by quarter scores
  


def parseBoxScore(date,teams): # parse play-by-play from a single game
  urlroot = "http://www.nba.com/games/"
  date = date.replace("-","")
  teamID = "".join(teams)
  gameID = date + teamID
  url = urlroot + date + "/" + teamID + "/gameinfo.html"
  f = urllib2.urlopen(url)
  html = f.read()
  f.close()
  #boxscore={}
  #go to <table id="nbaGITeamStats"...>
  # get visiting team [first from e.g <thead class="nbaGICHA_Hornets">]
  # get stat names from <td class="nbaGITeamHdrStats">
  # ...make dictionary
#            if q>=4:
#            mRemain = 5
#          else:
#            mRemain = 12
#          sRemain = 0.0
#        else:
#          l = re.search('<td class="nbaGIPbPLft">(.+)&nbsp;</td>', h)
#          m = re.search('<td class="nbaGIPbPMid">(.+)</td>', h)
#          r = re.search('<td class="nbaGIPbPRgt">(.+)&nbsp;</td>', h)
#          if not m:
#            l = re.search('<td class="nbaGIPbPLftScore">(.+)&nbsp;</td>', h)
#            m = re.search('<td class="nbaGIPbPMidScore">(.+)<br>', h)
#            r = re.search('<td class="nbaGIPbPRgtScore">(.+)&nbsp;</td>', h)
#            if not m:
#              # if we get here, quarter is over
#              play = "End of Q" + str(q+1)
#              mRemain = 0
#              sRemain = 0.0          
      #playList.append([str(count), gameID, str(q+1), str(mRemain), str(sRemain), play])
      #count += 1
  boxscore = []
  # get list of stats (keys)
  # for each team
  # get list of players 
  # for each player, get stats
  # for total, get stats
  #boxscore.append([str(count), gameID, str(q+1), str(mRemain), str(sRemain), play])
  return boxscore

def parsePlayList(date,teams): # parse play-by-play from a single game
  urlroot = "http://www.nba.com/games/"
  date = date.replace("-","")
  teamID = "".join(teams)
  gameID = date + teamID
  url = urlroot + date + "/" + teamID + "/gameinfo.html"
  f = urllib2.urlopen(url)
  html = f.read()
  f.close()
  # split by TblHdr for quarter-by-quarter breaks
  H = html.split('class="nbaGIPbPTblHdr"')
  # beginning with H[1]
  playList = []
  count = 1
  NQ = (len(H) -1)/2
  for q in range(NQ):  
    for h in H[2*q+1].split('<tr'):
      jumpball = re.search('<div class="gameEvent">(.+)</div>', h)
      if jumpball:
        if q>=4: # WHICH QUARTER IS IT??
          mRemain = 5 # overtime
        else:          
          mRemain = 12 # regulation
        sRemain = 0.0
        play = jumpball.groups()[0]
      else: # otherwise parse Lft Mid Rgt      
        qStart = re.search('<a name=".+">(.*)\n', h)
        if qStart:
          play = "Start of Q" + str(q+1)
          if q>=4:
            mRemain = 5
          else:
            mRemain = 12
          sRemain = 0.0
        else:
          l = re.search('<td class="nbaGIPbPLft">(.+)&nbsp;</td>', h)
          m = re.search('<td class="nbaGIPbPMid">(.+)</td>', h)
          r = re.search('<td class="nbaGIPbPRgt">(.+)&nbsp;</td>', h)
          if not m:
            l = re.search('<td class="nbaGIPbPLftScore">(.+)&nbsp;</td>', h)
            m = re.search('<td class="nbaGIPbPMidScore">(.+)<br>', h)
            r = re.search('<td class="nbaGIPbPRgtScore">(.+)&nbsp;</td>', h)
            if not m:
              # if we get here, quarter is over
              play = "End of Q" + str(q+1)
              mRemain = 0
              sRemain = 0.0
          if l:
            play = "[" + teams[0] + "]" + l.groups()[0]
          if r:
            play = "[" + teams[1] + "]" + r.groups()[0]
          if m:
            tRemain = m.groups()[0]
            mRemain = int(re.search('(\d+):\d+',tRemain).groups()[0])
            sRemain = float(re.search('\d+:(\d.+)\s',tRemain).groups()[0])
      playList.append([str(count), gameID, str(q+1), str(mRemain), str(sRemain), play])
      count += 1
  return playList

def removeExtraRebs(playList): # remove, e.g., "Free Throw 1 of 2 Missed" -> "Team Rebound"
  prevplay = ''
  for p in playList: # for each game, parse play-by-play
    play = p[-1]
    isReb = re.search("\[[A-Z]+\] [Tt]eam [Rr]ebound", play)
    ftMiss = re.search("[Ff]ree [Tt]hrow (\d) of (\d) Missed", prevplay)
    if isReb and ftMiss and ftMiss.groups()[0] < ftMiss.groups()[1]:
      #print prevplay + "\n" # debug
      #print play + "\n" # debug
      playList.remove(p)
    prevplay = play
  return playList

def writePlays(gamelist, playbyplay): # loop play-by-play parser over all games in a season
  delim = ","
  fr = open(gamelist,"r") 
  fw = open(playbyplay,"w")
  fr.readline() # first line is data names
  keys = ["Number","GameID","Quarter","MinRemain","SecRemain","Play"]
  fw.write(delim.join(keys) + "\n")
  for l in fr.readlines(): # for each game, parse play-by-play
    l = l.split("\t")
    date = l[0].replace("-","")
    teams = [l[1].rstrip(), l[2].rstrip()]
    print date + "".join(teams) # print which game we're working on
    playList = parsePlayList(date,teams) # get play list for this game
    playList = removeExtraRebs(playList) # remove, e.g., "Free Throw 1 of 2 Missed" -> "Team Rebound"
    for play in playList:
      fw.write(delim.join(play) + "\n")
  fw.close()
  
def writeBoxScores(gamelist, teamstats): # loop play-by-play parser over all games in a season
  delim = ","
  fr = open(gamelist,"r") 
  fw = open(teamstats,"w")
  fr.readline() # first line is data names
  for l in fr.readlines(): # for each game, parse play-by-play
    l = l.split("\t")
    date = l[0].replace("-","")
    teams = [l[1].rstrip(), l[2].rstrip()]
    print date + "".join(teams) # print which game we're working on
    boxscore = parseBoxScore(date,teams) # get play list for this game
    json.dump(boxscore, fw)
  fw.close()
  
def main(): 
  #writePlays(sys.argv[1], sys.argv[2])
  writeBoxScores(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
