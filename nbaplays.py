#!/usr/bin/python
# code to turn a list of nba games into play-by-play data
import sys
import re
import urllib2

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

def writePlays(season): # loop play-by-play parser over all games in a season
  gamelist = "gamelist_" + season + ".txt" # list of games
#   playbyplay = "playbyplay_" + season + ".txt" # play-by-play output
  playbyplay = "playbyplay_201415C.txt"
  fr = open(gamelist,"r") 
  fw = open(playbyplay,"w")
  fr.readline() # first line is data names
  fw.write("Number\tGameID\tQuarter\tMinRemain\tSecRemain\tPlay\n") # first line is data names
  for l in fr.readlines(): # for each game, parse play-by-play
    l = l.split("\t")
    date = l[0].replace("-","")
    teams = [l[1].rstrip(), l[2].rstrip()]
    print date + "".join(teams) # print which game we're working on
    playList = parsePlayList(date,teams) # get play list for this game
    for play in playList:
      fw.write("\t".join(play) + "\n")
  fw.close()

def main():
  season = sys.argv[1]  
#   season = "201415"
  writePlays(season)

if __name__ == "__main__":
    main()
