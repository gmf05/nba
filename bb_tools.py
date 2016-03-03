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
DATAPATH = '/media/gmf/GMF/unsynced/nba/data' # where to save data
NBAHOME = '/home/gmf/Code/git/nba' # where are scripts
        
user_agent = {'User-agent': 'Mozilla/5.0'}
current_year = '2015'
default_season = current_year + '-10'
stats_base_url = 'http://stats.nba.com/stats/'
do_sportvu = False

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

## BEGIN HELPER FUNCTIONS
def getclosest(i, N):
  N = np.array(N)
  dist = abs(i-N)
  #return N[np.argmin(dist)]
  i=np.argmin(dist)
  return N[i],i

def zip2(keys,vals):
  return dict([(keys[i], vals[i]) for i in range(len(keys))])

def dict_inv(d):
  return zip2(d.values(), d.keys())
  
def dateify(date_str):
  y,m,d = date_str.split('-')
  return datetime.date(int(y),int(m),int(d))


def compute_sec_elapsed(period, pctime_str):
  nmin,nsec = pctime_str.split(':')
  nmin = int(nmin)
  nsec = int(nsec)
  if period<5:
    pctime_sec = (11-nmin)*60 + 60 - nsec
    t = (period-1)*720 + pctime_sec
  else:
    pctime_sec = (4-nmin)*60 + 60 - nsec
    t = 2880 + (period-5)*300 + pctime_sec
  return t
  
def nsec_game(Nperiods):
  if Nperiods<4:
    print 'WARNING: Less than four periods found...'
    return np.nan
  elif Nperiods==4:
    return 2880
  else:
    return (Nperiods-4)*300 + 2880

def nsec_gameid(gameid):
  return nsec_game(get_pbp(gameid).iloc[-1].PERIOD)
  
def nsec_remain_qtr(p):
  nmin,nsec = str(p.PCTIMESTRING).split(':')
  return int(nmin)*60 + int(nsec)

def clock2float(clock_time):
  mm,ss = clock_time.split(':')
  return int(mm) + float(ss)/60.0

## END HELPER FUNCTIONS

## BEGIN PLOTTING FUNCTIONS
# Simple version. Image based
def draw_court(axis=[0,100,0,50]): 
  #fig = plt.figure(figsize=(15,7.5))
  img = mpimg.imread(NBAHOME + '/image/nba_court_T.png')
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
  j = requests.get(stats_base_url + 'franchisehistory', params=stats_params, headers=user_agent).json()['resultSets'][0]
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
  T = T.iloc[keep_idx]
  return T

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

def get_players_all(season=default_season):
  p = stats_params.copy()
  p['Season'] = season
  j = requests.get(stats_base_url + 'commonallplayers', params=p, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_players_current():
  P = get_players_all()
  return P[P.TO_YEAR==current_year]

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
  p = stats_params.copy()
  p['GameID'] = gameid
  try:
    J = json.load(open('%s/json/bs_%s.json' % (DATAPATH, gameid), 'rb'))  
  except:
    J = requests.get('http://stats.nba.com/stats/boxscore', params=p, headers=user_agent).json()['resultSets']
  #return J # use for write_game_json
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
  p = stats_params.copy()
  p['GameID'] = gameid
  try:
    j = json.load(open('%s/json/pbp_%s.json' % (DATAPATH, gameid), 'rb'))
  except:
    #j = requests.get('http://stats.nba.com/stats/playbyplay', params=p, headers=user_agent).json()['resultSets'][0]
    j = requests.get('http://stats.nba.com/stats/playbyplayv2', params=p, headers=user_agent).json()['resultSets'][0]
  #return j # use for write_game_json
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_shots(gameid):
  p = stats_params.copy()
  p['ContextMeasure'] = 'FGA'
  p['GameID'] = gameid
  try:
    j = json.load(open('%s/json/sc_%s.json' % (DATAPATH, gameid), 'rb'))
  except:
    j = requests.get('http://stats.nba.com/stats/shotchartdetail', params=p, headers=user_agent).json()['resultSets'][0]
  #return j # use for write_game_json
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_average_shots():
  p = stats_params.copy()
  p['GameID']='0021500001' # required but doesn't change output
  p['ContextMeasure'] = 'FG_PCT'
  j = requests.get('http://stats.nba.com/stats/shotchartdetail', params=p, headers=user_agent).json()['resultSets'][1]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])
  
def get_synergy_data(query_name):
  j = requests.get('http://stats.nba.com/js/data/playtype' + '/%s.js' % query_name, params={}, headers=user_agent).json()['resultSets'][0]
  return pd.DataFrame(data=j['rowSet'],columns=j['headers'])

def get_sportvu_data(query_name, season='2015'):
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

#### OLD VVV OLD VVV OLD VVV #######






def get_sportvu(gameid, eventnum):
  #
  # Important to remember: Event number indexing in play-by-play begins at 1!
  if eventnum==0:
    print 'Warning: Event Num = 0 passed. Switching to event number 1.'
    eventnum+=1
  #
  p = stats_params.copy()
  p['GameEventID'] = eventnum
  p['GameID'] = gameid
  J = requests.get(stats_base_url + 'locations_getmoments', params=p, headers=user_agent).json()['resultSets'][0]
  player_fields = J['home']['players'][0].keys()
  home_players = pd.DataFrame(data=[J['home']['players'][i].values() for i in range(len(J['home']['players']))], columns=player_fields)
  away_players = pd.DataFrame(data=[J['visitor']['players'][i].values() for i in range(len(J['visitor']['players']))], columns=player_fields)
  players = pd.merge(home_players, away_players, how='outer')
  jerseydict = dict(zip(players.playerid.values, players.jersey.values))
  playerteamdict = dict(zip(players.playerid.values, [J['home']['teamid'] for n in range(len(home_players))] + [J['visitor']['teamid'] for n in range(len(away_players))]))
  moments = J['moments']
  #  
  # SHOULD WE DOWNSAMPLE THE NUMBER OF MOMENTS CHOSEN????
  # 
  # Initialize arrays
  num_moments = len(moments)
  num_players = 10
  fields = ['playerx','playery','playerid','playernum', 'playername', 'playerpos', 'teamid','ballx','bally',
          'ballz','shotclock_remain','sec_remain','momentid','period']
  num_fields = len(fields)
  D = pd.DataFrame(data=[[None for i in range(num_fields)] for j in range(num_moments)], columns=fields)
  player_fields = ['playerid','playernum','playername', 'playerpos','playerx','playery','teamid']
  for f in player_fields: D[f] = [np.zeros(num_players,dtype=int) for n in range(num_moments)]

  # VERY IMPORTANT!: Here we sort order of the position data to make sure home=1-5, away=6-10
  home_idx=[]
  away_idx=[]
  for k in range(1,11):
    if moments[0][-1][k][0]==J['home']['teamid']: home_idx.append(k)
    elif moments[0][-1][k][0]==J['visitor']['teamid']: away_idx.append(k)
  player_idx = np.concatenate((home_idx,away_idx))
  
  # Loop over each entry in the SportVu data (each moment, ~0.04 sec)
  for i in range(num_moments):
    D.period.iloc[i], D.momentid.iloc[i], D.sec_remain.iloc[i], D.shotclock_remain.iloc[i] = moments[i][0:4]
    D.ballx.iloc[i],D.bally.iloc[i],D.ballz.iloc[i] = moments[i][-1][0][2:5]
#    # Initializing lists for player info
    # Filling out player info
    for j in range(num_players):
      #print i,j,player_idx[j],D.playerid.shape
      D.playerid[i][j] = moments[i][-1][player_idx[j]][1]
      D.playerx[i][j], D.playery[i][j] = moments[i][-1][player_idx[j]][2:4]
      D.playernum[i][j] = jerseydict[D.playerid[i][j]]
      D.teamid[i][j] = playerteamdict[D.playerid[i][j]]

  # Also, we reflect the court to match TV: Home team attacks right to start  
  #D.playerx = 100 - D.playerx
  #D.ballx = 100 - D.ballx
  return D


def get_event_players(gameid, eventnum):
  # Important to remember: Event number indexing in play-by-play begins at 1!
  p = stats_params.copy()
  p['GameEventID'] = eventnum
  p['GameID'] = gameid
  J = requests.get(stats_base_url + 'locations_getmoments', params=p, headers=user_agent).json()['resultSets'][0]
  player_fields = J['home']['players'][0].keys()
  home_players = pd.DataFrame(data=[J['home']['players'][i].values() for i in range(len(J['home']['players']))], columns=player_fields)
  away_players = pd.DataFrame(data=[J['visitor']['players'][i].values() for i in range(len(J['visitor']['players']))], columns=player_fields)
  players = pd.merge(home_players, away_players, how='outer')
  playerteamdict = dict(zip(players.playerid.values, [J['home']['teamid'] for n in range(len(home_players))] + [J['visitor']['teamid'] for n in range(len(away_players))]))
  players['team'] = [playerteamdict[players.iloc[n]['playerid']] for n in range(len(players))]
  moments = [J['moments'][0], J['moments'][-1]]
  num_players = 10
  fields = ['playerid','teamid','shotclock_remain','sec_remain','momentid','period']
  num_fields = len(fields)
  D = pd.DataFrame(data=[[None for i in range(num_fields)] for j in range(2)], columns=fields)
  player_fields = ['playerid','teamid']
  for f in player_fields: D[f] = [np.zeros(num_players,dtype=int) for n in range(2)]
  D.period.iloc[0], D.momentid.iloc[0], D.sec_remain.iloc[0], D.shotclock_remain.iloc[0] = moments[0][0:4]
  D.period.iloc[1], D.momentid.iloc[1], D.sec_remain.iloc[1], D.shotclock_remain.iloc[1] = moments[-1][0:4]      
  for j in range(num_players):    
    D.playerid[0][j] = moments[0][-1][j+1][1] # +1 bc ball is row 0!
    D.teamid[0][j] = playerteamdict[D.playerid[0][j]]
    D.playerid[1][j] = moments[-1][-1][j+1][1] # +1 bc ball is row 0!
    D.teamid[1][j] = playerteamdict[D.playerid[1][j]]
  return D
  
def get_players_game(gameid):
  eventnum = 1
  J = json.load( open( '%s/json/sv_%s_%s.json' % (DATAPATH,gameid,str(eventnum).zfill(4)), 'r' ) )
  player_fields = J['home']['players'][0].keys()
  home_players = pd.DataFrame(data=[J['home']['players'][i].values() for i in range(len(J['home']['players']))], columns=player_fields)
  away_players = pd.DataFrame(data=[J['visitor']['players'][i].values() for i in range(len(J['visitor']['players']))], columns=player_fields)
  players = pd.merge(home_players, away_players, how='outer')
  playerteamdict = dict(zip(players.playerid.values, [J['home']['teamid'] for n in range(len(home_players))] + [J['visitor']['teamid'] for n in range(len(away_players))]))
  players['team'] = [playerteamdict[players.iloc[n]['playerid']] for n in range(len(players))]
  return players

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
  
## END DATA GRAB FUNCTIONS

## WRITE FUNCTION:
def write_game_json(gameid, do_sportvu=False):
  print 'Game %s, box score' % gameid
  with open('%s/json/bs_%s.json' % (DATAPATH, gameid), 'w') as f:
    json.dump( get_boxscore(gameid), f )
  
  print 'Game %s, play by play' % gameid
  with open('%s/json/pbp_%s.json' % (DATAPATH, gameid), 'w') as f:
    json.dump( get_pbp(gameid), f )
    
  print 'Game %s, shot chart' % gameid
  with open('%s/json/shots_%s.json' % (DATAPATH, gameid), 'w') as f:
    json.dump( get_shots(gameid), f )

def write_gamelist_json(gamelist):
  f = open(gamelist, 'r')
  f.readline() # drop headers    
  for r in f.readlines():
    gameid = r.split(',')[0]
    write_game_json(gameid)

def write_gamelist_by_date(seasonid,startday,stopday):
  numdays = (stopday-startday).days
  datelist = [startday + datetime.timedelta(days=x) for x in range(0, numdays+1)]

  f = open('%s/csv/gamelist_update.csv' % DATAPATH, 'w')
  f.write('gameid,seasonid,gameabbr,away,home\n') # write headers
  for d in datelist:
    diso = str.replace(d.isoformat(),'-','')
    games = get_gamelist_by_date(diso)
    for g in games:
      home = g['home']['team_key']
      away = g['visitor']['team_key']
      gameid0 = diso + away + home
      print d,g['id'],away,home
      #
      # VV STILL NEED TO FIX
      #
      if seasonid==g['id'][0:5]: # make sure to exclude all start break!
        f.write(','.join([g['id'],seasonid,gameid0,away,home]) + '\n')
  f.close()
