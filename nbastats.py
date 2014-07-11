import urllib2
import json
# import elementtree.ElementTree as ET
import scipy.io as spio
import numpy as np

API_KEY = "YOUR_API_KEY"
sqdl_call = "date,team,o:team,points,margin,margin after the first, margin at the half, margin after the third,biggest lead,field goals attempted, field goals made, three pointers attempted, three pointers made, free throws attempted, free throws made,points in the paint,assists,steals,blocks,offensive rebounds,defensive rebounds,turnovers"
features = sqdl_call.split(",")
# sqdl_html=sqdl_call + "@season=YYYY and game number=NNNN"
sqdl_html=sqdl_call + "@season=YYYY"
replace_table = {",":"%2C", ":":"%3A", " ":"+", "=":"%3D", "@":"%40"}
for n in replace_table:
  sqdl_html = sqdl_html.replace(n,replace_table[n])
urlroot = "http://api.sportsdatabase.com/nba/query.json?sdql=" + sqdl_html + "&output=json&api_key=" + API_KEY

def getSeason(yyyy):
  games = []
  url = urlroot.replace("YYYY", str(yyyy))
  F = urllib2.urlopen(url)
  J = F.read()    
  F.close()
  J = J.replace("json_callback(","") # removing junk text
  J = J.replace("});","}") # removing junk text
  J = J.replace("\'", "\"") # switching to double quotes throughout
  J0 = json.loads(J)
  features = J0['headers']
  data = J0['groups'][0]['columns']
  Nsamples = len(data[0])

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
  return data,features

if __name__ == "__main__":
  season = 2013
  (G,F) = getSeason(season)
  D = {"games":G, "features":F}
  spio.matlab.savemat('NBASeason' + str(season), D)
