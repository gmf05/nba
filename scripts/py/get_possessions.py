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


def get_period_starters(gameid):
#%
  # Get box score information so we can see which
  # teams are home/away
  try:
    info_g = bb.get_boxscore_v2(gameid, box_type='summary')
  except:
    info_g = bb.get_boxscore(gameid)[2]      
  home = info_g['HOME_TEAM_ID'].values[0]

  # Get play-by-play so we can parse it
  pbp_g = bb.get_pbp(gameid) # play-by-play
    
  # Drop technical foul related activity since player who
  # commits one may not be on court
  pbp_g = pbp_g[pbp_g['EVENTMSGACTIONTYPE']!=16]
  desc = []
  for i,p in pbp_g.iterrows():
    h,v = p[['HOMEDESCRIPTION','VISITORDESCRIPTION']]
    if not h:
      desc.append(v)
    elif not v:
      desc.append(h)
    else:
      desc.append(h + ' ' + v)
  pbp_g['DESCRIPTION'] = desc
  idx = np.where([not bool(re.search('T.FOUL', str(p))) for p in pbp_g['DESCRIPTION'].values])[0]
  pbp_g = pbp_g.iloc[idx]
  
  # NOTE: there are sometimes extraneous EVENTMSGTYPE for quarter start (12)
  # or quarter end (13). They happen a couple times per season, but ruin all 
  # quarters after they happen. We check by making sure start/end indices
  # have right length and make sequential sense, using a helper function
  period_start, period_end = get_period_start_end(pbp_g)
  
  # Now we find starters for each period
  home_starters = []
  away_starters = []
  for m in range(len(period_start)):
    p_period = pbp_g.iloc[period_start[m]: period_end[m]]
    # Note : Last condition drops weird "team rebound" entries
    p_period = p_period[(p_period['PLAYER1_NAME']>0) & (p_period['EVENTMSGTYPE']<=11) & (p_period['PLAYER1_TEAM_ID']>0)]
    
    # Who is subbed out before they are subbed in?
    period_subs = p_period[p_period['EVENTMSGTYPE']==8]
    
    period_players = np.unique(np.union1d(np.union1d(p_period['PLAYER1_ID'].values, p_period['PLAYER2_ID'].values), 
                                          p_period['PLAYER3_ID'].values))
    # Drop player_id = 0
    period_players = np.delete(period_players, np.where(period_players==0)[0])
    # Drop Team IDs appearing in player ID list
    # e.g. team rebound
    period_players = np.delete(period_players, np.where(period_players>=1610000000)[0])
    # Drop any players where "persontype" = 7. Apparently, those are errors of some kind
    # Or placeholders
    period_players = np.setdiff1d(period_players, p_period[p_period.PERSON1TYPE==7].PLAYER1_ID.values)
    period_players = np.setdiff1d(period_players, p_period[p_period.PERSON2TYPE==7].PLAYER2_ID.values)
    #period_players = np.setdiff1d(period_players, p_period[p_period.PERSON3TYPE==7].PLAYER3_ID.values)
    
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
    
    # Players who started either never came out (p_neverout)
    # or were subbed out *before* being subbed in again (if at all) (p_out)
    p_neverout = player_subs[np.where(np.isinf(player_subs[:,1]) * np.isinf(player_subs[:,2]))[0], 0]
    p_out = player_subs[np.where(player_subs[:,1]<player_subs[:,2])[0], 0]
    period_starters = np.union1d(p_neverout, p_out)
  
    # Drop any extraneous players
    # OR: TODO!: if too few players, fix with box score    
    Nstarters = len(period_starters)
    if Nstarters<10:
      print 'Too few starters G=%s, Q=%d, N=%d' % (gameid,m+1,len(period_starters))
      # CAN WE SOLVE THIS WITH BOX SCORE MINUTES???
      # Somebody should have a quarter's worth of minutes
    elif Nstarters>10:
      print 'Too many starters G=%s, Q=%d, N=%d' % (gameid,m+1,len(period_starters))
      # Try to drop extra(s)
      # by picking who appears last in PBP order
      
      first_idx=[]
      for pl in period_starters:
        idx_pl = np.inf
        try:
          idx_pl = np.min([idx_pl, np.where(p_period['PLAYER1_ID']==pl)[0][0]])
          idx_pl = np.min([idx_pl, np.where(p_period['PLAYER2_ID']==pl)[0][0]])
          idx_pl = np.min([idx_pl, np.where(p_period['PLAYER3_ID']==pl)[0][0]])
        except:
          0
        first_idx.append(idx_pl)
      period_starters = period_starters[np.argsort(first_idx)[0:10]]

    home_idx = []
    away_idx = []
    for n,plyr in enumerate(period_starters):
      try:      
        if home == p_period[p_period['PLAYER1_ID']==plyr].iloc[0]['PLAYER1_TEAM_ID']:
          home_idx.append(n)
        else:
          away_idx.append(n)
      except:
        try:
          if home == p_period[p_period['PLAYER2_ID']==plyr].iloc[0]['PLAYER2_TEAM_ID']:
            home_idx.append(n)
          else:
            away_idx.append(n)
        except:
          try:
            if home == p_period[p_period['PLAYER3_ID']==plyr].iloc[0]['PLAYER3_TEAM_ID']:
              home_idx.append(n)
            else:
              away_idx.append(n)
          except:
            print 'Error', str(plyr)
    
    # Fill in -1 if total number of players < 5 for home/away
    home_players = period_starters[home_idx]
    Nhome = len(home_players)
    if Nhome<5:
      home_players = np.hstack((home_players, [-1 for n in range(5-Nhome)]))
    elif Nhome>5:
      print 'Too many home starters'
      home_players = home_players[0:5]
    away_players = period_starters[away_idx]
    Naway = len(away_players)
    if Naway<5:
      away_players = np.hstack((away_players, [-1 for n in range(5-Naway)]))
    elif Naway>5:
      print 'Too many away starters'
      away_players = away_players[0:5]

    home_starters.append(home_players)
    away_starters.append(away_players)
  
  return home_starters, away_starters

#%
def get_possessions(gameid):
  
  try:
    info_g = bb.get_boxscore_v2(gameid, box_type='summary')
  except:
    info_g = bb.get_boxscore(gameid)[2]

  home = info_g['HOME_TEAM_ID'].values[0]
  away = info_g['VISITOR_TEAM_ID'].values[0]

  pbp_g = bb.get_pbp(gameid) # play-by-play
  home_period_starters, away_period_starters = get_period_starters(gameid)
  
  home_score = 0
  #home_score_prev = 0
  away_score = 0
  #away_score_prev = 0
  # Some games (0029600002) don't have all quarter starts
  # This helps
  home_players = home_period_starters[0]
  away_players = away_period_starters[0]
  events = []
  period_remain_prev = 720.0
  # Assign first possession based on who wins initial jump ball:
  # If no jump ball exists, start with home on offense (doesn't matter)
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
  pbp_g['SCORECHANGE'] = np.hstack((0, np.diff(scores[:,0]) + np.diff(scores[:,1])))
  
  # make a table of FT "sessions"
  ft_sessions = pbp_g[pbp_g['EVENTMSGTYPE']==3][['PERIOD','PCTIMESTRING','PLAYER1_ID']].reset_index()
  # Drop technical free throws from ft_sessions
  ft_sessions = ft_sessions.iloc[np.where([(1-bool(re.search('Technical', str(pbp_g.iloc[i]['HOMEDESCRIPTION'])))) 
  * (1-bool(re.search('Technical', str(pbp_g.iloc[i]['VISITORDESCRIPTION'])))) for i in ft_sessions['index']])[0]]

  for i,p in pbp_g.iterrows():
    
    # Play description, number, type
    h = p['HOMEDESCRIPTION']
    v = p['VISITORDESCRIPTION']
    e_type = p['EVENTMSGTYPE']
      
    # Switch to handle different plays
    # Shots (1/2/3), turnover (5) and foul (6)
    # inform who's on offense (home_isoff)
    # Substituion (8) changes players oncourt
    # Start of quarter (12) changes players on court
    save_event = True
    poss_type = 1 # 1 : most events, 2 : and-one, 3 : technical FT
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
    if e_type==1:
      if h and (not v or re.search('Shot',h) or re.search('Layup',h) or re.search('Dunk',h)): home_isoff = True
      elif v and (not h or re.search('Shot',v) or re.search('Layup',v) or re.search('Dunk',v)): home_isoff = False
    elif e_type==2:
      if h and (not v or re.search('MISS',h)): home_isoff = True
      elif v and (not h or re.search('MISS',v)): home_isoff = False
    elif e_type==3:
      if h and (not v or re.search('Free Throw',h)): home_isoff = True
      elif v and (not h or re.search('Free Throw',v)): home_isoff = False
        
      # If it's first free throw, save "session" as one event
      # Also, if it's first and only free throw due to and-one -- tag poss_type
      # also, if it's technical free throw -- tag poss_type
      if (home_isoff and re.search('Free Throw 1', h)) or (not home_isoff and re.search('Free Throw 1', v)):
        # Change event data here to reflect "session" as opposed to 1 FT
        # idx = set of FTA associated with this session
        idx = ft_sessions[(ft_sessions['PERIOD']==p['PERIOD']) & (ft_sessions['PCTIMESTRING']==p['PCTIMESTRING']) 
                           & (ft_sessions['PLAYER1_ID']==p['PLAYER1_ID'])]['index'].values
        num_fta = len(idx)
        num_ft = np.sum(pbp_g['SCORECHANGE'].iloc[idx])
        p['SCORECHANGE'] = num_ft
        if home_isoff:
          h = h.split('(')[0].replace('Free Throw 1 of %d' % num_fta, 'Free Throws, %d of %d' % (num_ft, num_fta))
        else:
          v = v.split('(')[0].replace('Free Throw 1 of %d' % num_fta, 'Free Throws, %d of %d' % (num_ft, num_fta))
        # If it's an and-one note it
        if num_fta==1:
          poss_type = 2
      # Don't save subsequent free throws
      elif (home_isoff and re.search('Free Throw \d', h)) or (not home_isoff and re.search('Free Throw \d', v)):
        save_event = False
      # Save technical free throws, but add a tag so they don't count as possessions
      elif (home_isoff and re.search('Technical Free Throw', h)) or (not home_isoff and re.search('Technical Free Throw', v)):
        save_event = True
        poss_type = 0
        
    elif e_type==5:
      if h and (not v or re.search('Turnover',h)): home_isoff = True
      elif v and (not h or re.search('Turnover',v)): home_isoff = False
    # SUB (8)
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
    elif e_type==10: # Jump ball
      home_isoff = bool(p['PLAYER3_TEAM_ID']==home)
      save_event = False
    # START OF QUARTER (12)
    elif e_type==12:
      home_players = home_period_starters[p['PERIOD']-1]
      away_players = away_period_starters[p['PERIOD']-1]
      period_remain_prev = bb.clock2float(p['PCTIMESTRING'])*60.0
      save_event = False
    elif e_type==13:
      save_event = False
    else:
      save_event = False
      
    # Catch weird / out-of-order plays
    if p['SCORECHANGE']<0 or p['SCORECHANGE']>=4: 
      save_event = False
      
    if save_event:
      period_remain = bb.clock2float(p['PCTIMESTRING'])*60.0
      duration = period_remain_prev - period_remain
      period_remain_prev = period_remain
      # Save event details  
      event_p = {}
      event_p['SEASONID'] = gameid[:5] # SEASONID
      event_p['GAMEID'] = gameid # GAMEID
      event_p['PERIOD'] = int(p['PERIOD']) # PERIOD
      event_p['PERIODREMAIN'] = period_remain
      event_p['DURATION'] = duration
      event_p['EVENTTYPE'] = p['EVENTMSGTYPE'] # EVENTTYPE
      event_p['SCORECHANGE'] = int(p['SCORECHANGE'])
      event_p['POSSTYPE'] = int(poss_type)
      
      # if there's a score, update
      if p['SCORE']:
        away_score,home_score = [int(j) for j in p['SCORE'].split('-')]
  
      if home_isoff:
        #off_score = home_score
        #def_score = away_score
        event_p['OFFTEAM'] = home
        event_p['DEFTEAM'] = away
        event_p['OFFPLAYERS'] = home_players.astype('int').tolist()
        event_p['DEFPLAYERS'] = away_players.astype('int').tolist()
        #event_p['SCORECHANGE'] = int(home_score - home_score_prev)
      else:
        #off_score = away_score
        #def_score = home_score
        event_p['OFFTEAM'] = away
        event_p['DEFTEAM'] = home
        event_p['OFFPLAYERS'] = away_players.astype('int').tolist()
        event_p['DEFPLAYERS'] = home_players.astype('int').tolist()
        #event_p['SCORECHANGE'] = int(away_score - away_score_prev)
            
      if home_isoff:
        event_p['DESCRIPTION'] = h
      else:
        event_p['DESCRIPTION'] = v
      #event_p['OFFSCORE'] = off_score
      #event_p['DEFSCORE'] = def_score
      
      # write
      events.append(event_p)
      #away_score_prev = away_score
      #home_score_prev = home_score
  
  return events

#% Main loop

def main():

  games = pd.read_csv(bb.REPOHOME + '/data/csv/games_96-15.csv')
  #games = games[(games['SEASON_ID']>=212) & (games['SEASON_ID']<213)]
  #games = games[(games['SEASON_ID']>=213) & (games['SEASON_ID']<214)]
  games = games[(games['SEASON_ID']>=214) & (games['SEASON_ID']<215)]
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
