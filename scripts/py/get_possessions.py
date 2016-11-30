# -*- coding: utf-8 -*-
"""
Created on Mon Sep 19 16:04:20 2016

@author: gmf
"""

# Import modules
import re
import numpy as np
import pandas as pd
import bb_tools as bb
#import statsmodels.api as sm
import sklearn.linear_model as slm

# Connect to MongoDB
from pymongo import MongoClient
client = MongoClient('localhost', 27117)
db = client['nba']
events_db = db['possessions']

#all_players = bb.get_players_all()
#all_player_ids = all_players['PERSON_ID'].values

# only need once:
#import pymongo
#events_db.create_index([('SEASONID', pymongo.ASCENDING), ('GAMEID', pymongo.ASCENDING)])

# where do periods start and end??
def get_period_start_end(pbp_g):
  period_start = np.where(pbp_g['EVENTMSGTYPE']==12)[0][0:] + 1
  period_end = np.where(pbp_g['EVENTMSGTYPE']==13)[0][0:]
  period_start = np.sort(period_start)
  period_end = np.sort(period_end)
  
  i=0
  Nstart = len(period_start)
  Nend = len(period_end)
  Nmax = np.max([Nstart, Nend])
  while i<Nmax-1:
    inc = True
    delete_bad = False
    if period_start[i] > period_end[i]:
      if i==0:
        #print 'Missing entry start beginning', gameid
        period_start = np.insert(period_start, 0, 1)
      else:
        #print 'Order error 1', gameid
        delete_bad = True
      inc = False
    elif i==Nstart-1:  # extr     
      delete_bad = True
      inc = False
    elif period_end[i]>=period_start[i+1]:
      #print 'Order error 2', gameid
      delete_bad = True
      inc = False
    if delete_bad:
      #print 'Deleting entry:' # debug 
      i1 = np.where(np.diff(period_start)<10)[0]+1
      i2 = np.where(np.diff(period_end)<10)[0]+1
      if len(i1)>0:
        period_start = np.delete(period_start, i1)
      if len(i2)>0:
        period_end = np.delete(period_end, i2)
      Nmax-=1
    else:
      if inc:
        i+=1
      
  if len(period_start) > len(period_end):
    #print 'Missing entry end', gameid
    period_end = np.hstack([period_end, len(pbp_g)])
    
  # Final check. Should be passed!  
  if len(period_start)!=len(period_end): # problem!
    print 'Size mismatch!', pbp_g.iloc[0]['GAME_ID']
    print period_start
    print period_end
    print '\n'
  else:
    0
  
  return period_start, period_end


def get_period_starters(pbp_g):
#%
  # Get box score information so we can see which
  # teams are home/away
  gameid = pbp_g.iloc[0]['GAME_ID']
  info_g = bb.get_info(gameid)
  home,away = info_g[['HOME_TEAM_ID','VISITOR_TEAM_ID']]
  away_team, home_team = bb.get_teams_gameid(gameid)

  pbp_g = pbp_g[pbp_g['EVENTMSGACTIONTYPE']!=16] # drop un-useful event type, apparently related to technicals
  pbp_g = pbp_g[pbp_g['EVENTMSGTYPE']!=11] # drop ejections/violations, lots of extraneous ones
  # Drop technical fouls -- Often, they come from people NOT on the court
  idx = np.where([not bool(re.search('T.FOUL', str(p))) for p in pbp_g['HOMEDESCRIPTION'].values])[0]
  pbp_g = pbp_g.iloc[idx]
  idx = np.where([not bool(re.search('T.FOUL', str(p))) for p in pbp_g['VISITORDESCRIPTION'].values])[0]
  pbp_g = pbp_g.iloc[idx]
  # Drop timeouts -- These often have a player ID attached, which is weird
  idx = np.where([not bool(re.search('Timeout', str(p))) for p in pbp_g['HOMEDESCRIPTION'].values])[0]
  pbp_g = pbp_g.iloc[idx]
  idx = np.where([not bool(re.search('Timeout', str(p))) for p in pbp_g['VISITORDESCRIPTION'].values])[0]
  pbp_g = pbp_g.iloc[idx]
  
  # NOTE: there are sometimes extraneous EVENTMSGTYPE for quarter start (12)
  # or quarter end (13). They happen a couple times per season, but ruin the
  # the whole start/end sequnece within the game, so we can't rely on looking
  # for 12/13 alone.
  # We check by making sure start/end indices have right length and 
  # make a valid sequence using a helper function
  period_start, period_end = get_period_start_end(pbp_g)
  
  # Now we find starters for each period
  away_starter_list = []
  home_starter_list = []
  for m in range(len(period_start)):
    pbp_period = pbp_g.iloc[period_start[m]: period_end[m]]
    # Note : Last condition drops weird "team rebound" entries
    pbp_period = pbp_period[(pbp_period['PLAYER1_NAME']>0) & (pbp_period['EVENTMSGTYPE']<=11) & (pbp_period['PLAYER1_TEAM_ID']>0)]
    
    # Who is subbed out before they are subbed in?
    period_subs = pbp_period[pbp_period['EVENTMSGTYPE']==8]
    
    period_players = np.unique(np.union1d(np.union1d(pbp_period['PLAYER1_ID'].values, pbp_period['PLAYER2_ID'].values), 
                                          pbp_period['PLAYER3_ID'].values))
    # Drop player_id = 0
    period_players = np.delete(period_players, np.where(period_players==0)[0])
    # Drop Team IDs appearing in player ID list
    # e.g. team rebound
    period_players = np.delete(period_players, np.where(period_players>=1610000000)[0])
    # Drop any players where "persontype" = 7. Apparently, those are errors of some kind
    # Or placeholders
    period_players = np.setdiff1d(period_players, pbp_period[pbp_period.PERSON1TYPE==7].PLAYER1_ID.values)
    period_players = np.setdiff1d(period_players, pbp_period[pbp_period.PERSON2TYPE==7].PLAYER2_ID.values)
    #period_players = np.setdiff1d(period_players, pbp_period[pbp_period.PERSON3TYPE==7].PLAYER3_ID.values)
    
    # Now we have a list of players from the period
    # Who was subbed in/out and when?
    Nplayers = len(period_players)
    player_subs = np.Inf*np.ones((Nplayers, 3))
    player_subs[:,0] = period_players
    
    for i,plyr in enumerate(period_players):
      try:
        player_subs[i,1] = period_subs[period_subs['PLAYER1_ID']==plyr].index[0] # plyr first comes out
      except:
        0
      try:
        player_subs[i,2] = period_subs[period_subs['PLAYER2_ID']==plyr].index[0] # plyr first comes in
      except:
        0
    
    # Players who started either never came out (pl_neverout)
    # or were subbed out *before* being subbed in again (if at all) (pl_out)
    pl_neverout = player_subs[np.where(np.isinf(player_subs[:,1]) * np.isinf(player_subs[:,2]))[0], 0]
    pl_out = player_subs[np.where(player_subs[:,1]<player_subs[:,2])[0], 0]
    period_starters = np.union1d(pl_neverout, pl_out)

    is_away = np.array([p in away_team['PLAYER_ID'].values for p in period_starters], dtype=np.int)
    away_starters = period_starters[np.where(is_away)[0]]

    is_home = np.array([p in home_team['PLAYER_ID'].values for p in period_starters], dtype=np.int)
    home_starters = period_starters[np.where(is_home)[0]]
    
    Nstarters = len(period_starters)
    Naway = len(away_starters)
    Nhome = len(home_starters)
    
    # Drop any extraneous players
    # OR: TODO!: if too few players, fix with box score
    if Naway!=5 or Nhome!=5 or Nstarters!=10:
      print gameid, m+1, 'Wrong number of starters:  ',Nstarters,Naway,Nhome
      # Run problem-solver, which may use more data, such as box score        
      # For now: Fill in -1 if total number of players < 5 for home/away        
      if Naway<5:
        print ' -- Too few (away)'
        for n in range(5-Naway):
          away_starters = np.append(away_starters, -1)
      if Nhome<5:
        print ' -- Too few (home)'
        for n in range(5-Nhome):
          home_starters = np.append(home_starters, -1)
        
        # TODO: CAN WE SOLVE THIS WITH BOX SCORE MINUTES???
        # Somebody should have a quarter's worth of minutes


      # Try to drop extra(s)
      # by keeping who appears first in PBP order
      # Basically, this assumes most likely error is a missing SUB event
      if Naway>5:
        print ' -- Too many (away)'
        away_first_event = []
        for pid in away_starters:
          try:
            idx = np.where(pbp_period['PLAYER1_ID']==pid)[0][0]
          except:
            try:
              idx = np.where(pbp_period['PLAYER2_ID']==pid)[0][0]
            except:
              idx = np.where(pbp_period['PLAYER3_ID']==pid)[0][0]
          away_first_event.append(idx)
        away_starters = away_starters[np.argsort(away_first_event)[0:5]]

      
      if Nhome>5:
        print ' -- Too many (home)'
        home_first_event = []
        for pid in home_starters:
          try:
            idx = np.where(pbp_period['PLAYER1_ID']==pid)[0][0]
          except:
            try:
              idx = np.where(pbp_period['PLAYER2_ID']==pid)[0][0]
            except:
              idx = np.where(pbp_period['PLAYER3_ID']==pid)[0][0]
          home_first_event.append(idx)
        home_starters = home_starters[np.argsort(home_first_event)[0:5]]
                
    away_starter_list.append(away_starters)
    home_starter_list.append(home_starters)
  
  return away_starter_list, home_starter_list

#%
def get_possessions(gameid):
  
  info_g = bb.get_info(gameid)
  home,away = info_g[['HOME_TEAM_ID','VISITOR_TEAM_ID']]

  pbp_g = bb.get_pbp(gameid) # play-by-play
  away_period_starters, home_period_starters = get_period_starters(pbp_g)

  # Initialize variables  
  home_players = home_period_starters[0]
  away_players = away_period_starters[0]
  events = []
  period_remain_prev = 720.0
  
  # Assign first possession based on who wins initial jump ball:
  # If no jump ball exists, start with home on offense
  # Note : it doesn't matter because we will figure out based on next event anyway
  try:
    home_isoff = pbp_g[pbp_g['EVENTMSGTYPE']==10].iloc[0]['PLAYER3_TEAM_ID']==home
  except:
    home_isoff = True
      
  # Compute score changes first
  scores = np.zeros([len(pbp_g),2])
  for i,s in enumerate(pbp_g['SCORE'].iloc[1:].values):
    if s:
      scores[i+1,:] = [int(j) for j in s.split(' - ')]
    else:
      scores[i+1,:] = scores[i,:]
  score_change = np.hstack((0, np.diff(scores[:,0]) + np.diff(scores[:,1])))

  # make a table of FT "sessions"
  # Start with a list of all FTs
  ft_list = pbp_g[pbp_g['EVENTMSGTYPE']==3][['PERIOD','PCTIMESTRING','PLAYER1_ID','HOMEDESCRIPTION','VISITORDESCRIPTION']].reset_index()
  ft_list['SEC_REMAIN'] = [bb.nsec_elapsed(f['PERIOD'],f['PCTIMESTRING']) for i,f in ft_list.iterrows()]
  # Drop technical free throws from ft_sessions
  ft_list = ft_list.iloc[np.where([(1-bool(re.search('Technical', str(pbp_g.iloc[i]['HOMEDESCRIPTION'])))) 
  * (1-bool(re.search('Technical', str(pbp_g.iloc[i]['VISITORDESCRIPTION'])))) for i in ft_list['index']])[0]]
  ft_list['MISS'] = [int(bool(re.search('MISS', str(f['HOMEDESCRIPTION']) + str(f['VISITORDESCRIPTION'])))) for i,f in ft_list.iterrows()]
  
  # Then break up into "sessions"
  time_objs = {(p['PERIOD'],p['SEC_REMAIN'],p['PCTIMESTRING']) for i,p in ft_list.iterrows()}
  ft_sessions = pd.DataFrame()
  ft_sessions['PERIOD']=[t[0] for t in time_objs]
  ft_sessions['PCTIMESTRING']=[t[2] for t in time_objs]
  ft_sessions['FTA'] = [len(ft_list[(ft_list['PERIOD']==t[0]) & (ft_list['PCTIMESTRING']==t[2])]) for t in time_objs]
  ft_sessions['FTM'] = ft_sessions['FTA'] - [ft_list[(ft_list['PERIOD']==t[0]) & (ft_list['PCTIMESTRING']==t[2])]['MISS'].sum() for t in time_objs]
  
  # Mark missed shots that are follow by offensive rebounds
  fg_miss = pbp_g[pbp_g['EVENTMSGTYPE']==2][['PERIOD','PCTIMESTRING','PLAYER1_TEAM_ID']].reset_index()
  rebs = pbp_g[pbp_g['EVENTMSGTYPE']==4][['PERIOD','PCTIMESTRING','PLAYER1_ID','PLAYER1_TEAM_ID']]
  # also fix team rebounds
  
  # Arrays to hold results  
  Npbp = len(pbp_g)
  fta = np.zeros(Npbp)
  ftm = np.zeros(Npbp)
  oreb = np.zeros(Npbp)
  
  # for each missed shot, mark whether shooting team matching rebounding team
  reb_idx = 0
  for i,f in fg_miss.iterrows():
    t_miss = bb.nsec_elapsed(f['PERIOD'],f['PCTIMESTRING'])
    while rebs.iloc[reb_idx]['PERIOD']<f['PERIOD']:
      reb_idx += 1
    while bb.nsec_elapsed(rebs.iloc[reb_idx]['PERIOD'], rebs.iloc[reb_idx]['PCTIMESTRING']) < t_miss:
      reb_idx += 1
    
    if rebs.iloc[reb_idx]['PLAYER1_TEAM_ID']==f['PLAYER1_TEAM_ID'] or rebs.iloc[reb_idx]['PLAYER1_ID']==f['PLAYER1_TEAM_ID']:
      oreb[f['index']] += 1
  
  pbp_g['OREB'] = oreb
  fg_miss = pbp_g[pbp_g['EVENTMSGTYPE']==2][['PERIOD','PCTIMESTRING','OREB']]
  # For each session:
  # Attach each session to a made shot (event type = 1)
  # OR a shooting foul (event type = 6)
  for i,f in ft_sessions.iterrows():
    if f['FTA']==1:
      idx = np.where((pbp_g['PERIOD']==f['PERIOD']) & (pbp_g['PCTIMESTRING']==f['PCTIMESTRING']) & (pbp_g['EVENTMSGTYPE']==1))[0]
    elif f['FTA']>=1:
      idx = np.where((pbp_g['PERIOD']==f['PERIOD']) & (pbp_g['PCTIMESTRING']==f['PCTIMESTRING']) & (pbp_g['EVENTMSGTYPE']==6))[0]
    fta[idx] = f['FTA']
    ftm[idx] = f['FTM']
    score_change[idx] += f['FTM']

  pbp_g['FTA'] = fta
  pbp_g['FTM'] = ftm
  pbp_g['SCORE_CHANGE'] = score_change

  for i,p in pbp_g.iterrows():
    
    # Switch to handle different play types
    # Shots (1/2/3), turnover (5) and foul (6)
    # inform who's on offense (home_isoff)
    # Substituion (8) changes players oncourt
    # Start of quarter (12) changes players on court
    # 1 made shot
    # 2 missed shot
    # 3 free throw
    # 4 rebound
    # 5 turnover
    # 6 foul
    # 7 violation -- seems to never have scorechange > 0, so ignore
    # 8 sub
    # 9 timeout
    # 10 jump ball
    # 11 ejection
    # 12 start of quarter
    # 13 end of quarter
    
    h = p['HOMEDESCRIPTION']
    v = p['VISITORDESCRIPTION']
    e_type = p['EVENTMSGTYPE']
    save_event = True
    fga_pts = 0
    
    # Made shot
    if e_type==1:
      poss_type = 1
      if h and (not v or re.search('Shot',h) or re.search('Layup',h) or re.search('Dunk',h)): home_isoff = True
      elif v and (not h or re.search('Shot',v) or re.search('Layup',v) or re.search('Dunk',v)): home_isoff = False
      if home_isoff and h:
        fga_pts = 2 + int(bool(re.search('3PT', h)))
      elif v:
        fga_pts = 2 + int(bool(re.search('3PT', v)))
      else: # sometimes extraneous "made shots" with no description, etc
        save_event = False
        
    # Missed shot
    elif e_type==2:
      poss_type = 2
      if h and (not v or re.search('MISS',h)): home_isoff = True
      elif v and (not h or re.search('MISS',v)): home_isoff = False
      # get fgav - field goal attempted value
      if home_isoff:
        fga_pts = 2 + int(bool(re.search('3PT', h)))
      else:
        fga_pts = 2 + int(bool(re.search('3PT', v)))
      # Missed shot doesn't end poss if OREB
      if p['OREB']: save_event = False
        
    # Turnover
    elif e_type==5:
      poss_type = 5
      if h and (not v or re.search('Turnover',h)): home_isoff = True
      elif v and (not h or re.search('Turnover',v)): home_isoff = False
    
    # Foul 
    elif e_type==6:
      # Technical fouls : don't save
      if (h and re.search('Technical',h)) or (v and re.search('Technical',v)):
        save_event = False
      # Personal foul without FTs or and-one : don't save
      # Note: We don't save on and-one b/c it's already attached to made shot.
      if p['FTA']<=1:
        save_event = False
      # Shooting/personal foul with FTs : save
      elif p['FTA']>1:
        poss_type = 3
        fga_pts = p['FTA']
      
    # SUB
    elif e_type==8:
      save_event = False
      if h and (not v or re.search('SUB',h)):
        try:
          home_players[np.where(home_players==p['PLAYER1_ID'])[0]] = p['PLAYER2_ID']
          # UNLESS free throw
        except:
          print 'Error in home SUB', i
      elif v and (not h or re.search('SUB',v)): 
        try:
          away_players[np.where(away_players==p['PLAYER1_ID'])[0]] = p['PLAYER2_ID']
          # UNLESS free throw
        except:
          print 'Error in away SUB', i
    
    # Jump ball
    elif e_type==10:
      home_isoff = bool(p['PLAYER3_TEAM_ID']==home)
      save_event = False
      
    # START OF QUARTER (12)
    elif e_type==12:
      home_players = home_period_starters[p['PERIOD']-1]
      away_players = away_period_starters[p['PERIOD']-1]
      period_remain_prev = bb.clock2float(p['PCTIMESTRING'])*60.0
      save_event = False
    
    # End of quarter
    elif e_type==13:
      save_event = False
      if p['PERIOD']<4:
        period_remain_prev = 720
      else:
        period_remain_prev = 300
    # Others
    else:
      save_event = False
      
    # Catch weird / out-of-order plays
    if p['SCORE_CHANGE']<0 or p['SCORE_CHANGE']>=5:
      save_event = False
      
    if save_event:
      period_remain = np.round(bb.clock2float(p['PCTIMESTRING'])*60.0, 2)
      if period_remain_prev<30 and period_remain>300:
        if p['PERIOD']<=4:
          period_remain_prev = 720
        else:
          period_remain_prev = 300
      duration = period_remain_prev - period_remain
      period_remain_prev = period_remain
      nsec_elapsed = bb.nsec_elapsed(p['PERIOD'], p['PCTIMESTRING'])
      # Save event details  
      event_p = {}
      event_p['SEASON_ID'] = gameid[:5] # SEASONID
      event_p['GAME_ID'] = gameid # GAMEID
      event_p['PERIOD'] = int(p['PERIOD']) # PERIOD
      event_p['PERIOD_REMAIN'] = period_remain
      event_p['SEC_ELAPSED'] = nsec_elapsed
      event_p['DURATION'] = duration
      event_p['SCORE_CHANGE'] = int(p['SCORE_CHANGE'])
      event_p['POSS_TYPE'] = int(poss_type)
      event_p['FTA'] = int(p['FTA'])
      event_p['FTM'] = int(p['FTM'])
      event_p['FGA_PTS'] = int(fga_pts)
  
      if home_isoff:
        event_p['OFF_TEAM'] = home
        event_p['DEF_TEAM'] = away
        event_p['OFF_PLAYERS'] = home_players.astype('int').tolist()
        event_p['DEF_PLAYERS'] = away_players.astype('int').tolist()
      else:
        event_p['OFF_TEAM'] = away
        event_p['DEF_TEAM'] = home
        event_p['OFF_PLAYERS'] = away_players.astype('int').tolist()
        event_p['DEF_PLAYERS'] = home_players.astype('int').tolist()
            
      # If not a foul, take description from offensive team
      if e_type != 6:
        if home_isoff:
          event_p['DESCRIPTION'] = h
        else:
          event_p['DESCRIPTION'] = v
        event_p['OFF_PLAYER'] = p['PLAYER1_ID']
      # If a foul, write free throw caption
      else:
        event_p['DESCRIPTION'] = '%s Free Throws, %d of %d' % (p['PLAYER2_NAME'], p['FTM'], p['FTA'])
        event_p['OFF_PLAYER'] = p['PLAYER2_ID']
  
      # write
      events.append(event_p)

  return events

#%% Main loop

def main():

  games = pd.read_csv(bb.REPOHOME + '/data/csv/games_96-15.csv')
#  games = games[(games['SEASON_ID']<=212) | (games['SEASON_ID']>250)]
  games = games[(games['SEASON_ID']>=212) & (games['SEASON_ID']<213)]
  #games = games[(games['SEASON_ID']>=213) & (games['SEASON_ID']<214)]
  #games = games[(games['SEASON_ID']>=214) & (games['SEASON_ID']<215)]
  #games = games[(games['SEASON_ID']>=215) & (games['SEASON_ID']<216)]
  #games = pd.read_csv(bb.REPOHOME + '/data/csv/games2016.csv')
  istart = 0
  for i,g in games.iloc[istart:].iterrows():
    gameid = '00' +  str(g['GAME_ID'])
    print gameid
    events = get_possessions(gameid)
    events_db.insert_many(events)

if __name__ == '__main__': 
  main()
