import sys
import csv
import json
import urllib2
import scipy.io as spio
import numpy 

sqdl_features = "date,team,o:team,points,margin,margin after the first,margin at the half,margin after the third,biggest lead,field goals attempted,field goals made,three pointers attempted,three pointers made,free throws attempted,free throws made,points in the paint,assists,steals,blocks,offensive rebounds,defensive rebounds,turnovers"
features = sqdl_features.split(",")
urlroot = "http://api.sportsdatabase.com/nba/query.json?sdql=SQDL&output=json&api_key=YOUR_API_KEY"

def sqdlHTML(sqdl):
  replace_table = {",":"%2C", ":":"%3A", " ":"+", "=":"%3D", "@":"%40"}
  html = sqdl
  for n in replace_table:
    html = html.replace(n,replace_table[n])
  return html

def getSeason(yyyy):
  sqdl_html = sqdlHTML(sqdl_features + "@season=" + str(yyyy))
  url = urlroot.replace("SQDL",sqdl_html)
  FR = urllib2.urlopen(url)
  J = FR.read()    
  FR.close()
  J = J.replace("json_callback(","") # removing junk text
  J = J.replace("});","}") # removing junk text
  J = J.replace("\'", "\"") # switching to double quotes throughout
  J0 = json.loads(J)
  data = J0['groups'][0]['columns']
  data =  numpy.asarray(data).T.tolist()
  return data

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

if __name__ == "__main__":
  yyyy = sys.argv[1]
#   csvSeason(yyyy) # works
#   xlsSeason(yyyy) # doesn't work
  matSeason(yyyy) # doesn't work
