#!/usr/bin/python
#
#import sys
import re
import datetime
import urllib2
import shutil
from bs4 import BeautifulSoup # for parsing html

def latestGamelist(season_code, gamelist):
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
  fw0 = file(gamelist, "a")  
  fw = file("games_latest_" + season_code + ".csv", "w")
  keys = ['gameid_num', 'gameid', 'away', 'home']
  fw.write(delim.join(keys) + '\n')
  startdate = A[1]
  startday = datetime.date(int(startdate[0:4]), int(startdate[4:6]), int(startdate[6:8])) + datetime.timedelta(1)
  stopday = datetime.date.today() - datetime.timedelta(1) # stop yesterday
  seasonyear = str(startday.year - (startday.month<8)) # new year's games are part of prev season until october
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
          print gameid # debug
          fw.write(delim.join(dout) + "\n")
          fw0.write(delim.join(dout) + "\n")
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
  fw0.close()

def getLine(gameid):   # get final money line from vegasinsider.com 
  # dictionary of name conventions used on the site
  # NOTE: multiple team codes are NOT the standard ones used by the NBA
  # e.g. UTA = UTH, BKN = NJN, PHX = PHO, NOP = NOR
  teamNames = {"ATL": "hawks", "BOS":"celtics", "BKN":"nets", "CHA":"hornets","CHI":"bulls","CLE":"cavaliers","DAL":"mavericks","DEN":"nuggets","DET":"pistons","GSW":"warriors","HOU":"rockets","IND":"pacers","LAC":"clippers","LAL":"lakers","MEM":"grizzlies","MIA":"heat","MIL":"bucks","MIN":"timberwolves","NOP":"pelicans","NYK":"knicks","OKC":"thunder","ORL":"magic","PHI":"76ers","PHX":"suns","POR":"trail-blazers","SAC":"kings","SAS":"spurs","TOR":"raptors","UTA":"jazz","WAS":"wizards"}  
  teamAbbrevVI = {"ATL": "ATL", "BOS":"BOS", "BKN":"NJN", "CHA":"CHA","CHI":"CHI","CLE":"CLE","DAL":"DAL","DEN":"DEN","DET":"DET","GSW":"GSW","HOU":"HOU","IND":"IND","LAC":"LAC","LAL":"LAL","MEM":"MEM","MIA":"MIA","MIL":"MIL","MIN":"MIN","NOP":"NOR","NYK":"NYK","OKC":"OKC","ORL":"ORL","PHI":"PHI","PHX":"PHO","POR":"POR","SAC":"SAC","SAS":"SAS","TOR":"TOR","UTA":"UTH","WAS":"WAS"}
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
  maxRows = len(txt)
  trind = -1
  while not gotLine and abs(trind)<maxRows:
    try:  
      txt0 = txt[trind].split("</TD>")
      txt1 = txt0[2][re.search("<TD.*>",txt0[2]).end():].strip()
      txt2 = txt0[3][re.search("<TD.*>",txt0[3]).end():].strip()
      if re.search(teamAbbrevVI[gameid[8:11]], txt1): # if away team is favorite
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
      trind -= 1
  if not gotLine:
    l1 = ''
    l2 = ''
  return [l1, l2]
  

def gamelinesToday():
  # get list of nba games happening today
  #
  # IDEA:
  # for each day, get source HTML for day's schedule
  # then parse HTML for text "Link to game info for [[team 1]] vs [[team 2]]"
  # use regular expressions to match [[team 1]] and [[team 2]]
  # then convert to gameID (e.g. "20150329LALBKN")
  # Usually these tags repeat, so just keep the unique ones  
  fw = open("linestoday.csv", "w")  
  fw.write("gameid,away,home,awayline,homeline\n")
  delim = ","
  teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BKN', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHA', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHX', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS'}
  diso = str.replace(datetime.date.today().isoformat(),'-','')
  url = "http://www.nba.com/gameline/" + diso
  f = urllib2.urlopen(url)
  html = f.read()
  f.close()
  ma1=html.split("Link to game info for ")
  gameids = []
  for i in range(1,len(ma1)):
    ma2=re.search(r'(?P<First>.+?) vs. (?P<Second>.+?)"',ma1[i])
    team1abbrev=teamAbbrevs[ma2.group(1)]
    team2abbrev=teamAbbrevs[ma2.group(2)]
    gameid = diso + team1abbrev + team2abbrev 
    gameids.append(gameid)
  gameids = list(set(gameids)) # keep unique gameids
  #print "\n".join(gameids) # debug
  # get lines for these games
  for g in gameids:
    l = getLine(g)
    fw.write( g + delim + g[8:11] + delim + g[11:14] + delim +  str(l[0]) + delim + str(l[1]) + "\n" )
    print g + delim + g[8:11] + delim + g[11:14] + delim +  str(l[0]) + delim + str(l[1]) # debug
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

def writeplaysCSV(gamelist, playlist):
  delim = ","
  fr = open(gamelist,"r") 
  fr.readline() # first line is data names
  games = fr.readlines()
  fw = open(playlist,"a")
  #keys = ["gameid", "gameid_num", "eventid", "prd", "msg_type", "action_type", "vtms", "htms", "tm", "game_clock", "player_code", "play"]
  #fw.write(delim.join(keys) + "\n")
  for game in games:
    game = game.split("\n")[0].split(delim)
    gameid = game[1]
    print gameid # debug
    date = gameid[:8]
    teams = game[2:4]
    seasonyear = str(int(date[0:4]) - (int(date[4:6])<8)) # new year's games are part of prev season until october
    #url = "http://www.nba.com/games/game_component/dynamic/" + date + "/" + teams + "/pbp_all.xml"
    url = "http://data.nba.com/data/10s/html/nbacom/" + seasonyear + "/gameinfo/" + date + "/" + game[0] + "_playbyplay_csi.html"
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    events = soup.find_all("table")[0].find_all("tr")
    # reset count, score, prd
    htms = 0
    vtms = 0
    prd = 0
    count=1
    for e in events:
      action_type = 0
      msg_type = 0
      dat = e.find_all("td")
      # switch to handle whether dat is length 1 (jump ball / start & stop quarter)
      # length 2 (do nothing) or length 3 & if length 3 (game event)
      # length 3 requires most work
      if len(dat)==1:
        # either...
        # jump ball (msg_type = 10) 
        # period start (msg_type = 12) -> update prd
        # period stop (msg_type = 13)
        play = dat[0].text.strip() # remove junk at end of line
        tm = ''
        # which msg_type?
        if re.search("[Jj]ump [Bb]all", play):
          msg_type = 10
          game_time = re.match("\((.+)\)", play).groups()[0]
        if re.search("[Ss]tart of", play):
          play = play.replace("Back to Top","") # text that appears @ quarter start
          msg_type = 12
          prd+=1
          if re.search("[Qq]uarter", play):
            game_time = "12:00"
          else:
            game_time = "5:00"
        if re.search("[Ee]nd of", play):
          game_time = "00:00.0"
          msg_type = 13
        I = [gameid, game[0], str(count), str(prd), str(msg_type), str(action_type), tm, str(vtms), str(htms), game_time, 'player_code', play]
        #print play # debug
        fw.write(delim.join(I) + "\n")
      if len(dat)==2:
        # do nothing because table entries are just team names
        []
      if len(dat)==3:
        # decide which team is affected
        if len(dat[0].text)==1:
          tm = teams[1]
          j=2
        else:
          #if len(dat[2].text)==1:  #do nothing because no play listed
          #  continue
          #else:
          tm = teams[0]
          j=0
        # tm = away, j=1 ; tm = home, j=3      
        play = dat[j].text.strip()
        # is it a scoring play?
        if dat[1].attrs['class'][0]=="nbaGIPbPMidScore":
          temp = dat[1].text.split("[")[1].split("]")[0] # drop [ ] border
          leadteam = temp[0:3]
          scr = temp.strip(leadteam + " ").split("-")
          if leadteam==teams[0]:
            vtms = int(scr[0])
            htms = int(scr[1])
          if leadteam==teams[1]:
            vtms = int(scr[1])
            htms = int(scr[0])        
        # find message type
        msg_type = 0
        if re.search("[Ss]hot: [Mm]ade", play):
          msg_type = 1
        if re.search("[Ss]hot: [Mm]issed", play):
          msg_type = 2
        if re.search("[Ff]ree [Tt]hrow", play):
          msg_type = 3
        if re.search("[Rr]ebound", play):
          msg_type = 4
        if re.search("[Tt]urnover", play):
          msg_type = 5
        if re.search("[Ff]oul", play):
          msg_type = 6
        #if re.search("[kicked ball or goaltend or delay of game]", play):
        #  msg_type = 7
        if re.search("[Ss]ubstitution", play):
          msg_type = 8
        if re.search("[Tt]imeout", play):
          msg_type = 9
        if re.search("[Jj]ump [Bb]all", play):
          msg_type = 10
        if re.search("[Ee]jection", play):
          msg_type = 11
        if re.search("[Ii]nstant [Rr]eplay", play):
          msg_type = 18
        game_time = dat[1].text.split(" ")[0]
        I = [gameid, game[0], str(count), str(prd), str(msg_type), str(action_type), tm, str(vtms), str(htms), game_time, 'player_code', play]
        #print play # debug
        fw.write(delim.join(I) + "\n")
        count+=1
  fw.close()

def main():
  # set names of data files:
  #season_code = sys.argv[1]
  season_code = '00214' # 2014-15 regular season
  gamelist_full = "games_" + season_code + ".csv"
  gamelist_new = "games_latest_" + season_code + ".csv"
  boxscorelist = "scores_" + season_code + ".csv"
  scorelist = "scorelines_" + season_code + ".csv"
  playlist = "plays_" + season_code + ".csv"
  # update game list, box scores, play-by-play with newest data  
  print "\n\nGetting latest games..."  
  latestGamelist(season_code, gamelist_full)
  print "\n\nWriting team box scores..."  
  writeTeamTotals(gamelist_new, scorelist)
  print "\n\nWriting player box scores..."    
  writescoresCSV(gamelist_new, boxscorelist)
  print "\n\nWriting play-by-play..."  
  writeplaysCSV(gamelist_new, playlist)
  print "\n\nGetting today's lines..."  
  gamelinesToday()
  

# boilerplate to run on execution
if __name__ == "__main__":
    main()
