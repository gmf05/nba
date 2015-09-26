#!/usr/bin/python
# pulling nba play-by-play via xml to json
#
#
import sys
import re
import urllib2
from bs4 import BeautifulSoup # for parsing html
#import json
#import xmltodict

def writeplaysCSV(gamelist, playlist):
  delim = ","
  fr = open(gamelist,"r") 
  fr.readline() # first line is data names
  games = fr.readlines()
  fw = open(playlist,"w")
  keys = ["gameid", "gameid_num", "eventid", "prd", "msg_type", "action_type", "vtms", "htms", "tm", "game_clock", "player_code", "play"]
  fw.write(delim.join(keys) + "\n")
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
        play = dat[0].text.strip()
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
        play = dat[j].text  
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

def main():
    season_code = "00213" # 2013-14 regular season
    #season_code = "00214" # 2014-15 regular season
    gamelist = "games_" + season_code + ".csv"
    playlist = "plays_" + season_code + ".csv"
    writeplaysCSV(gamelist, playlist)

# boilerplate to run on execution
if __name__ == "__main__":
    main()
