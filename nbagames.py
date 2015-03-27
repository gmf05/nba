#!/usr/bin/python
# code to make a list of nba games between 2 dates
import datetime
import re
import urllib2

def writeGamelist(season_code,startday,stopday):
  # def writeGamelist(filename,date1,date2)
  # assumes date1, date2 are of 'mm-dd-yyyy' format
  #
  # make dictionary of team names <-> abbreviation
  teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS'}
  delim = ","
  fw = file("games_" + season_code + ".csv", "w")
  # add line of field names
  keys = ['gameid_num', 'gameid', 'away', 'home']
  fw.write(delim.join(keys) + '\n')
  # get list of days and search for games
  numdays = (stopday-startday).days
  datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]
  count=1
  for d in datelist:
    diso = str.replace(d.isoformat(),'-','')
    url = "http://data.nba.com/data/10s/html/nbacom/" + str(startday.year) + "/gameinfo/" + diso + "/" + season_code + str(count).zfill(5) + "_boxscore_csi.html"
    #url = "http://www.nba.com/gameline/" + diso
    f = urllib2.urlopen(url)
    html = f.read()
    f.close()
    # every third entry in "Link to game info..." is a new game
    # NOTE: This may be too simple & require work if there are bugs down the road, but it works for now
    # Otherwise replace this with a better regexp match or push full match to ma2 below
    #ma1=html.split("Link to game info for ")
    #i=1
    #while i<len(ma1):
      ma2=re.search(r'(?P<First>.+?) vs. (?P<Second>.+?)"',ma1[i])
      try: # may be necessary to catch KeyError that occurs at all-star break
        team1abbrev=teamAbbrevs[ma2.group(1)]
        team2abbrev=teamAbbrevs[ma2.group(2)]
        gameid = diso + team1abbrev + team2abbrev
        gameid_num = season_code + str(count).zfill(5) # convert count to 5-digit string
        dout = [gameid_num, gameid, team1abbrev, team2abbrev]
        print gameid_num + delim + gameid + "\n"
        count+=1
        fw.write(delim.join(dout) + "\n")
      except:
        # if unexpected team occurs
        []
      i+=3
  fw.close()

def main():
   filename = '201415-latest'
   season_code = '00214'
   date1 = datetime.date(2014,10,28)
   date2 = datetime.date.today() - datetime.timedelta(1) # i.e. through yesterday
   writeGamelist(filename, season_code, date1, date2)

#  filename = '201314-regular'
#  season_code = '00213'
#  date1 = datetime.date(2013,10,29)
#  date2 = datetime.date(2014,04,16)
#  writeGamelist(filename, season_code, date1, date2)

if __name__ == "__main__":
    main()
