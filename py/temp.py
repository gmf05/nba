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
#teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA'}
teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA', 'Washington Bullets':'WSB', 'Kansas City Kings':'KCK', 'San Diego Clippers':'SDC', 'Seattle SuperSonics':'SEA', 'Vancouver Grizzlies':'VAN'}
fr = open("nbaseasons.csv","r")
fr.readline() # throwaway line
for n in range(0, 28): # jump to 1990
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
csvfile = open('scorelines_00214.csv', 'r')
fieldnames = tuple(csvfile.readline().strip().split(",")) # get field names
reader = csv.reader( csvfile )
out = "{\n\t\"data\": [\n\t\t" + ",\n\t\t".join([json.dumps(row) for row in reader]) + "\n\t]\n}\n"
jsonfile = open('test2.json', 'w')
jsonfile.write(out)
jsonfile.close()