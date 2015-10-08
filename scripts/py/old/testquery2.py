#!/usr/bin/python
# json -> pandas DataFrame -> html table
from pandas import DataFrame
import json
import urlparse
import cgi
import cgitb
cgitb.enable() # helps troubleshoot cgi

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
json_file = open(json_path + '/pbp_' + gameid + '.json','r')
j = json.loads(json_file.read())
df = DataFrame(j['rowSet'])
df.columns = j['headers']
df2 = DataFrame([df.HOMEDESCRIPTION, df.NEUTRALDESCRIPTION, df.VISITORDESCRIPTION]).T
#vs = ['HOMEDESCRIPTION','NEUTRALDESCRIPTION','VISITORDESCRIPTION']
vs2 = ['Home','','Away']
df2.columns = vs2
#df.columns = j['headers']
print df2.to_html()

print "</body></html>"