#!/usr/bin/python
#%%
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 21:23:30 2015

Simple Python script to get Vegas money lines for a list of NBA games

@author: Grant Fiddyment  <neurocoding05@gmail.com>
"""
import re # parse text using regular expressions
import shutil 
import urllib2 # TO DO: SWITCH TO REQUESTS MODULE
#import requests # query web

# Where should the output files be saved?
NBAPATH = '/home/gmf/' # <<<< CHANGE THIS FOR YOUR SYSTEM!!
delim = ','

#season_code = '00299' # 1999 regular season
season_code = '00214' # 2014 regular season
#season_code = '00414' # 2014 playoffs

# Open game list
fr = open(NBAPATH + 'games_' + season_code + '.csv','r')
fr.readline() # drop headers
fw = open(NBAPATH + 'vegaslines_' + season_code + '.csv', 'w')

# Function to, given an NBA game, get final money line from vegasinsider.com 
def getLine(gameid):   
  # dictionary of name conventions used on the site
  # NOTE: multiple team codes are NOT the standard ones used by the NBA
  # e.g. UTA = UTH, BKN = NJN, PHX = PHO, NOP = NOR
  teamNames = {'ATL': 'hawks', 'BOS':'celtics', 'BKN':'nets', 'CHA':'hornets','CHI':'bulls','CLE':'cavaliers','DAL':'mavericks','DEN':'nuggets','DET':'pistons','GSW':'warriors','HOU':'rockets','IND':'pacers','LAC':'clippers','LAL':'lakers','MEM':'grizzlies','MIA':'heat','MIL':'bucks','MIN':'timberwolves','NOP':'pelicans','NYK':'knicks','OKC':'thunder','ORL':'magic','PHI':'76ers','PHX':'suns','POR':'trail-blazers','SAC':'kings','SAS':'spurs','TOR':'raptors','UTA':'jazz','WAS':'wizards'}  
  teamAbbrevVI = {'ATL': 'ATL', 'BOS':'BOS', 'BKN':'NJN', 'CHA':'CHA','CHI':'CHI','CLE':'CLE','DAL':'DAL','DEN':'DEN','DET':'DET','GSW':'GSW','HOU':'HOU','IND':'IND','LAC':'LAC','LAL':'LAL','MEM':'MEM','MIA':'MIA','MIL':'MIL','MIN':'MIN','NOP':'NOR','NYK':'NYK','OKC':'OKC','ORL':'ORL','PHI':'PHI','PHX':'PHO','POR':'POR','SAC':'SAC','SAS':'SAS','TOR':'TOR','UTA':'UTH','WAS':'WAS'}
  date = '-'.join([gameid[4:6], gameid[6:8], gameid[2:4]])
  url = u'http://www.vegasinsider.com/nba/odds/las-vegas/line-movement/' + teamNames[gameid[8:11]] + '-@-' + teamNames[gameid[11:14]] + '.cfm/date/' + date
  # spoof an alternate user-agent: works for vegasinsider
  # courtesy of stackoverflow
  request = urllib2.Request(url, headers={'User-Agent':'Mozilla'})
  response = urllib2.urlopen(request)
  with open('tempout.txt', 'wb') as outfile:
    shutil.copyfileobj(response, outfile)
  html = open('tempout.txt', 'rb').read()
  # pseudocode:
  # Jump to VI CONSENSUS LINE MOVEMENTS
  # Jump to end of table (header for VI)
  # Get following <TABLE> of lines
  # Start at last row of this table and work backwards until a moneyline is extracted
  txt = html[re.search('VI CONSENSUS LINE MOVEMENTS',html).start():]  
  txt = txt[re.search('</TABLE>',txt).end():] # get following table (1)
  txt = txt[0:re.search('</TABLE>',txt).end():] # get following table (2)
  txt = txt.split('<TR>') # break up table rows
  gotLine = False
  maxRows = round(0.5*len(txt))
  maxRows = len(txt)
  trind = -1
  while not gotLine and abs(trind)<maxRows:
    try:  
      txt0 = txt[trind].split('</TD>')
      txt1 = txt0[2][re.search('<TD.*>',txt0[2]).end():].strip()
      txt2 = txt0[3][re.search('<TD.*>',txt0[3]).end():].strip()
      if re.search(teamAbbrevVI[gameid[8:11]], txt1): # if away team is favorite
        l1 = int(re.search('([+-][\d]+)', txt1).groups()[0])
        try:
          l2 = int(re.search('([+-][\d]+)', txt2).groups()[0])
        except: # handles case when money line = 0 bc there is no +/-
          l2 = int(re.search('([\d]+)', txt2).groups()[0])
      else: # if home team is favorite
        try:    
          l1 = int(re.search('([+-][\d]+)', txt2).groups()[0])
        except: # handles case when money line = 0 bc there is no +/-
          l1 = int(re.search('([\d]+)', txt2).groups()[0])
        l2 = int(re.search('([+-][\d]+)', txt1).groups()[0])
      gotLine = True
    except: # if this parsing fails, go back a row     
      trind -= 1
  if not gotLine:
    l1 = ''
    l2 = ''
  return [l1, l2]
  
# TO DO: Simplify getLine above ...
def getLine2(gameid):   
  # dictionary of name conventions used on the site
  # NOTE: multiple team codes are NOT the standard ones used by the NBA
  # e.g. UTA = UTH, BKN = NJN, PHX = PHO, NOP = NOR
  teamNames = {'ATL': 'hawks', 'BOS':'celtics', 'BKN':'nets', 'CHA':'hornets','CHI':'bulls','CLE':'cavaliers','DAL':'mavericks','DEN':'nuggets','DET':'pistons','GSW':'warriors','HOU':'rockets','IND':'pacers','LAC':'clippers','LAL':'lakers','MEM':'grizzlies','MIA':'heat','MIL':'bucks','MIN':'timberwolves','NOP':'pelicans','NYK':'knicks','OKC':'thunder','ORL':'magic','PHI':'76ers','PHX':'suns','POR':'trail-blazers','SAC':'kings','SAS':'spurs','TOR':'raptors','UTA':'jazz','WAS':'wizards'}  
  teamAbbrevVI = {'ATL': 'ATL', 'BOS':'BOS', 'BKN':'NJN', 'CHA':'CHA','CHI':'CHI','CLE':'CLE','DAL':'DAL','DEN':'DEN','DET':'DET','GSW':'GSW','HOU':'HOU','IND':'IND','LAC':'LAC','LAL':'LAL','MEM':'MEM','MIA':'MIA','MIL':'MIL','MIN':'MIN','NOP':'NOR','NYK':'NYK','OKC':'OKC','ORL':'ORL','PHI':'PHI','PHX':'PHO','POR':'POR','SAC':'SAC','SAS':'SAS','TOR':'TOR','UTA':'UTH','WAS':'WAS'}
  date = '-'.join([gameid[4:6], gameid[6:8], gameid[2:4]])
  url = u'http://www.vegasinsider.com/nba/odds/las-vegas/line-movement/' + teamNames[gameid[8:11]] + '-@-' + teamNames[gameid[11:14]] + '.cfm/date/' + date
  # spoof an alternate user-agent: works for vegasinsider
  # courtesy of stackoverflow
  request = urllib2.Request(url, headers= {'User-Agent':'Mozilla'})
  response = urllib2.urlopen(request)
  with open('tempout.txt', 'wb') as outfile:
    shutil.copyfileobj(response, outfile)
  html = open('tempout.txt', 'rb').read()
  # pseudocode:
  # Jump to VI CONSENSUS LINE MOVEMENTS
  # Jump to end of table (header for VI)
  # Get following <TABLE> of lines
  # Start at last row of this table and work backwards until a moneyline is extracted
  txt = html[re.search('VI CONSENSUS LINE MOVEMENTS',html).start():]  
  txt = txt[re.search('</TABLE>',txt).end():] # get following table (1)
  txt = txt[0:re.search('</TABLE>',txt).end():] # get following table (2)
  txt = txt.split('<TR>') # break up table rows
  gotLine = False
  maxRows = round(0.5*len(txt))
  maxRows = len(txt)
  trind = -1
  while not gotLine and abs(trind)<maxRows:
    try:  
      txt0 = txt[trind].split('</TD>')
      txt1 = txt0[2][re.search('<TD.*>',txt0[2]).end():].strip()
      txt2 = txt0[3][re.search('<TD.*>',txt0[3]).end():].strip()
      if re.search(teamAbbrevVI[gameid[8:11]], txt1): # if away team is favorite
        l1 = int(re.search('([+-][\d]+)', txt1).groups()[0])
        try:
          l2 = int(re.search('([+-][\d]+)', txt2).groups()[0])
        except: # handles case when money line = 0 bc there is no +/-
          l2 = int(re.search('([\d]+)', txt2).groups()[0])
      else: # if home team is favorite
        try:    
          l1 = int(re.search('([+-][\d]+)', txt2).groups()[0])
        except: # handles case when money line = 0 bc there is no +/-
          l1 = int(re.search('([\d]+)', txt2).groups()[0])
        l2 = int(re.search('([+-][\d]+)', txt1).groups()[0])
      gotLine = True
    except: # if this parsing fails, go back a row     
      trind -= 1
  if not gotLine:
    l1 = ''
    l2 = ''
  return [l1, l2]
  
# Loop over games, get odds
fw.write(delim.join(['gameid','away','home','line_away','line_home']) + '\n')
for r in fr.readlines():
  junk,gameid_simple,away,home = r.split(delim)
  print gameid_simple # debug
  try:
    l1,l2 = getLine(gameid_simple)
    print l1,l2 # debug
    fw.write(delim.join([gameid_simple, away, home, str(l1), str(l2)]) + '\n')
  except:
    print 'Encountered error on %s' % gameid_simple
fw.close()