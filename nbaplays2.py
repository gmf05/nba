#!/usr/bin/python
import re
import numpy
import urllib2

def parseTR(trHTML,teams):
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
      time="12:00"
      q = S1.groups()[0]
      event = S1.groups()[0] 
    elif S2:
      time="00:00"
      q = S2.groups()[0]
      event = S2.group()
    else:
      isParsed = False
      time="00:00"
      event = "Error"
  else:
    isParsed = False
    time = "00:00"
    event = "Error"
  gamelist = "NBAdata/bballvalue/gamelist2011playoffs.txt"
  f = open(gamelist,'r')
  f.readline()
  return isParsed,time,event

def parsePlayList(date,teams):
  urlroot = "http://www.nba.com/games/"
  gameID = date + "".join(teams)
  url = urlroot + date + "/" + "".join(teams) + "/gameinfo.html"
  print url
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
      (isParsed,time,event) = parseTR(r,teams)
      if isParsed:
        print time + " " + event
        eventList.append([gameID,count,time,event])
        count+=1
  return eventList

def writePlays():
  # get game list
#   gamelist = "NBAdata/bballvalue/gamelist2011playoffs.txt"
  gamelist = "NBAdata/gamelist2014playoffs.txt"
  f = open(gamelist,'r')
  f.readline()
  for l in f.readlines():
    l = l.split("\t")
#     date = l[2].replace("-","")
#     teams = [l[9], l[7]]
    date = l[0].replace("-","")
    teams = [l[1].rstrip(), l[2].rstrip()]
    print teams
    try:
      eventList = parsePlayList(date,teams)
    except:
      []

def main():
  writePlays()
#   parsePlayList("20140424",["OKC","MEM"])
#   parsePlayList("20140201",["MIA","NYK"])

if __name__ == "__main__":
    main()
