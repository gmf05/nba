
import re
import urllib2
from bs4 import BeautifulSoup
delim = ','
teamCodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Washington Bullets':'WSB', 'Kansas City Kings':'KCK', 'San Diego Clippers':'SDC', 'Seattle SuperSonics':'SEA', 'Vancouver Grizzlies':'VAN', 'New Orleans/Oklahoma City Hornets':'NOK', 'League Average':'AVG'}

# get shot charts from ESPN.com
def writeShots():
  #fr = open("games_bbref_all.csv","r")
  calendarMonths = {'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12'}
  #id_start = 400578293
  #id_end = 400579522
#   id_start = 400488874
#   id_end = 400490103
  id_start = 400277722
  id_end = 400278950
  season = str(2014)
  fw = open("shots_test2.csv", "w")
  keys = ['gameid','gameid_espn','season','away','home','team','player_code','prd','clock','pts','made','x','y','distance']
  fw.write(delim.join(keys) + '\n')
  for gameid_espn in range(id_start, id_end+1):
    gameid_espn = str(gameid_espn)
    url1 = 'http://espn.go.com/nba/boxscore?gameId=' + gameid_espn
    url2 = 'http://sports.espn.go.com/nba/gamepackage/data/shot?gameId=' + gameid_espn
    html = urllib2.urlopen(url1).read()
    awayLong,homeLong,month,day,year = re.search('statistics from the (.+) vs. (.+) game played on (.+) (\d+), (\d+)', html).groups()
    away = teamCodes[awayLong]
    home = teamCodes[homeLong]
    date = year + calendarMonths[month] + day
    gameid = date + away + home
    print gameid # debug
    xml = urllib2.urlopen(url2).read()
    soup = BeautifulSoup(xml)
    d = [gameid, gameid_espn, season, away, home]
    for shot in soup.find_all('shot'):
      isMade=str(int(shot['made']=='true'))
      player_tm = [away,home][shot['t']=='h']
      player_code = shot['p'].lower().replace(' ','_') # player code
      dist,shottype,clock,prd0 = re.search('(\d+)ft (.+) (.+) in (\d).+', shot['d']).groups()
      if shottype=='3-pointer':
        pts = 3
      else:
        pts = 2
      prd = int(prd0) + 4*bool(re.search('OT', shot['d'])) # add 4 to periods if we are in OT
      shotI = [player_tm, player_code, str(prd), clock, str(pts), isMade, shot['x'], shot['y'], dist]
      print delim.join(d) + delim + delim.join(shotI)
      fw.write(delim.join(d) + delim + delim.join(shotI) + '\n')

def main():
  writeShots()        

if __name__ == "__main__":
    main()