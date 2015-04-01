#!/usr/bin/python
#
import sys
import re
import urllib2
import shutil
from bs4 import BeautifulSoup # for parsing html

#delim = ","
#score1 = "lines_00213.csv"
#score2 = "lines2_00213.csv"
#fr = open(score1,"r")
#fw = open(score2,"w")
#for r in fr.readlines():
#    r0 = r.split(delim)
#    r1 = r0[0:-1]
#    fw.write(delim.join([r0[0], r0[1]]) + "\n")
#    fw.write(delim.join([r0[0], r0[2]])) # already has newline
#fw.close()

def getAllLines(gamelist, linelist):
  fr = open(gamelist, "r")
  fr.readline() # field names is first line
  fw = open(linelist, "w")
  delim = ","
  for game in fr.readlines():
    gameid = game.split(delim)[1]
    line = getLine(gameid)
    print gameid + delim + str(line[0]) + delim + str(line[1]) # debug
    fw.write(gameid + delim + str(line[0]) + "\n")
    fw.write(gameid + delim + str(line[1]) + "\n")
  fw.close()

def getLine(gameid):   # get final money line from vegasinsider.com 
  # dictionary of name conventions used on the site
  teamNames = {"ATL": "hawks", "BOS":"celtics", "BKN":"nets", "CHA":"hornets","CHI":"bulls","CLE":"cavaliers","DAL":"mavericks","DEN":"nuggets","DET":"pistons","GSW":"warriors","HOU":"rockets","IND":"pacers","LAC":"clippers","LAL":"lakers","MEM":"grizzlies","MIA":"heat","MIL":"bucks","MIN":"timberwolves","NOP":"pelicans","NYK":"knicks","OKC":"thunder","ORL":"magic","PHI":"76ers","PHX":"suns","POR":"trail-blazers","SAC":"kings","SAS":"spurs","TOR":"raptors","UTA":"jazz","WAS":"wizards"}  
  date = "-".join([gameid[4:6], gameid[6:8], gameid[2:4]])
  url = u"http://www.vegasinsider.com/nba/odds/las-vegas/line-movement/" + teamNames[gameid[8:11]] + "-@-" + teamNames[gameid[11:14]] + ".cfm/date/" + date
  # spoof an alternate user-agent: works for vegasinsider
  # courtesy of stackoverflow
  headers = {'User-Agent':"Mozilla"}  
  request = urllib2.Request(url, headers=headers)  
  response = urllib2.urlopen(request)
  with open("tempout.txt", "wb") as outfile:
    shutil.copyfileobj(response, outfile)
  html = open("tempout.txt", "rb").read()
  # pseudocode:
  # Jump to VI CONSENSUS LINE MOVEMENTS
  # Jump to end of table (header for VI)
  # Get following <TABLE> of lines
  # Start at last row of this table and work backwards until a moneyline is extracted
  txt = html[re.search("VI CONSENSUS LINE MOVEMENTS",html).start():]  
  txt = txt[re.search("</TABLE>",txt).end():] # get following table (1)
  txt = txt[0:re.search("</TABLE>",txt).end():] # get following table (2)
  txt = txt.split("<TR>") # break up table rows
  gotLine = False
  maxRows = round(0.5*len(txt))
  trind = -1
  while not gotLine and abs(trind)<maxRows:
    try:  
      txt0 = txt[trind].split("</TD>")
      txt1 = txt0[2][re.search("<TD.*>",txt0[2]).end():].strip()
      txt2 = txt0[3][re.search("<TD.*>",txt0[3]).end():].strip()
      if re.search(gameid[8:11], txt1): # if away team is favorite
        l1 = int(re.search("([+-][\d]+)", txt1).groups()[0])
        try:
          l2 = int(re.search("([+-][\d]+)", txt2).groups()[0])
        except: # handles case when money line = 0 bc there is no +/-
          l2 = int(re.search("([\d]+)", txt2).groups()[0])
      else: # if home team is favorite
        try:    
          l1 = int(re.search("([+-][\d]+)", txt2).groups()[0])
        except: # handles case when money line = 0 bc there is no +/-
          l1 = int(re.search("([\d]+)", txt2).groups()[0])
        l2 = int(re.search("([+-][\d]+)", txt1).groups()[0])
      gotLine = True
    except: # if this parsing fails, go back a row
      l1 = None
      l2 = None      
      trind -= 1
  return [l1, l2]

def combineScoreLines(scorelist, linelist, scorelinelist):
  delim = ","  
  fr1 = open(scorelist, "r")
  fr2 = open(linelist, "r")
  fw = open(scorelinelist, "w")
  r1 = fr1.readline() # dummy line = field names
  r1 = r1.strip("\n")
  fw.write(r1 + delim + "line\n")
  for r1 in fr1.readlines():
    r1 = r1.strip("\n")
    r2 = fr2.readline()
    r2b = r2.split(delim)[1]
    fw.write(r1 + delim + r2b)
  fw.close()

def writescoresCSV(gamelist, scorelist):
  delim = ","
  fr = open(gamelist,"r") 
  fr.readline() # first line is data names
  games = fr.readlines()
  fw = open(scorelist,"a")
  keys = ["gameid", "gameid_num", "away", "home", "tm", "player_code", "pos", "min", "fgm", "fga", "3pm", "3pa", "ftm", "fta", "+/-", "off", "def", "tot", "ast", "pf", "st", "to", "bs", "ba", "pts"]
  Ncols = len(keys)
  #fw.write(delim.join(keys) + "\n")
  for game in games:
    game = game.split("\n")[0].split(delim)
    gameid = game[1]
    print gameid # debug
    date = gameid[:8]
    teams = game[2:4]
    seasonyear = str(int(date[0:4]) - (int(date[4:6])<8)) # new year's games are part of prev season until october
    #line = [100, 100]
    #url = "http://www.nba.com/games/game_component/dynamic/" + date + "/" + teams + "/pbp_all.xml"
    url = "http://data.nba.com/data/10s/html/nbacom/" + seasonyear + "/gameinfo/" + date + "/" + game[0] + "_boxscore_csi.html"
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    # get to table
    teamstats = soup.find_all("table")
    
    #
    ## away team
    #
    playerstats = teamstats[0].find_all('tr')[3:-2]
    totalstats = teamstats[0].find_all('tr')[-2]
    for p in playerstats:
      I = [gameid, game[0], teams[0], teams[1], teams[0]]
      entries = p.find_all('td')
      # replace player name with player code
      try:
        player_code = re.search("/playerfile/(.+)/index.html", entries[0].find_all('a')[0].attrs['href']).groups()[0]
      except:
        player_code = 'player_code'
      I.append(player_code)
      for e in entries[1:]:
        try:      
          temp = str(e.text)
        except:
          temp = ''
        if temp=='&nbsp;':
          temp = ''          
        if re.match("([\d]+)-([\d]+)", temp):
          temp = temp.split("-")
          for t in temp: I.append(t)
        else:
          I.append(temp)
      if len(I)==Ncols:
        fw.write(delim.join(I) + "\n")        
    # stat totals
    I = [gameid, game[0], teams[0], teams[1], teams[0]]
    entries = totalstats.find_all('td')
    I.append("total")
    for e in entries[1:]:
      try:      
        temp = str(e.text)
      except:
        temp = ''
      if temp=='&nbsp;':
        temp = ''          
      if re.match("([\d]+)-([\d]+)", temp):
        temp = temp.split("-")
        for t in temp: I.append(t)
      else:
        I.append(temp)
    if len(I)==Ncols:
      fw.write(delim.join(I) + "\n")
    #
    ## home team
    #
    playerstats = teamstats[1].find_all('tr')[3:-2]
    totalstats = teamstats[1].find_all('tr')[-2]
    for p in playerstats:
      I = [gameid, game[0], teams[0], teams[1], teams[1]]
      entries = p.find_all('td')
      # replace player name with player code
      try:
        player_code = re.search("/playerfile/(.+)/index.html", entries[0].find_all('a')[0].attrs['href']).groups()[0]
      except:
        player_code = 'player_code'
      I.append(player_code)
      for e in entries[1:]:
        try:      
          temp = str(e.text)
        except:
          temp = ''
        if temp=='&nbsp;':
          temp = ''          
        if re.match("([\d]+)-([\d]+)", temp):     
          temp = temp.split("-")
          for t in temp: I.append(t)
        else:
          I.append(temp)
        if len(I)==Ncols:
          fw.write(delim.join(I) + "\n")    
    # stat totals
    I = [gameid, game[0], teams[0], teams[1], teams[1]]
    entries = totalstats.find_all('td')
    I.append("total")
    for e in entries[1:]:
      try:      
        temp = str(e.text)
      except:
        temp = ''
      if temp=='&nbsp;':
        temp = ''          
      if re.match("([\d]+)-([\d]+)", temp):     
        temp = temp.split("-")
        for t in temp: I.append(t)
      else:
        I.append(temp)
    if len(I)==Ncols:
      fw.write(delim.join(I) + "\n")
  fw.close()
    
def writeTeamTotals(gamelist, scorelist):
  delim = ","
  fr = open(gamelist,"r") 
  fr.readline() # first line is data names
  games = fr.readlines()
  fw = open(scorelist,"a")
  keys = ["gameid", "gameid_num", "away", "home", "tm", "line", "player_code", "pos", "min", "fgm", "fga", "3pm", "3pa", "ftm", "fta", "+/-", "off", "def", "tot", "ast", "pf", "st", "to", "bs", "ba", "pts"]
  Ncols = len(keys)
  #fw.write(delim.join(keys) + "\n")
  for game in games:
    game = game.split("\n")[0].split(delim)
    gameid = game[1]
    print gameid # debug
    date = gameid[:8]
    teams = game[2:4]
    seasonyear = str(int(date[0:4]) - (int(date[4:6])<8)) # new year's games are part of prev season until october
    line = getLine(gameid)
    #line = [100 100]
    #url = "http://www.nba.com/games/game_component/dynamic/" + date + "/" + teams + "/pbp_all.xml"
    url = "http://data.nba.com/data/10s/html/nbacom/" + seasonyear + "/gameinfo/" + date + "/" + game[0] + "_boxscore_csi.html"
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    # get to table
    teamstats = soup.find_all("table")
    
    #
    ## away team
    #
    # stat totals
    totalstats = teamstats[0].find_all('tr')[-2]
    I = [gameid, game[0], teams[0], teams[1], teams[0], str(line[0])]
    entries = totalstats.find_all('td')
    I.append("total")
    for e in entries[1:]:
      try:      
        temp = str(e.text)
      except:
        temp = ''
      if temp=='&nbsp;':
        temp = ''          
      if re.match("([\d]+)-([\d]+)", temp):
        temp = temp.split("-")
        for t in temp: I.append(t)
      else:
        I.append(temp)
    if len(I)==Ncols:
      fw.write(delim.join(I) + "\n")
    #
    ## home team
    #
    # stat totals
    totalstats = teamstats[1].find_all('tr')[-2]
    I = [gameid, game[0], teams[0], teams[1], teams[1], str(line[1])]
    entries = totalstats.find_all('td')
    I.append("total")
    for e in entries[1:]:
      try:      
        temp = str(e.text)
      except:
        temp = ''
      if temp=='&nbsp;':
        temp = ''          
      if re.match("([\d]+)-([\d]+)", temp):     
        temp = temp.split("-")
        for t in temp: I.append(t)
      else:
        I.append(temp)
    if len(I)==Ncols:
      fw.write(delim.join(I) + "\n")
  fw.close()

def main():
    #season_code = "00213" # 2013-14 regular season
    season_code = "00214" # 2014-15 regular season
    gamelist = "games_" + season_code + ".csv"
    scorelist = "scores_" + season_code + ".csv"
    writescoresCSV(gamelist, scorelist)
    teamscorelist = "scores_team_" + season_code + ".csv"
    writeTeamTotals(gamelist, teamscorelist)

    #writescoresCSV(gamelist, scorelist)
    #writeTeamTotals(gamelist, teamscorelist)

# boilerplate to run on execution
if __name__ == "__main__":
    main()
