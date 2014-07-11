import urllib2
import json
import elementtree.ElementTree as ET
import scipy.io as spio
import numpy as np

urlroot = "http://api.sportsdatabase.com/nba/query.json?sdql="
API_KEY = "YOUR_API_KEY"
teams = ["Bobcats", "Bucks", "Bulls", "Cavaliers", "Celtics", "Clippers", "Grizzlies", "Hawks", "Heat", "Pelicans", "Jazz", "Kings", "Knicks", "Lakers", "Magic", "Mavericks", "Nets", "Nuggets", "Pacers", "Pistons", "Raptors", "Rockets", "Seventysixers", "Spurs", "Suns", "Supersonics", "Thunder", "Timberwolves", "Trailblazers", "Warriors", "Wizards"]

def getSeason(yyyy):
  sdql = "season=" + str(yyyy)  
  stats = []
  
  for team in teams:
    print team 
    url = urlroot + team + ":" + sdql.replace("=","%3D") + "&output=json&api_key=" + API_KEY
    try:
      f = urllib2.urlopen(url)
      jsonp = f.read()
      jsonp = jsonp.replace("json_callback(","")
      jsonp = jsonp.replace("});","")
      f.close()
#       json_parsed = json.loads(json_str)
#       for game_str in json_parsed.get('games', []):
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

#     get list of games
#     from each game, get features of interest
      wins = 1
      pts = 100
      stats.append({
        'Win': wins, 
        'Points': pts
        })
    except Exception, e:
      print e
  
  return stats 

if __name__ == "__main__":
  season = 2013
  S = getSeason(season)
  D = {"stats": S, "teams", teams}
  spio.matlab.savemat('NBASeason' + str(season), D)
