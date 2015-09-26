
import re
import urllib2
from bs4 import BeautifulSoup
import json
delim = ','
teamCodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Washington Bullets':'WSB', 'Kansas City Kings':'KCK', 'San Diego Clippers':'SDC', 'Seattle SuperSonics':'SEA', 'Vancouver Grizzlies':'VAN', 'New Orleans/Oklahoma City Hornets':'NOK', 'League Average':'AVG'}

# get shot charts from ESPN.com
def writeShots():
  #fr = open("games_bbref_all.csv","r")
  calendarMonths = {'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12'}
  id_start = 400578293
  id_end = 400579522
#   id_start = 400488874
#   id_end = 400490103
  #id_start = 400277722
  #id_end = 400278950
  #season = str(2014)
  fw = open("shots_test_new.csv", "w")
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
    season = str( int(year) - (int(month)<=8) )
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
      #print delim.join(d) + delim + delim.join(shotI) # debug
      fw.write(delim.join(d) + delim + delim.join(shotI) + '\n')

def writeShots2():
  delim = ','
  fr = open("csv/games_00214.csv","r")
  fr.readline() # drop headers
  fw = open("csv/shots_test2.csv","w")
  I = [1, 4, 6, 7, 8, 9, 12, 16, 17, 18, 20]
  headers = ['gameid','gameid_num', 'player_code', 'team', 'prd', 'min_remain', 'sec_remain', 'pts', 'dist', 'x', 'y', 'made']
  fw.write(delim.join(headers) + '\n')
  for r in fr.readlines():
    gameid_num,gameid = r.split(delim)[0:2]
    print gameid # debug
    url = 'http://stats.nba.com/stats/shotchartdetail?Season=&SeasonType=Regular+Season&LeagueID=00&TeamID=0&PlayerID=0&GameID=' + gameid_num + '&Outcome=&Location=&Month=0&SeasonSegment=&DateFrom=&DateTo=&OpponentTeamID=0&VsConference=&VsDivision=&Position=&RookieYear=&GameSegment=&Period=0&LastNGames=0&ContextFilter=&ContextMeasure=FG_PCT&zone-mode=basic&viewShots=true'
    jsn = urllib2.urlopen(url).read()
    j = json.loads(jsn)
    #headers = j['resultSets'][0]['headers']
    shots = j['resultSets'][0]['rowSet']
    for s in shots:
      dat = [str(s[i]) for i in I]
      dat[1] = dat[1].lower().replace(' ','_').replace("'","") # format player_code
      dat[2] = teamCodes[dat[2]] # replace team name with team code
      dat[6] = re.search('(\d)PT Field Goal', dat[6]).groups()[0]
      dat.insert(0, gameid)
      #print delim.join(dat)
      fw.write(delim.join(dat) + '\n')
  fw.close()

def writeShots3():
  delim = ','
  I = [1, 4, 6, 7, 8, 9, 12, 16, 17, 18, 20]
  headers = ['gameid','gameid_num', 'player_code', 'team', 'prd', 'min_remain', 'sec_remain', 'pts', 'dist', 'x', 'y', 'made']
  game_start = 1
  game_end = 1230
  season_year = 12
  fw = open('csv/shots_002' + str(season_year).zfill(2) + '.csv','w')
  fw.write(delim.join(headers) + '\n')
  for game_num in range(game_start, game_end):
    gameid_num = '002' + str(season_year).zfill(2) + str(game_num).zfill(5)
    url1 = 'http://stats.nba.com/stats/boxscore?GameID=' + gameid_num + '&RangeType=0&StartPeriod=0&EndPeriod=0&StartRange=0&EndRange=0&playbyplay=undefined'
    try:    
      jsn1 = json.loads(urllib2.urlopen(url1).read())
      gameid = jsn1['resultSets'][0]['rowSet'][0][5].replace('/','')
      print gameid # debug
      url2 = 'http://stats.nba.com/stats/shotchartdetail?Season=&SeasonType=Regular+Season&LeagueID=00&TeamID=0&PlayerID=0&GameID=' + gameid_num + '&Outcome=&Location=&Month=0&SeasonSegment=&DateFrom=&DateTo=&OpponentTeamID=0&VsConference=&VsDivision=&Position=&RookieYear=&GameSegment=&Period=0&LastNGames=0&ContextFilter=&ContextMeasure=FG_PCT&zone-mode=basic&viewShots=true'
      jsn2 = json.loads(urllib2.urlopen(url2).read())
      shots = jsn2['resultSets'][0]['rowSet']
      for s in shots:
        dat = [str(s[i]) for i in I]
        dat[1] = dat[1].lower().replace(' ','_').replace("'","") # format player_code
        dat[2] = teamCodes[dat[2]] # replace team name with team code
        dat[6] = re.search('(\d)PT Field Goal', dat[6]).groups()[0]
        dat.insert(0, gameid)
        fw.write(delim.join(dat) + '\n')
    except Exception as e:
      print gameid,gameid_num,e
  fw.close()

def main():
  writeShots3()

if __name__ == "__main__":
    main()