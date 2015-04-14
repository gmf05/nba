from bs4 import BeautifulSoup
import urllib2

def writeBBref(season_code):
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
        writeBBref(season_code)
        
if __name__ == "__main__":
    main()
