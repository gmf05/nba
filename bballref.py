import re
import datetime    
import urllib2
from bs4 import BeautifulSoup

def writeBBrefGames(season_code):
    teamAbbrevs = {'Atlanta Hawks':'ATL', 'Boston Celtics':'BOS', 'Brooklyn Nets':'BRK', 'Chicago Bulls':'CHI', 'Charlotte Hornets':'CHH', 'Charlotte Bobcats':'CHA', 'Cleveland Cavaliers':'CLE', 'Dallas Mavericks':'DAL', 'Denver Nuggets':'DEN', 'Detroit Pistons':'DET', 'Golden State Warriors':'GSW', 'Houston Rockets':'HOU', 'Indiana Pacers':'IND', 'Los Angeles Clippers':'LAC', 'Los Angeles Lakers':'LAL', 'Memphis Grizzlies':'MEM', 'Miami Heat':'MIA', 'Milwaukee Bucks':'MIL', 'Minnesota Timberwolves':'MIN', 'New Orleans Pelicans':'NOP', 'New York Knicks':'NYK', 'Oklahoma City Thunder':'OKC', 'Orlando Magic':'ORL', 'Philadelphia 76ers':'PHI', 'Phoenix Suns':'PHO', 'Portland Trail Blazers':'POR', 'Sacramento Kings':'SAC', 'San Antonio Spurs':'SAS', 'Toronto Raptors':'TOR', 'Utah Jazz':'UTA', 'Washington Wizards':'WAS', 'New Jersey Nets':'NJN', 'New Orleans Hornets':'NOH', 'Charlotte Bobcats':'CHA', 'Washington Bullets':'WSB', 'Kansas City Kings':'KCK', 'San Diego Clippers':'SDC', 'Seattle SuperSonics':'SEA', 'Vancouver Grizzlies':'VAN', 'New Orleans/Oklahoma City Hornets':'NOK'}
    fr = open("nbaseasons.csv","r")
    fr.readline() # throwaway line
    for n in range(0, 35): # jump ahead
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
    

def writeBBrefScores(season_code):
    fr = open("games_bbref_" + season_code + ".csv","r")
    fw = open("scores_bbref_" + season_code + ".csv","w")
    fr.readline() # throwaway line
    delim = ","
    #valkeys = ['fgm','fga','3pm','3pa','ftm','fta','off','def','tot','ast','st','bs','to','pf','pts]    
    #valind = [2,3,5,6,8,9,11,12,13,14,15,16,17,18,19]
    valind = [1,2,3,5,6,8,9,-1,11,12,13,14,18,15,17,16,-1,19]
    keys = ['gameid','gameid_num','away','home','tm','player_code','pos','min','fgm','fga','3pm','3pa','ftm','fta','+/-','off','def','tot','ast','pf','st','to','bs','ba','pts']
    fw.write(delim.join(keys) + "\n")
    for r in fr.readlines():
        r = r.strip().split(delim)    
        gameid = r[0]
        away = r[1]
        home = r[2]
        gameid0 = gameid.replace(away, '0')
        print gameid # debug
        url = "http://www.basketball-reference.com/boxscores/" + gameid0 + ".html"
        html = urllib2.urlopen(url).read()
    
        table1 = html.split("id=\"" + away + "_basic\">")[1].split("</table>")[0]
        tabrows1 = BeautifulSoup(table1).find_all('tr')
        season_year = 1900 + int(season_code[-2:])
        season_year = season_year + 100*(season_year<1950)
        if season_year >= 1985:
            I = range(2,7) + range(8, len(tabrows1)) # 7 = table headings if season >=1985
        else:
            I = range(2, len(tabrows1)) # no table headings if season < 1985
        tm = away
        for i in I:
            td = tabrows1[i].find_all('td')
            d = [gameid, '', away, home, tm]
            player_code = td[0].text.lower().replace(' ','_').replace('.','') # needs work?
            if player_code=='team_totals':
                player_code='total'
            d.append(player_code)
            d.append('') # no position data
            for v in valind:
                if v>0:
                    d.append(td[v].text)
                else:
                    d.append('')
            fw.write(delim.join(d) + "\n")
        
        table2 = html.split("id=\"" + home + "_basic\">")[1].split("</table>")[0]    
        tabrows2 = BeautifulSoup(table2).find_all('tr')
        if season_year >= 1985:
            I = range(2,7) + range(8, len(tabrows2)) # 7 = table headings if season >=1985
        else:
            I = range(2, len(tabrows2)) # no table headings if season < 1985
        tm = home
        for i in I:
            td = tabrows2[i].find_all('td')
            d = [gameid, '', away, home, tm]
            player_code = td[0].text.lower().replace(' ','_').replace('.','') # needs work?
            if player_code=='team_totals':
                player_code='total'
            d.append(player_code)
            d.append('') # no position data
            for v in valind:
                if v>0:
                    d.append(td[v].text)
                else:
                    d.append('')
            fw.write(delim.join(d) + "\n")
    fw.close()

def main():
#     I = range(79,100) + range(0,15)
    I = range(12,15)
    Is = [str(i).zfill(2) for i in I]
    for i in Is:
        season_code = "002" + i
        writeBBrefScores(season_code)
        
if __name__ == "__main__":
    main()
