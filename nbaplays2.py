#!/usr/bin/python
import re
import numpy
import urllib2

def timeRemaining(timeStr,qtr):
  qstart = [36, 24, 12, 0, -5, -10, -15, -20]
  tmin = qstart[qtr] + int(timeStr[0:2])
  tsign = numpy.sign(tmin)

  if tsign>=0:    
    tsec = float(timeStr[3::])
  else:
    tmin = tmin+1
    tsec = 60-float(timeStr[3::])
    if tsec==60:
      tsec = 0
      tmin -= 1
  tmin0 = abs(tmin)
  tminstr = '%02d' % tmin0
  tsecstr = '%02d' % tsec
  tdict = {"1":"00","0":"00","-1":"-00"}
  tremain =  tdict[str(tsign)] + ":" + tminstr + ":" + tsecstr
  return tremain

def parseTR(trHTML,teams,qtr):
  isParsed = True
  H = trHTML.split("<td")[1::]
  if len(H)==3:
    lft = re.search(">(.+)&nbsp;<",H[0])    
    rgt = re.search(">(.+)&nbsp;<",H[2])
    time = re.search(">(.+) <",H[1]).groups()[0] 
    if lft:
      play = "[" + teams[0] + "]" + lft.groups()[0]
    elif rgt:
      play = "[" + teams[1] + "]" + rgt.groups()[0]
    else:
      isParsed = False
      play = "Error"
  elif len(H)==1:
    S1 = re.search('<div class="gameEvent">(.+)</div>',H[0].rstrip())
    # check S1 -- jump ball doesn't print...
    S2 = re.search("End of  ([\d].+)",H[0])
    if S1:
      play = S1.groups()[0] 
      if qtr<5:
        time="12:00"
      else:
        time="5:00"
    elif S2:
      time="00:00"
      play = S2.group()
    else:
      isParsed = False
      tremain=""
      play = "Error"
  else:
    isParsed = False
    tremain = ""
    play = "Error"  
  if isParsed:
    tremain = timeRemaining(time,qtr)
  else:
    tremain = []
  return isParsed,tremain,play

def parsePlayList(date,teams):
  urlroot = "http://www.nba.com/games/"
  date = date.replace("-","")
  teamID = "".join(teams)
  gameID = date + teamID
  url = urlroot + date + "/" + teamID + "/gameinfo.html"
  f = urllib2.urlopen(url)
  html = f.read()
  f.close()
  h = html.split('<tr class="nbaGIPBPTeams">')
  h.remove(h[0])
  h[-1] = h[-1].split("</table>")[0]
  playList = []
  count=1
  for i in range(len(h)):
    rows = h[i].split("</tr>")[1::]
    for r in rows:
      (isParsed,time,play) = parseTR(r,teams,i)
      if isParsed:
        playList.append([gameID,str(count),time,play])
        count+=1
  return playList

def writePlays(season):
  gamelist = "gamelist_" + season + ".txt"
  playbyplay = "playbyplay_" + season + ".txt"

  fr = open(gamelist,"r")
  fw = open(playbyplay,"w")
  fr.readline()
  fw.write("GameID\tLineNumber\tTimeRemaining\tEntry\n")
  for l in fr.readlines():
    l = l.split("\t")
#     date = l[2].replace("-","") # old
#     teams = [l[9], l[7]] # old
    date = l[0].replace("-","")
    teams = [l[1].rstrip(), l[2].rstrip()]
    print teams
    try:
      playList = parsePlayList(date,teams)
      for play in playList:
        fw.write("\t".join(play) + "\n")
    except:
      [] 
  fw.close()

def main():
#  season = "2014playoffs"
  season = "201415"
  writePlays(season)
#   e = parsePlayList("2014-06-15",["MIA","SAS"])
#   parsePlayList("20140424",["OKC","MEM"])
#   parsePlayList("20140201",["MIA","NYK"])

if __name__ == "__main__":
    main()
