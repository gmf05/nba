#!/usr/bin/python
import json
import pymongo
from pymongo import MongoClient

gameid = '0021400001'
#gameid = '0021400008'
#gameid = '0041400104' # PLAYOFFS GAME 1
JSONPATH = '/home/gmf/Code/repos/nba/json'
json_file = JSONPATH + '/pbp_' + gameid + '.json'
pbp = json.loads(open(json_file,'r').read())['rowSet']
json_file = JSONPATH + '/bs_' + gameid + '.json'
bs = json.loads(open(json_file,'r').read())

client = MongoClient()
db = client.nba
for i in db.nba.find():
  print i
  
db.nba.insert(json.dumps(pbp))

for p in pbp:
  db.nba.insert(json.dumps(p))
  
