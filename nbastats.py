import urllib2
import json
# import elementtree.ElementTree as ET
import scipy.io as spio
import numpy as np

API_KEY = "YOUR_API_KEY"
features=["date", "team", "o:team"]
sqdl="date,team,o:team,points,margin,margin after the first, margin at the half, margin after the third,biggest lead,field goals attempted, field goals made, three pointers attempted, three pointers made, free throws attempted, free throws made,points in the paint,assists,steals,blocks,offensive rebounds,defensive rebounds,turnovers@season=YYYY and game number=NNNN"
# sqdl = "date,team,o:team@season=YYYY and game number=NNNN" # simple features


sqdl_html = sqdl.replace(",","%2C").replace(":", "%3A").replace(" ", "+").replace("=","%3D").replace("@","%40")
# urlroot = "http://api.sportsdatabase.com/nba/query.json?sdql=date%2Cteam%2Co%3Ateam%40season%3DYYYY+and+game+number%3DNNNN&output=json&api_key=" + API_KEY
urlroot = "http://api.sportsdatabase.com/nba/query.json?sdql=" + sqdl_html + "&output=json&api_key=" + API_KEY

def getSeason(yyyy):
  games = []
  urlroot = urlroot.replace("YYYY", str(yyyy))
  for g in range(3):      
    url = urlroot.replace("NNNN", str(g)) 
    F = urllib2.urlopen(url)
    J = F.read()    
    F.close()
    J = J.replace("json_callback(","") # removing junk text
    J = J.replace("});","}") # removing junk text
    J = J.replace("\'", "\"") # switching to double quotes throughout
    J0 = json.loads(J)
    features = J0['headers']
    data = J0['groups'][0]['columns']
    games.append(data)

#     N = len(data[0])
#     # loop over each game, add data to list
#         game_tree = ET.XML(game_str)
#       
#      games.append({
#       'league': league,
#       'start': start,
#        'home': home,
#        'away': away,
#        'home-score': home_tree.get('score'),
#        'away-score': visiting_tree.get('score'),
#        'status': gamestate_tree.get('status'),
#        'clock': gamestate_tree.get('display_status1'),
#        'clock-section': gamestate_tree.get('display_status2')
#      })
      # for loop:
#       games.append({
#         'Win': wins, 
#         'Points': pts
#         })
  return games,features

if __name__ == "__main__":
  season = 2013
  G = getSeason(season)
  D = {"games": G}
  spio.matlab.savemat('NBASeason' + str(season), D)
