import sys
import csv
import json
import urllib2
import scipy.io as spio
import numpy 

team_features = "date,team,o:team,points,margin,margin after the first,margin at the half,margin after the third,biggest lead,field goals attempted,field goals made,three pointers attempted,three pointers made,free throws attempted,free throws made,points in the paint,assists,steals,blocks,offensive rebounds,defensive rebounds,turnovers"
player_features="o:team,assists,blocks,defensive rebounds,field goals attempted,field goals made,fouls,free throws attempted,free throws made,minutes,offensive rebounds,points,rebounds,steals,three pointers attempted,three pointers made,turnovers"
urlroot = "http://api.sportsdatabase.com/nba/query.json?sdql=SQDL&output=json&api_key=YOUR_API_KEY"

def formatSQDL(sqdl):
  replace_table = {",":"%2C", ":":"%3A", " ":"+", "=":"%3D", "@":"%40"}
  html = sqdl
  for n in replace_table:
    html = html.replace(n,replace_table[n])
  return html

def formatJSONP(jsonp):
  J = jsonp.replace("json_callback(","").replace("});","}") # remove padding
  J = J.replace("\'", "\"") # switching to double quotes throughout
  J = json.loads(J)
  J = J['groups'][0]['columns']
  J =  numpy.asarray(J).T.tolist()
  # remove unplayed games (needs to be itereated for some reason...)
  for n in range(2):
    for j in J:
      if not any(j[3::]):
        print j
        J.remove(j)
  return J

def getSeason(yyyy):
  features = team_features.split(",")
  sqdl_html = formatSQDL(team_features + "@season=" + str(yyyy))
  url = urlroot.replace("SQDL",sqdl_html)
  F = urllib2.urlopen(url)
  data = formatJSONP(F.read())
  F.close()
  return data,features

def getPlayerSeason(player, team, yyyy):
  pf = "date," + player_features.replace(",", "," + player + ":")  
  sqdl_html = formatSQDL(pf + "@" + team + ":season=" + str(yyyy))
  sqdl_call = pf + "@" + team + ":season=" + str(yyyy)
  url = urlroot.replace("SQDL",sqdl_html)
  F = urllib2.urlopen(url)
  data = formatJSONP(F.read())
  F.close()
  # save to .mat file
  features = pf.replace(player + ":","").split(",") 
  stats =  numpy.asarray(data,dtype=numpy.object)
  D = {"stats":stats, "features":features}
  matfile = player.replace(" ","-") + "-" + str(yyyy) + ".mat"
  spio.matlab.savemat(matfile, D)
#   return data,features

def csvSeason(yyyy):
  games = getSeason(yyyy)
  with open('NBASeason' + str(yyyy) + '.csv','w') as csvfile:
    csvWriter = csv.writer(csvfile)
    csvWriter.writerow(features)
    for g in games:
      csvWriter.writerow(g)
    csvfile.close()

def matSeason(yyyy):
  games =  numpy.asarray(getSeason(yyyy),dtype=numpy.object)
  D = {"games":games, "features":features}
  spio.matlab.savemat('NBASeason' + str(yyyy) + '.mat', D)

def xlsSeason(yyyy):
  games = getSeason(yyyy)
  with open('NBASeason' + str(yyyy) + '.xls','w') as csvfile:
    csvWriter = csv.writer(csvfile,dialect=csv.excel_tab)
    csvWriter.writerow(features)
    for g in games:
      csvWriter.writerow(g)
    csvfile.close()

def main():
  yyyy = sys.argv[1]
#   csvSeason(sys.argv[1]) # works
#   xlsSeason(sys.argv[1]) # doesn't work
#   matSeason(sys.argv[1]) # works
  getPlayerSeason(sys.argv)

if __name__ == "__main__":
  main()
