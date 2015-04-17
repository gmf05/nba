#!/usr/bin/python
# code to make a list of nba games between 2 dates
import datetime
import re
import urllib2

def writeTeamList():
    url = "http://stats.nba.com/stats/commonteamyears?LeagueID=00" # 00 = NBA
    web = urllib2.urlopen(url)
    tree = ET.parse(web).getroot()

def getTeams():
    # write team list if doesn't exist
    # else load teamlist
    # keep teams playing in 2014
    

def writeGamelist(filename,startday,stopday):
  # def writeGamelist(filename,date1,date2)
  # assumes date1, date2 are of 'mm-dd-yyyy' format
  #
  # make dictionary of team names <-> abbreviation
  teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS'}
  fw = file("gamelist_" + filename + ".txt", "w")
  numdays = (stopday-startday).days
  datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]
  # for each day, get source code for day's schedule
  # then parse html for text "Link to game info for [[team 1]] vs [[team 2]]"
  for d in datelist:
    diso = str.replace(d.isoformat(),'-','')
    url = "http://www.nba.com/gameline/" + diso
    f = urllib2.urlopen(url)
    html = f.read()
    f.close()
    # every third entry in "Link to game info..." is a new game
    # NOTE: This may be too simple & require work if there are bugs down the road, but it works for now
    # Otherwise replace this with a better regexp match or push full match to ma2 below
    ma1=html.split("Link to game info for ")
    i=1
    while i<len(ma1):
      ma2=re.search(r'(?P<First>.+?) vs. (?P<Second>.+?)"',ma1[i])
      team1abbrev=teamAbbrevs[ma2.group(1)]
      team2abbrev=teamAbbrevs[ma2.group(2)]
      gameID = diso + team1abbrev + team2abbrev 
      print gameID + "\n"
      i+=3
      fw.write(diso + "\t" + team1abbrev + "\t" + team2abbrev + "\n")
  fw.close()

def main():
#   season = '201415-preAS'
#   date1 = datetime.date(2014,10,28)
#   date2 = datetime.date(2015,02,12)
#   writeGamelist(season, date1, date2)
# 
#   season = '201415-postAS'
#   date1 = datetime.date(2015,02,16)
#   date2 = datetime.date(2015,03,01)
#   writeGamelist(season, date1, date2)

  season = '201415-latest'
  date1 = datetime.date(2015,03,02)
  date2 = datetime.date.today() - datetime.timedelta(1) # i.e. through yesterday
  writeGamelist(season, date1, date2)

if __name__ == "__main__":
    main()
