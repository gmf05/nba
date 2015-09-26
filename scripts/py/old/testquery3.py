#!/usr/bin/python
# json -> pandas DataFrame -> html table
from pandas import DataFrame
import json
import urlparse
import cgi
import cgitb
cgitb.enable() # helps troubleshoot cgi
import matplotlib
import matplotlib.pyplot as plt, mpld3 # plotting

# HTML header
print "Content-Type: text/html\n"
print """
<html><head><title>Query NBA Play-by-Play</title></head>
<body>
"""

# Get user query:
testurl = 'http://neurocoding.info/cgibin/testquery.py?s=00214&g=30&z=3'
form = cgi.FieldStorage()
print """
 <form method="post" action="index.cgi">
 <p>Season: <input type="text" name="season_code"/></p>
 <p>Game: <input type="text" name="gamenum"/></p>
 <p> <input type="submit" value="Submit"/> </p>
 </form>
"""
season_code = form.getvalue("season_code","00214")
gamenum = form.getvalue("gamenum","1").zfill(5)
gameid = season_code + gamenum
#print gameid
query = urlparse.parse_qs(urlparse.urlparse(testurl).query)

# Load appropriate JSON file, print to HTML table
json_path = '/var/www/data/json'
#json_path = '../json'
#json_file = open(json_path + '/pbp_' + query['s'][0] + str(query['g'][0]).zfill(5) + '.json','r')
json_file = open(json_path + '/shots_' + gameid + '.json','r')
j = json.loads(json_file.read())
df = DataFrame(j['rowSet'])
df.columns = j['headers']
#df2 = DataFrame([df.LOC_X, df.LOC_Y, df.SHOT_DISTANCE, df.SHOT_TYPE, df.SHOT_MADE_FLAG])
#df2 = DataFrame([df.LOC_X, df.LOC_Y])
#xs,ys,made = df.LOC_X,df.LOC_Y,df.SHOT_MADE_FLAG
xs,ys,made = df.LOC_X[0:10],df.LOC_Y[0:10],df.SHOT_MADE_FLAG[0:10]

for i in range(0,len(xs)):
  if made[i]:
    plt.text(xs[i],ys[i], 'o')
  else:
    plt.text(xs[i],ys[i], 'x')
plt.show()
mpld3.show()

print "</body></html>"