#!/usr/bin/python
# code to make a list of nba games between 2 dates
import sys
import re
import urllib2
import datetime

def writeGamelist(season_code,startday,stopday,gamelist):
  # def writeGamelist(filename,date1,date2)
  # assumes date1, date2 are of 'mm-dd-yyyy' format
  #
  # make dictionary of team names <-> abbreviation
  #teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS'}
  teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA'}
  delim = ","
  #fw = file("games_" + season_code + ".csv", "w")
  fw = file(gamelist, "w")
  # add line of field names
  keys = ['gameid_num', 'gameid', 'away', 'home']
  fw.write(delim.join(keys) + '\n')
  # get list of days and search for games
  numdays = (stopday-startday).days
  datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]
  count=1
  season_year = str(startday.year - (startday.month<8))
  for d in datelist:
    diso = str.replace(d.isoformat(),'-','')
    pingflag = True 
    while pingflag:
      try:
        url = "http://data.nba.com/data/10s/html/nbacom/" + season_year + "/gameinfo/" + diso + "/" + season_code + str(count).zfill(5) + "_boxscore_csi.html"
        f = urllib2.urlopen(url)
        html = f.read()
        f.close()
        # parse html to get team codes
        #ma = re.findall("<th colspan=\"17\">(.+)</th>", html) # good for formatted lines
        ma = re.findall("<th colspan=\"17\">(.*?)</th>", html) # good for non-greedy match, non-formatted lines
        if ma:
          ma[0] = ma[0].split(' (')[0] # drop team record
          ma[1] = ma[1].split(' (')[0] # drop team record
          team1abbrev=teamAbbrevs[ma[0]]
          team2abbrev=teamAbbrevs[ma[1]]
          gameid = diso + team1abbrev + team2abbrev
          gameid_num = season_code + str(count).zfill(5) # convert count to 5-digit string
          dout = [gameid_num, gameid, team1abbrev, team2abbrev]
          print gameid_num + delim + gameid + "\n"
          fw.write(delim.join(dout) + "\n")
        count+=1
      except urllib2.HTTPError:
        pingflag = False
      except:
        # debug
        # instead of this....
        # count+=1??, pingflag = False??
        print url
        print d
        print str(count)
        break
  fw.close()

def updateGamelist(season_code, gamelist):
  # def writeGamelist(filename,date1,date2)
  # assumes date1, date2 are of 'mm-dd-yyyy' format
  #
  # make dictionary of team names <-> abbreviation
  teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS'}
  delim = ","
  #fw = file("games_" + season_code + ".csv", "w")  
  fr = file(gamelist, "r")  
  A = fr.readlines()[-1].split(delim)
  fr.close()
  fw = file(gamelist, "a")
  startdate = A[1]
  startday = datetime.date(int(startdate[0:4]), int(startdate[4:6]), int(startdate[6:8])) + datetime.timedelta(1)
  stopday = datetime.date.today()
  seasonyear = str(int(startdate[0:4]) - (int(startdate[4:6])<8)) # new year's games are part of prev season until october
  # get list of days and search for games
  numdays = (stopday-startday).days
  datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]
  count = int(A[0].split(season_code)[1]) + 1
  for d in datelist:
    diso = str.replace(d.isoformat(),'-','')
    pingflag = True 
    while pingflag:
      try:
        url = "http://data.nba.com/data/10s/html/nbacom/" + seasonyear + "/gameinfo/" + diso + "/" + season_code + str(count).zfill(5) + "_boxscore_csi.html"
        f = urllib2.urlopen(url)
        html = f.read()
        f.close()
        # parse html to get team codes
        ma = re.findall("<th colspan=\"17\">(.+)</th>", html)
        if ma:
          ma[0] = ma[0].split(' (')[0] # drop team record
          ma[1] = ma[1].split(' (')[0] # drop team record
          team1abbrev=teamAbbrevs[ma[0]]
          team2abbrev=teamAbbrevs[ma[1]]
          gameid = diso + team1abbrev + team2abbrev
          gameid_num = season_code + str(count).zfill(5) # convert count to 5-digit string
          dout = [gameid_num, gameid, team1abbrev, team2abbrev]
          print gameid_num + delim + gameid + "\n"
          fw.write(delim.join(dout) + "\n")
        count+=1
      except urllib2.HTTPError:
        pingflag = False
      except:
        # debug
        print url
        print d
        print str(count)
        break
  fw.close()

def writeGamelist2():
  0    

def main():
  #season_code = '00213' # 2013-14 regular season
  #date1 = datetime.date(2013,10,29)
  #date2 = datetime.date(2014,04,16)   

  season_code = '00214' # 2014-15 regular season
  date1 = datetime.date(2014,10,28)
  date2 = datetime.date(2015,03,25)

  season_code = '00214' # 2014-15 regular season
  date1 = datetime.date(2014,03,26)
  date2 = datetime.date(2015,03,28)
  gamelist = "2015latest.csv"

  writeGamelist(season_code, date1, date2, gamelist)

# boilerplate to run on execution
if __name__ == "__main__":
    season_code = sys.argv[1]
    # parse sys.argv[2] & sys.argv[3] for dates
    date1 = 0
    date2 = 0
    writeGamelist(season_code, date1, date2)
