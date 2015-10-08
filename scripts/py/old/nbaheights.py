#!/usr/bin/python
import re
import urllib2
import sqlite3
#db_path = '/var/www/data/db'
db_path = '../sql'
conn = sqlite3.connect(db_path + '/nba.db')
c = conn.cursor()
c.execute("select distinct player from Scores where player!='total';")
players = c.fetchall()[1:]
conn.close() # close SQLite connection
fw = open("../player_heights.csv","w")
for p in players:
  print p[0]
  names = p[0].split('_')  
  if len(names)==2:
    firstnm,lastnm = names
  else:
    firstnm,middlenm,lastnm = names
  playerid = lastnm[0:5] + firstnm[0:2] + '01'
  url = 'http://www.basketball-reference.com/players/' + lastnm[0] + '/' + playerid + '.html'
  html = urllib2.urlopen(url).read()
  ht = html.split('Height:</span>')[1].split('<')[0]
  feet,inches = re.search('(\d)-(\d+)',ht).groups()
  totinches = 12*int(feet) + int(inches)
  fw.write(','.join([p[0], playerid, str(totinches)]) + '\n')
fw.close()