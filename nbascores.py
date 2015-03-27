#
#
import sys
import re
import urllib2
from bs4 import BeautifulSoup # for parsing html

def writescoresCSV(gamelist, scorelist):
  delim = ","
  fr = open(gamelist,"r") 
  fr.readline() # first line is data names
  games = fr.readlines()
  fw = open(scorelist,"w")  
  keys = ["gameid", "gameid_num", "away", "home", "tm", "player_code", "pos", "min", "fgm", "fga", "3pm", "3pa", "ftm", "fta", "+/-", "off", "def", "tot", "ast", "pf", "st", "to", "bs", "ba", "pts"]
  Ncols = len(keys)
  fw.write(delim.join(keys) + "\n")
  for game in games:
    game = game.split("\n")[0].split(delim)
    gameid = game[1]
    print gameid + "\n"
    date = gameid[:8]
    teams = game[2:4]
    seasonyear = str(int(date[0:4]) - (int(date[4:6])<8)) # new year's games are part of prev season until october
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
        temp = e.text
        if temp=='&nbsp;':
          temp = ''          
        if re.match("([\d]+)-([\d]+)", temp):
          temp = temp.replace('-',',')
        I.append(temp)
      if len(I)==Ncols:
        fw.write(delim.join(I) + "\n")        
    # stat totals
    I = [gameid, game[0], teams[0], teams[1], teams[0]]
    entries = totalstats.find_all('td')
    I.append("total")
    #I.append(re.search("/playerfile/(.+)/index.html", entries[0].find_all('a')[0].attrs['href']).groups(0)[0])
    for e in entries[1:]:
      if e.text=='&nbsp;':
        e.text = None
      I.append(e.text)
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
        temp = str(e.text)
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
    #I.append(re.search("/playerfile/(.+)/index.html", entries[0].find_all('a')[0].attrs['href']).groups(0)[0])
    for e in entries[1:]:
      temp = str(e.text)
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
  fw = open(scorelist,"w")
  keys = ["gameid", "gameid_num", "away", "home", "tm", "player_code", "pos", "min", "fgm", "fga", "3pm", "3pa", "ftm", "fta", "+/-", "off", "def", "tot", "ast", "pf", "st", "to", "bs", "ba", "pts"]
  Ncols = len(keys)
  fw.write(delim.join(keys) + "\n")
  for game in games:
    game = game.split("\n")[0].split(delim)
    gameid = game[1]
    print gameid + "\n"
    date = gameid[:8]
    teams = game[2:4]
    seasonyear = str(int(date[0:4]) - (int(date[4:6])<8)) # new year's games are part of prev season until october
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
    I = [gameid, game[0], teams[0], teams[1], teams[0]]
    entries = totalstats.find_all('td')
    I.append("total")
    #I.append(re.search("/playerfile/(.+)/index.html", entries[0].find_all('a')[0].attrs['href']).groups(0)[0])
    for e in entries[1:]:
      temp = str(e.text)
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
    I = [gameid, game[0], teams[0], teams[1], teams[1]]
    entries = totalstats.find_all('td')
    I.append("total")
    #I.append(re.search("/playerfile/(.+)/index.html", entries[0].find_all('a')[0].attrs['href']).groups(0)[0])
    for e in entries[1:]:
      temp = str(e.text)
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
    season_code = "00213" # 2013-14 regular season
    #season_code = "00214" # 2014-15 regular season
    gamelist = "games_" + season_code + ".csv"
    scorelist = "boxscores_" + season_code + ".csv"
    writescoresCSV(gamelist, scorelist)

# boilerplate to run main on execution    
if __name__ == "__main__":
    season_code = sys.argv[1]
    gamelist = "games_" + season_code + ".csv"
    scorelist = "boxscores_" + season_code + ".csv"
    writescoresCSV(gamelist, scorelist)
