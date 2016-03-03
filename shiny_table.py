# -*- coding: utf-8 -*-
"""
Created on Thu Mar  3 09:44:34 2016

@author: gmf
"""

import numpy as np
import pandas as pd
import bb_tools as bb

# Get the current players.
players = bb.get_players_current()
nplayers = len(players)

# Get potential AST & FT AST numbers.
pass_stats = bb.get_sportvu_stats('passing')

# This data frame will be the displayed stat table.
player_stats = pd.DataFrame(data=players.PERSON_ID.values, columns=['PLAYER_ID'])
player_stats['PLAYER_NAME'] = players.DISPLAY_FIRST_LAST
player_stats['TEAM_ID'] = players.TEAM_ID

# Now cycle through players
# and compute Scoring Opportunities Created (SO)
# and Scoring Opportunities per Play (SOPP)

# These arrays will be counters.
so = 0.0*np.arange(nplayers)
sopp = 0.0*np.arange(nplayers)

for n,p in player_stats.iterrows():
  print n,p.PLAYER_NAME
  # Get player totals.
  # If player hasn't played (empty gamelog)
  # then skip.
  try:
    l = bb.get_player_gamelog(p.PLAYER_ID)
  except ValueError:
    print 'Error : ' + p.PLAYER_NAME + ' not found in Game logs!'    
    continue
  #gp = len(l)
  fga=np.sum(l.FGA)  
  fgm=np.sum(l.FGM)
  fta=np.sum(l.FTA)
  tov=np.sum(l.TOV)
  oreb=np.sum(l.OREB)
  mp=np.sum(l.MIN)

  # Get relevant potential ast, ft ast data.
  # Units are per game by default, so we convert to total
  # by multiplying by GP
  try:
    temp = np.where(pass_stats.PLAYER_ID==str(p.PLAYER_ID))[0]
    if len(temp)==0:
      temp = np.where(pass_stats.PLAYER==p.PLAYER_NAME)[0]
    idx = temp[0]
  except IndexError:
    print 'Error : ' + p.PLAYER_NAME + ' not found in SportVu Passing!'    
    continue
  ast_pot=pass_stats.AST_POT[idx]*pass_stats.GP[idx]
  ast_ft=pass_stats.AST_FT[idx]*pass_stats.GP[idx]
  
  # Get team totals for *this player's games*
  # Note, needing player-specific totals
  # is why we compute *inside* loop rather 
  # than outside.
  #
  # Note 2: We do this after passing data in case
  # passing data isn't found
  #
  # NOTE 3: Still need to fix conditions when players
  # have been traded and current TEAM ID 
  # is not equal to either team in boxscore for old team
  team_mp=0.0
  team_plays=0.0
  for g in l.Game_ID:
    # Is this player home or away?
    summary = bb.get_boxscore(g)[0].iloc[0]
    if p.PLAYER_TEAMID == summary.HOME_TEAM_ID:
      homeaway=0 # home
    elif p.PLAYER_TEAMID == summary.VISITOR_TEAM_ID:
      homeaway=1 # away
    else: # uh-oh...
      # If we get here, then player has been traded!
      # need to fill this in
      print g,p.PLAYER_NAME
      homeaway=0
    # Add team totals for this game.
    team_box = bb.get_boxscore(g)[5].iloc[homeaway]
    team_mp += bb.clock2float(team_box.MIN)
    team_plays += team_box.FGA + 0.44*team_box.FTA + team_box.TO

  # Compute SO, SOPP.
  so[n] = fga+0.44*float(fta)+tov+ast_pot+ast_ft+oreb
  sopp[n] = float(so[n])/team_plays * (team_mp/5 / mp )

# Save results.
player_stats['SO'] = so
player_stats['SOPP'] = sopp

# Print to CSV for R
player_stats.to_csv('shiny_table.csv')
