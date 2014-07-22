#!/usr/bin/python
import re
import numpy
import urllib2

def parseTR(trHTML,teams,qtr):
  qstart = [36, 24, 12, 0, -5, -10, -15, -20]
  isParsed = True
  H = trHTML.split("<td")[1::]
  if len(H)==3:
    lft = re.search(">(.+)&nbsp;<",H[0])    
    rgt = re.search(">(.+)&nbsp;<",H[2])
    time = re.search(">(.+) <",H[1]).groups()[0] 
    if lft:
      event = "[" + teams[0] + "]" + lft.groups()[0]
    elif rgt:
      event = "[" + teams[1] + "]" + rgt.groups()[0]
    else:
        isParsed = False
        event = "Error"
  elif len(H)==1:
    S1 = re.search('<div class="gameEvent">(.+)</div>',H[0].rstrip())
    # check S1 -- jump ball doesn't print...
    S2 = re.search("End of  ([\d].+)",H[0])
    if S1:
      if qtr<5:
        time="12:00"
      else:
        time="5:00"
      event = S1.groups()[0] 
    elif S2:
      time="00:00"
      event = S2.group()
    else:
      isParsed = False
      time="--"
      event = "Error"
  else:
    isParsed = False
    time = "00:00"
    event = "Error"
  
  if isParsed:
    tmin = int(time[0:2])
    tsec = float(time[3::])
    tremain =  str(qstart[qtr]+tmin) + ":" + '%02d' % tsec
  else:
    tremain = []
  return isParsed,tremain,event

def parsePlayList(date,teams):
  urlroot = "http://www.nba.com/games/"
  date = date.replace("-","")
  gameID = date + "".join(teams)
  url = urlroot + date + "/" + "".join(teams) + "/gameinfo.html"
  f = urllib2.urlopen(url)
  html = f.read()
  f.close()
  H = html.split('<tr class="nbaGIPBPTeams">')
  H.remove(H[0])
  H[-1] = H[-1].split("</table>")[0]
  eventList = []
  count=1
  for i in range(len(H)):
    rows = H[i].split("</tr>")[1::]
    for r in rows:
      (isParsed,time,event) = parseTR(r,teams,i)
      if isParsed:
        eventList.append([gameID,str(count),time,event])
        count+=1
  return eventList

def writePlays(season):
  gamelist = "NBAdata/gamelist" + season + ".txt"
  playbyplay = "NBAdata/playbyplay" + season + ".txt"
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
      eventList = parsePlayList(date,teams)
      for event in eventList:
        fw.write("\t".join(event) + "\n")
    except:
      [] 
  fw.close()

def main():
  season = "2014playoffs"
  writePlays(season)
#   e = parsePlayList("2014-06-15",["MIA","SAS"])
#   parsePlayList("20140424",["OKC","MEM"])
#   parsePlayList("20140201",["MIA","NYK"])

if __name__ == "__main__":
    main()
