# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 10:48:26 2015

@author: gmf
"""
import requests
import json
import re
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# PATHS : Change these for your system
DATAHOME = '/media/gmf/GMF/unsynced/nba/data' # where to save data
#DATAHOME = '/media/ext/GMF/Data/nba' # where to save data
REPOHOME = '/home/gmf/Code/git/nba' # where are scripts
        
current_year = '2015' # 2015-16 season
default_season = current_year + '-10' 
user_agent = {'User-agent': 'Mozilla/5.0'}

stats_query_names = ['boxscoreadvanced','boxscoreadvancedv2',
'boxscorefourfactors','boxscorefourfactorsv2','boxscoremisc',
'boxscoreplayertrackv2','boxscorescoring','boxscoretraditionalv2',
'boxscoreusage','boxscoreusagev2','commonallplayers',
'commonplayerinfo','commonteamroster','commonTeamYears',
'commonplayoffseries','draftcombinedrillresults',
'draftcombinenonstationaryshooting','draftcombineplayeranthro',
'draftcombinespotshooting','draftcombinestats','drafthistory',
'franchisehistory','homepageleaders','homepagev2',
'leagueleaders','playbyplay','playbyplayv2','playercareerstats',
'playergamelog','playerprofile','playerprofilev2',
'shotchartdetail','shotchartlineupdetail','teamgamelog',
'teaminfocommon','teamplayeronoffdetails','teamplayeronoffsummary','teamvsplayer',
'teamyearbyyearstats','videoStatus','videodetails','videoevents']

# Add elbow touch, post touch, paint touch??
sportvu_query_names = ['drives','defense','catchShoot','speed',
'shooting','rebounding','pullUpShoot','touches','passing',
'drivesTeam','defenseTeam','drivesTeam','defenseTeam',
'catchShootTeam','speedTeam','shootingTeam','reboundingTeam',
'pullUpShootTeam','touchesTeam','passingTeam']

# ADD PUTBACKS??? Add summary??
synergy_query_names = ['team_Transition','team_Cut',
'team_PRBallHandler','team_Handoff','team_Isolation',
'team_Misc','team_Postup','team_PRRollMan',
'team_Spotup','team_OffRebound','team_OffScreen',
'player_Transition','player_Cut','player_PRBallHandler',
'player_Handoff','player_Isolation','player_Misc',
'player_Postup','player_PRRollMan','player_Spotup',
'player_OffRebound','player_OffScreen']

combine_query_names =  ['drillresults', 'nonstationaryshooting', 
'playeranthro', 'spotshooting', 'stats']

stats_params = {
  'LeagueID':'00', # format: d{2}
  'SeasonID':'00215',
  'Season':0, # format: d{4}-d{2}
  'SeasonYear':'2015-10', # d{4}-d{2}
  'SeasonType':'Regular Season', # format: (Regular Season)|(Pre Season)|(Playoffs)
  'GameID':0, 
  'GameEventID':0, # format: 
  'StartPeriod':1, # format: 1-10
  'EndPeriod':10, # format: 1-10
  'StartRange':0,
  'EndRange':0,
  'RangeType':0,
  'AheadBehind':'', # format: (Ahead or Behind)|(Behind or Tied)|(Ahead or Tied)
  'ClutchTime':'', # format: (Last 5 Minutes)|(Last 4 Minutes)|(Last 3 Minutes)|(Last 2 Minutes)|(Last 1 Minute)|(Last 30 Seconds)|(Last 10 Seconds)
  'ContextFilter':'', # format: 
  'ContextMeasure':'FGA', # format: (FGM)|(FGA)|(FG_PCT)|(FG3M)|(FG3A)|(FG3_PCT)|(FTM)|(FTA)|(OREB)|(DREB)|(AST)|(FGM_AST)|(FG3_AST)|(STL)|(BLK)|(BLKA)|(TOV)|(POSS_END_FT)|(PTS_PAINT)|(PTS_FB)|(PTS_OFF_TOV)|(PTS_2ND_CHANCE)|(REB)|(TM_FGM)|(TM_FGA)|(TM_FG3M)|(TM_FG3A)|(TM_FTM)|(TM_FTA)|(TM_OREB)|(TM_DREB)|(TM_REB)|(TM_TEAM_REB)|(TM_AST)|(TM_STL)|(TM_BLK)|(TM_BLKA)|(TM_TOV)|(TM_TEAM_TOV)|(TM_PF)|(TM_PFD)|(TM_PTS)|(TM_PTS_PAINT)|(TM_PTS_FB)|(TM_PTS_OFF_TOV)|(TM_PTS_2ND_CHANCE)|(TM_FGM_AST)|(TM_FG3_AST)|(TM_POSS_END_FT)|(OPP_FTM)|(OPP_FTA)|(OPP_OREB)|(OPP_DREB)|(OPP_REB)|(OPP_TEAM_REB)|(OPP_AST)|(OPP_STL)|(OPP_BLK)|(OPP_BLKA)|(OPP_TOV)|(OPP_TEAM_TOV)|(OPP_PF)|(OPP_PFD)|(OPP_PTS)|(OPP_PTS_PAINT)|(OPP_PTS_FB)|(OPP_PTS_OFF_TOV)|(OPP_PTS_2ND_CHANCE)|(OPP_FGM_AST)|(OPP_FG3_AST)|(OPP_POSS_END_FT)|(PTS))
  'DateFrom':'',  # format: YYYY-MM-DD
  'DateTo':'',  # format: YYYY-MM-DD
  'DistanceRange':'', # format: (5ft Range)|(8ft Range)|(By Zone)
  'GameDate':'', # format: YYYY-MM-DD
#  'GameScope':'', # format (1): (Season)|(Last 10)|(Yesterday)|(Finals)
  'GameScope':'', # format (2): (Season)|(Last 10)|(Yesterday)|(Finals)
  'GameSegment':'', # format: (First Half)|(Overtime)|(Second Half)
#  'GraphStartSeason':'2015-11', # format: d{4}-d{2}
#  'GraphEndSeason':'2016-01', # format: d{4}-d{2}
#  'GraphStat':'FGM', # format: 
  'GROUP_ID':0,
  'GroupQuantity':1, # format: 1-5
  'IsOnlyCurrentSeason':0, # format: 0-1
  'LastNGames':0,
  'Location':'', # format: (Home)|(Road)
  'MeasureType':'', # format: (Base)|(Advanced)|(Misc)|(Four Factors)|(Scoring)|(Opponent)|(Usage)
  'Month':0,
  'OpponentTeamID':0,
  'Outcome':'', # format: W/L
  'PaceAdjust':'N', # format: Y/N
  'Period':0,
  'PerMode':'Totals', # format: (Totals)|(PerGame)|(MinutesPer)|(Per48)|(Per40)|(Per36)|(PerMinute)|(PerPossession)|(PerPlay)|(Per100Possessions)|(Per100Plays)
  'PlayerID':0,
  'PlayerExperience':'', # format: (Rookie)|(Sophomore)|(Veteran)
  'PlayerOrTeam':'', # format: (Player)|(Team)
  'PlayerPosition':'', # format: (F)|(C)|(G)|(C-F)|(F-C)|(F-G)|(G-F)
  'PlayerScope':'All Players', # format: (All Players)|(Rookies)
  'PlayerTeamID':0,
  'PlusMinus':'Y', # format: Y/N
  'PointDiff':'', # format: 
  'Position':'',
  'Rank':'N', # format: format: Y/N
  'RookieYear':'',
  'Scope':'', # format: (RS)|(S)|(Rookies)
  'Season':'',
  'SeasonSegment':'', # format: (Post All-Star)|(Pre All-Star)
  'StarterBench':'', # format: (Starters)|(Bench)
  'StatCategory':'', # (Points)|(Rebounds)|(Assists)|(Defense)|(Clutch)|(Playmaking)|(Efficiency)|(Fast Break)|(Scoring Breakdown)    
  'TeamID':0,
  'viewShots':'true',
  'VsConference':'', #  'VsConference':'East', # format: (East)|(West)
  'VsDivision':'' # format: (Atlantic)|(Central)|(Northwest)|(Pacific)|(Southeast)|(Southwest)|(East)|(West) 
  #'zone-mode':'basic',
  }
  
# Sports Illustrated play-by-play:
si_params = {'json':1, 'sport': 'basketball/nba',
   'id':0, 'box':'false', 'pbp':'true', 'linescore':'false'}

## BEGIN HELPER FUNCTIONS
def clock2float(clock_time):
  mm,ss = clock_time.split(':')
  return int(mm) + float(ss)/60.0

def dateify(date_str, delim='-'):
  y,m,d = date_str.split(delim)
  return datetime.date(int(y),int(m),int(d))

def dict_inv(d):
  return zip2(d.values(), d.keys())

def getclosest(i, N):
  N = np.array(N)
  dist = abs(i-N)
  #return N[np.argmin(dist)]
  i=np.argmin(dist)
  return N[i],i

def nsec_elapsed(period, pctime_str):
  nmin,nsec = pctime_str.split(':')
  nmin = int(nmin)
  nsec = int(nsec)
  if period<5: # regulation : 720 sec per quarter
    pctime_sec = (11-nmin)*60 + 60 - nsec
    return (period-1)*720 + pctime_sec
  else: # overtime : 300 sec per quarter
    pctime_sec = (4-nmin)*60 + 60 - nsec
    return 2880 + (period-5)*300 + pctime_sec
  
def nsec_total(Nperiods):
  if Nperiods<4:
    print 'WARNING: Less than four periods found...'
    return np.nan
  elif Nperiods==4:
    return 2880
  else:
    return (Nperiods-4)*300 + 2880

def nsec_total_gameid(gameid):
  return nsec_total(get_pbp(gameid).iloc[-1].PERIOD)
  
def nsec_remain_qtr(p):
  nmin,nsec = str(p.PCTIMESTRING).split(':')
  return int(nmin)*60 + int(nsec)

def zip2(keys,vals):
  return dict([(keys[i], vals[i]) for i in range(len(keys))])

## END HELPER FUNCTIONS

## BEGIN PLOTTING FUNCTIONS
# Simple version. Image based
def draw_court(axis=[0,100,0,50]): 
  #fig = plt.figure(figsize=(15,7.5))
  img = mpimg.imread(REPOHOME + '/image/nba_court_T.png')
  plt.imshow(img,extent=axis, zorder=0)
  
## END PLOTTING FUNCTIONS

## BEGIN DATA GRAB FUNCTIONS
def get_gamelist_by_date(date_iso):
  games_url = 'http://data.nba.com/5s/json/cms/noseason/scoreboard/%s/games.json' % date_iso
  G = requests.get(games_url, params={}, headers=user_agent)
  try:
    return G.json()['sports_content']['games']['game']
  except:
    return []
    
def get_teams_all():  
  j = requests.get('http://stats.nba.com/stats/franchisehistory', params=stats_params, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_teams_current():  
  T = get_teams_all()
  T = T[T.END_YEAR==current_year]
  # for each (unique) team, keep its "oldest version"
  # i.e. one with earliest start year
  keep_idx = []
  for t in np.unique(T.TEAM_ID):
    matches = np.where(T.TEAM_ID==t)[0]
    if len(matches)==1:
      keep_idx.append(matches[0])
    else:
      ordered_start_year = np.argsort(T.START_YEAR[matches])
      keep_idx.append(matches[ordered_start_year.values[0]])
  return T.iloc[keep_idx].reset_index()

def get_team_roster(teamid,season=default_season):
  p = stats_params.copy()
  p['TeamID'] = teamid
  p['Season'] = season
  j = requests.get('http://stats.nba.com/stats/commonteamroster', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])
  
def get_team_info(teamid,season=default_season):
  p = stats_params.copy()
  p['TeamID'] = teamid
  p['Season'] = season
  j = requests.get('http://stats.nba.com/stats/teaminfocommon', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_team_history(teamid):
  p = stats_params.copy()
  p['TeamID'] = teamid
  j = requests.get('http://stats.nba.com/stats/teamyearbyyearstats', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_players_all():
  p = stats_params.copy()
  p['Season'] = default_season
  j = requests.get('http://stats.nba.com/stats/commonallplayers', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_players_season(season=default_season):
  season_year = int(season.split('-')[0])
  P = get_players_all()
  return P.iloc[np.where([(int(p.FROM_YEAR)<=season_year)*(int(p.TO_YEAR)>=season_year) for n,p in P.iterrows()])[0]].reset_index()

def get_players_current():
  P = get_players_all()
  return P[P.TO_YEAR==current_year].reset_index()

def get_player_info(playerid):
  p = stats_params.copy()
  p['PlayerID']=str(playerid)
  j = requests.get('http://stats.nba.com/stats/commonplayerinfo', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_player_career(playerid):
  p = stats_params.copy()
  p['PlayerID']=str(playerid)
  j = requests.get('http://stats.nba.com/stats/playercareerstats', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_player_gamelog(playerid,season=default_season):
  p = stats_params.copy()
  p['PlayerID'] = playerid
  p['Season'] = season
  j = requests.get('http://stats.nba.com/stats/playergamelog', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_team_gamelog(teamid,season=default_season):
  p = stats_params.copy()
  p['TeamID'] = teamid
  p['Season'] = season
  j = requests.get('http://stats.nba.com/stats/teamgamelog', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])  

def get_boxscore(gameid):
  try:
    J = json.load(open('%s/json/box_%s.json' % (DATAHOME, gameid), 'rb'))  
  except:
    p = stats_params.copy()
    p['GameID'] = gameid
    J = requests.get('http://stats.nba.com/stats/boxscore', params=p, headers=user_agent).json()['resultSets']
  #---
  box=[]
  for j in J:
    if bool(j['rowSet']):
      box.append(pd.DataFrame(data=j['rowSet'],columns=j['headers']))
    else:
      box.append([])
  return box
  #---
  #return [pd.DataFrame(data=j['rowSet'],columns=j['headers']) for j in J]
  #return [pd.DataFrame(data=j['rowSet'],columns=j['headers']) for j in J[0:6]]

def get_pbp(gameid):
  try:
    j = json.load(open('%s/json/pbp_%s.json' % (DATAHOME, gameid), 'rb'))
  except:
    p = stats_params.copy()
    p['GameID'] = gameid
    #j = requests.get('http://stats.nba.com/stats/playbyplay', params=p, headers=user_agent).json()['resultSets'][0]
    j = requests.get('http://stats.nba.com/stats/playbyplayv2', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_shots(gameid):
  try:
    j = json.load(open('%s/json/sc_%s.json' % (DATAHOME, gameid), 'rb'))
  except:
    p = stats_params.copy()
    p['ContextMeasure'] = 'FGA'
    p['GameID'] = gameid
    j = requests.get('http://stats.nba.com/stats/shotchartdetail', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_average_shots():
  try:
    j = json.load(open('%s/json/shots_average.json' % DATAHOME, 'rb'))
  except:
    p = stats_params.copy()
    p['GameID']='0021500001' # required but doesn't change output
    p['ContextMeasure'] = 'FG_PCT'
    j = requests.get('http://stats.nba.com/stats/shotchartdetail', params=p, headers=user_agent).json()['resultSets'][0]
    with open('%s/json/shots_average.json' % DATAHOME, 'w') as f:
      json.dump(j, f)
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])
  
def get_synergy_stats(query_name):
  j = requests.get('http://stats.nba.com/js/data/playtype' + '/%s.js' % query_name, params={}, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_sportvu_stats(query_name, season='2015'):
  j = requests.get('http://stats.nba.com/js/data/sportvu/%s/%sData.json' % (season,query_name),params={},headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])  

def get_drafthistory():
  p = stats_params.copy()
  j = requests.get('http://stats.nba.com/stats/drafthistory', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_combine_results(query_name, season=default_season):
  # drillresults, nonstationaryshooting, playeranthro
  # spotshooting, stats
  p = stats_params.copy()
  p['Season'] = season
  j = requests.get('http://stats.nba.com/stats/draftcombine%s' % query_name, params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])


## Sports Illustrated play-by-play:
def get_si_pbp(gameid):
  try:
    k = json.load(open('%s/json/si_pbp_%s.json' % (DATAHOME, gameid), 'rb'))
  except:
    p = si_params.copy()
    p['id'] = gameid
    j = requests.get('http://www.si.com/pbp/liveupdate', params=p, headers=user_agent).json()
    k = j['apiResults'][0]['league']['season']['eventType'][0]['events'][0]['pbp']
  return pd.DataFrame.from_records(k)

def write_si_pbp(gameid):
  # convert gameid to SI id
  print 'Game %s, Sports Illustrated' % gameid
  p = si_params.copy()
  p['id'] = gameid
  j = requests.get('http://www.si.com/pbp/liveupdate', params=p, headers=user_agent).json()
  with open('%s/json/si_pbp_%s.json' % (DATAHOME, gameid), 'w') as f:
    json.dump( j['apiResults'][0]['league']['season']['eventType'][0]['events'][0]['pbp'], f)

#### NOTE: This is for now-removed SportVu endpoint
# Still works for any previously-saved data 
# Will need tweaking if/when the endpoint is returned
#

def get_sportvu_locations(gameid, eventnum):
  # 
  # Important to remember: Event number indexing in play-by-play begins at 1!
  if eventnum==0:
    print 'Warning: Event Num = 0 passed. Switching to event number 1.'
    eventnum+=1
  # 
  try:
    #J = json.load( open('%s/json/sv_%s_%s.json' % (DATAHOME, gameid, eventnum), 'rb') )
    #J = json.load( open('%s/json/sv_%s_%s.json' % (DATAHOME, gameid, eventnum.zfill(4)), 'rb') )
    J = json.load( open('%s/json/sv_%s_%s.json' % (DATAHOME, gameid, eventnum), 'rb') )
  except:
    p = stats_params.copy()
    p['GameEventID'] = eventnum
    p['GameID'] = gameid
    J = requests.get('http://stats.nba.com/stats/locations_getmoments', params=p, headers=user_agent).json()['resultSets'][0]

  home_players = pd.DataFrame.from_records(J['home']['players'])
  home_players['teamid'] = J['home']['teamid']
  away_players = pd.DataFrame.from_records(J['visitor']['players'])
  away_players['teamid'] = J['visitor']['teamid']
  players = pd.merge(home_players, away_players, how='outer')
  players['playername'] = [pl.firstname + ' ' + pl.lastname for n,pl in players.iterrows()]
  namedict = dict(zip(players.playerid.values, players.playername.values))  
  numberdict = dict(zip(players.playerid.values, players.jersey.values))
  positiondict = dict(zip(players.playerid.values, players.position.values))

  # SHOULD WE DOWNSAMPLE THE NUMBER OF MOMENTS CHOSEN????
  moments = J['moments']
  nmoments = len(moments)
  
  # Save simple (1-d) data
  nplayers = 10  
  period = [m[0] for m in moments]
  momentid = [m[1] for m in moments]
  period_remain = [m[2] for m in moments]
  shotclock_remain = [m[3] for m in moments]
  ballx = [m[5][0][2] for m in moments]
  bally = [m[5][0][3] for m in moments]
  ballz = [m[5][0][4] for m in moments]
  
  # Save larger (10-d) data for each player
  teamid = np.array(range(nmoments), dtype=object)
  playerid = np.array(range(nmoments), dtype=object)
  playername = np.array(range(nmoments), dtype=object)
  playernumber = np.array(range(nmoments), dtype=object)
  position = np.array(range(nmoments), dtype=object)
  playerx = np.array(range(nmoments), dtype=object)
  playery = np.array(range(nmoments), dtype=object)

  for m in range(nmoments):
    teamid[m] = [moments[m][5][n+1][0] for n in range(nplayers)]
    playerid[m] = [moments[m][5][n+1][1] for n in range(nplayers)]
    playerx[m] = [moments[m][5][n+1][2] for n in range(nplayers)]
    playery[m] = [moments[m][5][n+1][3] for n in range(nplayers)]
    playername[m] = [namedict[pl] for pl in playerid[m]]
    playernumber[m] = [numberdict[pl] for pl in playerid[m]]
    position[m] = [positiondict[pl] for pl in playerid[m]]

  # Return result as Pandas DataFrame
  D = pd.DataFrame(data=momentid, columns=['momentid'])
  D['period'] = period
  D['period_remain'] = period_remain
  D['shotclock_remain'] = shotclock_remain
  D['ballx'] = ballx
  D['bally'] = bally
  D['ballz'] = ballz
  D['playerid'] = playerid
  D['playername'] = playername
  D['playernumber'] = playernumber
  D['position'] = position
  D['teamid'] = teamid  
  D['playerx'] = playerx
  D['playery'] = playery
  return D

def get_players_event(gameid, eventnum):
  # Important to remember: Event number indexing in play-by-play begins at 1!
  if eventnum==0:
    print 'Warning: Event Num = 0 passed. Switching to event number 1.'
    eventnum+=1
  # 
  try:
    #J = json.load( open('%s/json/sv_%s_%s.json' % (DATAHOME, gameid, eventnum), 'rb') )
    J = json.load( open('%s/json/sv_%s_%s.json' % (DATAHOME, gameid, eventnum.zfill(4)), 'rb') )
  except:
    p = stats_params.copy()
    p['GameEventID'] = eventnum
    p['GameID'] = gameid
    J = requests.get('http://stats.nba.com/stats/locations_getmoments', params=p, headers=user_agent).json()['resultSets'][0]

  home_players = pd.DataFrame.from_records(J['home']['players'])
  home_players['teamid'] = J['home']['teamid']
  away_players = pd.DataFrame.from_records(J['visitor']['players'])
  away_players['teamid'] = J['visitor']['teamid']
  players = pd.merge(home_players, away_players, how='outer')
  players['playername'] = [pl.firstname + ' ' + pl.lastname for n,pl in players.iterrows()]  
  namedict = dict(zip(players.playerid.values, players.playername.values))
  numberdict = dict(zip(players.playerid.values, players.jersey.values))
  positiondict = dict(zip(players.playerid.values, players.position.values))
  
  moments = [J['moments'][0], J['moments'][-1]]
  nmoments = len(moments)
  
  # Initialize arrays
  nplayers = 10  
  momentid = [m[1] for m in moments]
  teamid = np.array(range(nmoments), dtype=object)
  playerid = np.array(range(nmoments), dtype=object)
  playername = np.array(range(nmoments), dtype=object)
  playernumber = np.array(range(nmoments), dtype=object)
  position = np.array(range(nmoments), dtype=object)
  playerx = np.array(range(nmoments), dtype=object)
  playery = np.array(range(nmoments), dtype=object)

  for m in range(nmoments):
    teamid[m] = [moments[m][5][n+1][0] for n in range(nplayers)]
    playerid[m] = [moments[m][5][n+1][1] for n in range(nplayers)]
    playerx[m] = [moments[m][5][n+1][2] for n in range(nplayers)]
    playery[m] = [moments[m][5][n+1][3] for n in range(nplayers)]
    playername[m] = [namedict[pl] for pl in playerid[m]]
    playernumber[m] = [numberdict[pl] for pl in playerid[m]]
    position[m] = [positiondict[pl] for pl in playerid[m]]

  D = pd.DataFrame(data=momentid, columns=['momentid'])
  D['playerid'] = playerid
  D['playername'] = playername
  D['playernumber'] = playernumber
  D['position'] = position
  D['teamid'] = teamid
  return D
  
def get_players_game(gameid):  
  eventnum = '1'
  # add while loop to ensure we keep going eventnum += 1
  # until we get a working number, if eventnum=1 doesn't work
  try:
    #J = json.load( open('%s/json/sv_%s_%s.json' % (DATAHOME, gameid, eventnum), 'rb') )
    J = json.load( open('%s/json/sv_%s_%s.json' % (DATAHOME, gameid, eventnum.zfill(4)), 'rb') )
  except:
    p = stats_params.copy()
    p['GameEventID'] = eventnum
    p['GameID'] = gameid
    J = requests.get('http://stats.nba.com/stats/locations_getmoments', params=p, headers=user_agent).json()['resultSets'][0]

  home_players = pd.DataFrame.from_records(J['home']['players'])
  home_players['teamid'] = J['home']['teamid']
  away_players = pd.DataFrame.from_records(J['visitor']['players'])
  away_players['teamid'] = J['visitor']['teamid']
  players = pd.merge(home_players, away_players, how='outer')
  return players
  #return get_boxscore(gameid)[4]
  
def get_play_team(p):
  # given a row of play-by-play data p, this function determines which 
  # team made the given play  
  #
  # 0 for home team
  # 1 for away team
  if p.HOMEDESCRIPTION is not None and p.VISITORDESCRIPTION is None:
    return 'home'
  elif p.HOMEDESCRIPTION is None and p.VISITORDESCRIPTION is not None:
    return 'away'
  elif p.HOMEDESCRIPTION is None and p.VISITORDESCRIPTION is None:
    return np.nan
  else: # both filled in -> have to check the description text
    h = p.HOMEDESCRIPTION
    v = p.VISITORDESCRIPTION
    e_type = p.EVENTMSGTYPE
    if e_type==1:
      if re.search('Shot',h): return 'home'
      elif re.search('Shot',v): return 'away'
    elif e_type==2:
      if re.search('MISS',h): return 'home'
      elif re.search('MISS',v): return 'away'
    elif e_type==3:
      if re.search('Free Throw',h): return 'home'
      elif re.search('Free Throw',v): return 'away'
    elif e_type==4:
      if re.search('REBOUND',h) or re.search('Rebound',h): return 'home'
      elif re.search('REBOUND',v) or re.search('Rebound',v): return 'away'
    elif e_type==5:
      if re.search('Turnover',h): return 'home'
      elif re.search('Turnover',v): return 'away'
    #elif e_type==6:
    #  if re.search('Turnover',h): return 0
    #  elif re.search('Turnover',v): return 1
    else:
      print 'PROBLEM!'
      print h + '\t' + v
      #oiuj

def get_play_desc(p):
  if p.HOMEDESCRIPTION is not None and p.VISITORDESCRIPTION is None:
    return str(p.HOMEDESCRIPTION).split(' (')[0]
  elif p.HOMEDESCRIPTION is None and p.VISITORDESCRIPTION is not None:
    return str(p.VISITORDESCRIPTION).split(' (')[0]
  elif p.HOMEDESCRIPTION is None and p.VISITORDESCRIPTION is None:
    return ''
  else: # both filled in -> have to check the description text
    h = p.HOMEDESCRIPTION.split(' (')[0]
    v = p.VISITORDESCRIPTION.split(' (')[0]
    e_type = p.EVENTMSGTYPE
    if e_type==1:
      if re.search('Shot',h): return h
      elif re.search('Shot',v): return v
    elif e_type==2:
      if re.search('MISS',h): return h
      elif re.search('MISS',v): return v
    elif e_type==3:
      if re.search('Free Throw',h): return h
      elif re.search('Free Throw',v): return v
    elif e_type==4:
      if re.search('REBOUND',h) or re.search('Rebound',h): return h
      elif re.search('REBOUND',v) or re.search('Rebound',v): return v
    elif e_type==5:
      if re.search('Turnover',h): return h
      elif re.search('Turnover',v): return v
    #elif e_type==6:
    #  if re.search('Turnover',h): return 0
    #  elif re.search('Turnover',v): return 1
    else:
      print 'PROBLEM!'
      print h + '\t' + v
      #oiuj
#### END OLD ^^^ END OLD ^^^ END OLD ^^^ #######  
      
## END DATA GRAB FUNCTIONS

## WRITE FUNCTIONS:
 
def write_game_json(gameid, do_sportvu=False):
  p = stats_params.copy()
  p['ContextMeasure'] = 'FGA'
  p['GameID'] = gameid
  
  print 'Game %s, box score' % gameid
  box = requests.get('http://stats.nba.com/stats/boxscore', params=p, headers=user_agent).json()['resultSets']
  with open('%s/json/box_%s.json' % (DATAHOME, gameid), 'w') as f:
    json.dump( box, f)
  
  print 'Game %s, play by play' % gameid
  pbp = requests.get('http://stats.nba.com/stats/playbyplayv2', params=p, headers=user_agent).json()['resultSets'][0]
  with open('%s/json/pbp_%s.json' % (DATAHOME, gameid), 'w') as f:
    json.dump( pbp, f)
    
  print 'Game %s, shot chart' % gameid
  shots = requests.get('http://stats.nba.com/stats/shotchartdetail', params=p, headers=user_agent).json()['resultSets'][0]
  with open('%s/json/shots_%s.json' % (DATAHOME, gameid), 'w') as f:
    json.dump( shots, f)

def write_gamelist_json(filename):
  f = open(filename, 'r')
  f.readline() # drop headers    
  for r in f.readlines():
    gameid = r.split(',')[0]
    write_game_json(gameid)

def write_gamelist_by_date(filename,seasonid,startday,stopday):
  numdays = (stopday-startday).days
  datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]

  f = open(filename, 'w')
  f.write('GAME_ID,SEASON_ID,GAME_CODE,AWAY,HOME\n') # write headers
  for d in datelist:
    diso = str.replace(d.isoformat(),'-','')
    games = get_gamelist_by_date(diso)
    for g in games:
      home = g['home']['team_key']
      away = g['visitor']['team_key']
      gamecode = diso + away + home
      print d,g['id'],away,home
      #
      # VV NEED TO FIX: STILL INCLUDES ALL STAR GAME
      #
      if seasonid==g['id'][0:5]: # make sure to exclude all start break!
        f.write(','.join([g['id'],seasonid,gamecode,away,home]) + '\n')
  f.close()
