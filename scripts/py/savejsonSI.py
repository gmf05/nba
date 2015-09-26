#!/usr/bin/python
# get JSON from SI.com -> raw text
import urllib2 # query web
import json # parse json
import sys # take input arguments from command line
import re # regular expressions
import datetime # date arithmetic

if __name__ == '__main__':

  # get list of all dates in the given season
  #season_year = sys.argv[1]      
  season_year = '2014'
  fr = open("csv/nbaseasons.csv","r")
  for r in fr.readlines():
    yr,day1,day2 = r.strip().split(',')
    if yr==season_year[-2:]:
      day1 = day1.split('/')
      startday = datetime.date(int(day1[0]),int(day1[1]),int(day1[2]))
      day2 = day2.split('/')
      stopday = datetime.date(int(day2[0]),int(day2[1]),int(day2[2]))
      break
  numdays = (stopday-startday).days
  datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]  
    
  # for each game on the given dates, get dataid
  idlist = []
  for d in datelist:
    curr_date = '-'.join([str(d.year), str(d.month).zfill(2), str(d.day).zfill(2)])
    diso = curr_date.replace('-','')
    print diso # debug
    sched_url = 'http://www.si.com/nba/schedule?season=' + season_year + '&date=' + curr_date
    html = urllib2.urlopen(sched_url).read()
    ma1 = re.findall('data-id="(.*?)"',html)
    ma2 = re.findall('data-gamecode="(.*?)"',html)
    for i in range(0,len(ma1)):
      if ma2[i][0:8]==diso: # if data-id matches curr_date, save it
        print ma1[i]
        idlist.append(ma1[i])
  
  # saving dataid in case something goes wrong
  temp = open("si_dataid_" + season_year + "_temp.csv","w")
  temp.write('dataid\n')
  for i in idlist:
    temp.write(i + '\n')
  temp.close()
  
  teamcodes = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA'}
  data_url = 'http://www.si.com/pbp/liveupdate?json=1&sport=basketball%2Fnba&id=*DATAID*&box=true&pbp=true&linescore=true'
  id_file = open("si_dataid_" + season_year + ".csv","w")
  id_file.write(','.join(['dataid', 'gameid']) + '\n')
  
  ## loop over games, collect data
  for dataid in idlist:
    # load json for given game
    j = json.loads(urllib2.urlopen(data_url.replace('*DATAID*', dataid)).read())
    game = j['apiResults'][0]['league']['season']['eventType'][0]['events'][0]
    # convert gameid to usual format (date + team1 + team2)
    date = game['startDate'][0] # 0: local time
    diso = str(date['year']) + str(date['month']).zfill(2) + str(date['date']).zfill(2)
    homename,awayname = [game['teams'][i]['location'] + ' ' + game['teams'][i]['nickname'] for i in[0, 1]]
    gameid = diso + teamcodes[awayname] + teamcodes[homename]
    print dataid, gameid # debug
    # save results
    id_file.write(','.join([dataid, gameid]) + '\n')
    json_file = open("json/si_" + gameid + ".json", "w")
    json.dump(game, json_file)
    json_file.close()    

  id_file.close()
      
      
