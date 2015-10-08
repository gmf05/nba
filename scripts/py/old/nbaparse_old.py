#!/usr/bin/python
#
#import sys # to read in command line arguments
import re # regular expressions
import datetime # handling date objects
import urllib2 # query web
import shutil # query web (.cfm)
from bs4 import BeautifulSoup # parse html tags

# global variables
delim = ','
gamefile = 'games_bbref_00214.csv'
playfile = 'plays_test.csv'

def getPlays(gamefile, playfile):
    fr = open(gamefile, "r")
    fw = open(playfile, "w")
    fr.readline() # drop headers
    keys = ["gameid", "season", "eventid", "prd", "msg_type", "action_type", "vtms", "htms", "tm", "game_clock", "player_code", "play"]
    fw.write(delim.join(keys) + "\n")
    for l in fr.readlines():
        gameid,season_year,away,home = l.strip().split(delim)
        season_year = int(season_year)
        print gameid # debug
        date = gameid[0:8]
        #season_year = int(date[0:4]) - (int(date[4:6]) <= 8)
        url = 'http://www.nba.com/games/' + date + '/' + ''.join([away,home])
        if season_year<=2008:
            url = url + '/playbyplay.html'
        else:
            url = url + '/gameinfo.html'
        html = urllib2.urlopen(url).read().replace('\n','').replace('\t','')
        tab = html[re.search('<div id="nbaGIP[Bb]P">', html).start() ::].split('<table')[1].split('</table')[0]
        soup = BeautifulSoup(tab)
        events = soup.find_all("tr")
        # reset count, score, prd
        htms = 0
        vtms = 0
        prd = 0
        count=1
        for e in events[1:]: # drop first row = team headers
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
              game_time = re.match("\((.*?)\)", play).groups()[0]
              play = play.replace('(' + game_time + ') ', '')
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
            play.replace(',',';')
            I = [gameid, str(season_year), str(count), str(prd), str(msg_type), str(action_type), tm, str(vtms), str(htms), game_time, 'player_code', play]
            #print play # debug
            fw.write(delim.join(I) + "\n")
          if len(dat)==2:
            # do nothing because table entries are just team names
            []
          if len(dat)==3:
            # decide which team is affected
            if len(dat[0].text)==1 and len(dat[2].text)==1: # no text for either team
              continue
            elif len(dat[2].text)>1:
              tm = home
              j=2
            else: # text for away team
              tm = away
              j=0
            # tm = away, j=1 ; tm = home, j=3      
            play = dat[j].text.strip().replace(',',';')
            # is it a scoring play?
            if dat[1].attrs['class'][0]=="nbaGIPbPMidScore":
              temp = dat[1].text.split("[")[1].split("]")[0] # drop [ ] border
              leadteam = temp[0:3]
              scr = temp.strip(leadteam + " ").split("-")
              if leadteam==away:
                vtms = int(scr[0])
                htms = int(scr[1])
              if leadteam==home:
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
            I = [gameid, str(season_year), str(count), str(prd), str(msg_type), str(action_type), tm, str(vtms), str(htms), game_time, 'player_code', play]
            #print play # debug
            fw.write(delim.join(I) + "\n")
            count+=1
    fw.close()

def main():
  getPlays("games_nba_all.csv", "plays_test.csv")    

# boilerplate to run on execution
if __name__ == "__main__":
    main()


#    
## concatenate game lists & add seasons
#delim = ','
#fw = open('games_nba_all.csv', 'w')
#keys = ['gameid', 'season', 'away', 'home']
#fw.write(delim.join(keys) + '\n')
#for season_year in range(5,15):
#    season_code = '002' + str(season_year).zfill(2)
#    fr = open('games_bbref_' + season_code + '.csv', 'r')
#    fr.readline()
#    for r in fr.readlines():
#        r = r.replace('PHO','PHX').replace('BRK','BKN').replace('CHH','CHA').strip().split(delim)
#        r.insert(1, str(2000+season_year))
#        fw.write(delim.join(r) + '\n')
#fw.close()