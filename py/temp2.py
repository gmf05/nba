# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 10:19:44 2015

@author: gmf
"""
# get packages
import re
import datetime
import urllib2
import shutil
from bs4 import BeautifulSoup # for parsing html


fr = open("nbaseasons_short.csv","r")
fr.readline() # throwaway line
fr.readline() # 2009
fr.readline() # 2010
fr.readline() # 2011

for r in fr.readlines():
    r = r.strip().split(",")
    season_code = "002" + r[0]    
    strt = r[1].split("/")
    stp = r[2].split("/")
    startday = datetime.date(int(strt[0]),int(strt[1]),int(strt[2]))
    stopday = datetime.date(int(stp[0]),int(stp[1]),int(stp[2]))
    gamelist = "games_" + season_code + ".csv"
    writeGamelist(season_code, startday, stopday, gamelist)

# get nba data for 09-13 seasons
for n in range(10,13): # range(11, 13) when new game lists are made
    season_code = "002" + str(n).zfill(2)
    gamelist = "games_" + season_code + ".csv"
    scorelist = "scores_" + season_code + ".csv"
    writescoresCSV(gamelist, scorelist)
    #teamscorelist = "scorelines_" + season_code + ".csv"
    #writeTeamTotals(gamelist, teamscorelist)
    #playlist = "plays_" + season_code + ".csv"
    #writeplaysCSV(gamelist, playlist)

##
# comb bball-reference for season game lists
import re
import datetime    
import urllib2
teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BRK', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHH', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHO', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA', 'Washington Bullets':'WSB', 'Kansas City Kings':'KCK', 'San Diego Clippers':'SDC', 'Seattle SuperSonics':'SEA', 'Vancouver Grizzlies':'VAN', 'New Orleans/Oklahoma City Hornets':'NOK'}
fr = open("nbaseasons.csv","r")
fr.readline() # throwaway line
for n in range(0, 17): # jump ahead
    fr.readline() # throwaway line
for r in fr.readlines():
    r = r.strip().split(",")
    season_code = "002" + r[0]    
    strt = r[1].split("/")
    stp = r[2].split("/")
    startday = datetime.date(int(strt[0]),int(strt[1]),int(strt[2]))
    stopday = datetime.date(int(stp[0]),int(stp[1]),int(stp[2]))
    fw = open("games_test_" + season_code + ".csv", "w")  
    fw.write("gameid,away,home\n")
    delim = ","
    #teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS'}
    numdays = (stopday-startday).days
    datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]
    for d in datelist:
        diso = str.replace(d.isoformat(),'-','')
        url = "http://www.basketball-reference.com/boxscores/index.cgi?month=" + str(d.month) + "&day=" + str(d.day) + "&year=" + str(d.year)
        f = urllib2.urlopen(url)
        html = f.read()
        f.close()      
        games = re.findall("/boxscores/(" + diso + "0.+).html\"", html)
        for g in games:
            if not re.search(".html\">", g):
                url2 = "http://www.basketball-reference.com/boxscores/" + g + ".html"
                ttl = urllib2.urlopen(url2).read().split("<title>")[1].split("</title>")[0]
                tm1 = re.search("(.+) at", ttl).groups()[0]
                tm2 = re.search("at (.*?) Box Score", ttl).groups()[0]
                if re.match("at ", tm2): tm2=tm2.split("at ")[1] # handling weird bug...
                gameid = diso + teamAbbrevs[tm1] + teamAbbrevs[tm2]
                print gameid # debug
                fw.write(gameid + delim + teamAbbrevs[tm1] + delim + teamAbbrevs[tm2] + "\n")
    fw.close()

# convert csv to json (dataTables likes this JSON format)
import csv
import json
def csv_to_json(csvfile, jsonfile):
  #csvfile = open('scorelines_00214.csv', 'r')
  #csvfile = open('games_bbref_all.csv', 'r')
  fr = open(csvfile,'r')
  fw = open(jsonfile,'w')  
  fieldnames = tuple(fr.readline().strip().split(",")) # get field names
  reader = csv.reader( fr )
  out = "{\n\t\"data\": [\n\t\t" + ",\n\t\t".join([json.dumps(row) for row in reader]) + "\n\t]\n}\n"
  fw.write(out)
  fw.close()


csv_to_json('scores_bbref_all.csv','scores_bbref_all.json')


# find teams' last game of 2013-14 season, get advanced stats
fr = open("games_bbref_00213.csv","r")
fr.readline() # throwaway
baseurl = '<script type="text/javascript" src="http://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2Fboxscores%2FGAMEID.html&div=div_GAMETEAM_advanced"></script>'
#baseurl = 'http://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2Fboxscores%2FGAMEID.html&div=div_GAMETEAM_advanced'

games = []
[games.append(r.strip().split(delim)) for r in fr.readlines()]
aways = [games[i][1] for i in range(0,len(games))]
homes = [games[i][2] for i in range(0,len(games))]
teams = list(set(homes))
fw = open("scratch.txt","w")

for t in teams:
    for a,b in enumerate(homes):
        if b==t:
            i1=a
    for a,b in enumerate(aways):
        if b==t:
            i2=a
    i = max(i1,i2)
    home = games[i][2]
    gameid = games[i][0][0:8] + "0" + home
    url = baseurl.replace('GAMEID', gameid).replace('GAMETEAM', t)
    fw.write(t + '\n' + url + '\n')
fw.close()



games = []
[games.append(r.strip().split(delim)) for r in fr.readlines()]
aways = [games[i][1] for i in range(0,len(games))]
homes = [games[i][2] for i in range(0,len(games))]
teams = list(set(homes))
fw = open("scratch.txt","w")

for t in teams:
    for a,b in enumerate(homes):
        if b==t:
            i1=a
    for a,b in enumerate(aways):
        if b==t:
            i2=a
    i = max(i1,i2)
    home = games[i][2]
    gameid = games[i][0][0:8] + "0" + home
    url = baseurl.replace('GAMEID', gameid).replace('GAMETEAM', t)
    # get html, parse into advanced table box score
    # get table
fw.close()


############
# small function to convert gameid_espn to real gameids
def espn_to_gameid(gameid_espn):
  teamCodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Washington Bullets':'WSB', 'Kansas City Kings':'KCK', 'San Diego Clippers':'SDC', 'Seattle SuperSonics':'SEA', 'Vancouver Grizzlies':'VAN', 'New Orleans/Oklahoma City Hornets':'NOK', 'League Average':'AVG'}
  calendarMonths = {'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12'}
  #gameid_espn = str(gameid_espn) # if necessary
  url = 'http://espn.go.com/nba/boxscore?gameId=' + gameid_espn
  html = urllib2.urlopen(url).read()
  awayLong,homeLong,month,day,year = re.search('statistics from the (.+) vs. (.+) game played on (.+) (\d+), (\d+)', html).groups()
  away = teamCodes[awayLong]
  home = teamCodes[homeLong]
  date = year + calendarMonths[month] + day
  print date + away + home  
  return date + away + home

# loop to save gameid_espn as real gameids
teamCodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Washington Bullets':'WSB', 'Kansas City Kings':'KCK', 'San Diego Clippers':'SDC', 'Seattle SuperSonics':'SEA', 'Vancouver Grizzlies':'VAN', 'New Orleans/Oklahoma City Hornets':'NOK', 'League Average':'AVG'}
calendarMonths = {'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12'}
season = str(2014)
fw = open("espn_gameids_new.csv", "w")
keys = ['gameid_espn', 'gameid']
fw.write(delim.join(keys) + '\n')
#id_start = 400578293 # 2014-15
#id_end = 400579522 # 2014-15
#id_start = 400488874 # 2013-14
#id_end = 400490103 # 2013-14
id_start = 400277722 # 2012-13
id_end = 400278950 # 2012-13
for gameid_espn in range(id_start, id_end+1):
  gameid_espn = str(gameid_espn)
  fw.write( delim.join([gameid_espn, espn_to_gameid(gameid_espn)]) + '\n' )
fw.close()


###
fr = open("csv/shots_00214.csv")
fr.readline()
fw = open("temp/shots_test.csv","w")
[fw.write(delim.join(r.split(delim)[-5:])) for r in fr.readlines()]
fw.close()



##

for date in datelist:
  url = 'http://data.nba.com/5s/json/cms/noseason/scoreboard/' + date + '/games.json'
  jsn = json.loads(urllib2.urlopen(url).read())