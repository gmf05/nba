# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 08:56:33 2016

@author: gmf
"""
# Note: Put this file in the same directory as data, or else
# modify paths below

# Import modules
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.animation as animation

# Data paths
box2014_file = 'Hackathon_nba_2014-15_sv_box_scores.txt'
box2015_file = 'Hackathon_nba_2015-16_sv_box_scores.txt'
#pbp_file = 'Hackathon_play_by_play.txt'
players_file = 'Hackathon_player_names_matched_team.txt'
hustle2016_file = 'Hackathon_playoff_hustle_stats_2016.txt'
possession2014_file = 'Hackathon_sv_possession_summary_2014-15.txt'
possession2015_file = 'Hackathon_sv_possession_summary_2015-16.txt'
sv2016_file = 'Hackathon_sv_raw_playoff_2016.txt'
reb2014_file = 'Hackathon_sv_rebound_summary_2014-15.txt'
reb2015_file = 'Hackathon_sv_rebound_summary_2015-16.txt'
shots2014_file = 'Hackathon_sv_shot_summary_2014-15.txt'
shots2015_file = 'Hackathon_sv_shot_summary_2015-16.txt'

# Load data
box2014 = pd.read_table(box2014_file, delimiter='\t')
box2015 = pd.read_table(box2015_file, delimiter='\t')
reb2014 = pd.read_table(reb2014_file, delimiter=' ')
reb2015 = pd.read_table(reb2015_file, delimiter=' ')
shots2014 = pd.read_table(shots2014_file, delimiter=' ')
shots2015 = pd.read_table(shots2015_file, delimiter=' ')
#pbp = pd.read_table(pbp_file, delimiter=' ') # fairly large (1 GB). may need to read in chunks
players = pd.read_table(players_file, delimiter=' ')
#hustle2016 = pd.read_table(hustle2016_file, delimiter=' ')
poss2014 = pd.read_table(possession2014_file, delimiter=' ')
poss2015 = pd.read_table(possession2015_file, delimiter=' ')
#sv2016 = pd.read_table(sv2016_file, delimiter=' ', nrows = 10**4) # LARGE (4 GB). may need to read in chunks
#sv2016 = pd.read_table(sv2016_file, delimiter=' ', chunksize = 10**4) # LARGE (4 GB). may need to read in chunks

# Helper functions
# Data grabbing functions for player info
def get_player_id_by_name(p_name):  
  return players[players['Name']==p_name].iloc[0]['Person_id']

def get_player_name_by_id(p_id):  
  return players[players['Person_id']==p_id].iloc[0]['Name']

# 
def draw_halfcourt(axis=[0,50,0,47]):
  img = mpimg.imread('HalfCourt.jpeg')
  img = img[:-22, :, :] # crop top
  plt.imshow(img,extent=axis, zorder=0)
  #plt.gca().axis('off')

def draw_fullcourt(axis=[0,94,0,50]): 
  img = mpimg.imread('FullCourt_copy.png') # load cropped, centered version
  plt.imshow(img,extent=axis, zorder=0)
  #plt.gca().axis('off')

# Stats
# Link / inverse link for logistic regression
def logit(x):
  x = np.array(x)
  return np.log(np.divide( x, (1.0 - x) ))

def logistic(x):
  #x = np.array(x)
  return np.divide( 1.0 , (1.0 + np.exp(-x)) )

# Model fitting 
def irls(X,y,link):
  y = np.matrix(y).T # Want column vector!!
  if link=='identity':
    def link_fun(x): return x
    def ilink_fun(x): return x
    def ilink_prime(x): return np.ones_like(x)
    def sqrtvar_fun(x): return np.ones_like(x)
    mu = np.copy(y)  
  elif link=='log':
    def link_fun(x): return np.log(x)
    def ilink_fun(x): return np.exp(x)
    def ilink_prime(x): return np.divide(1.0, x)
    def sqrtvar_fun(x): return np.sqrt(x)
    mu = np.copy(y) + 0.25
  elif link=='logit': # TODO: NEEDS UPDATE!!!
    def link_fun(x): return x
    def ilink_fun(x): return x
    def ilink_prime(x): return np.ones_like(x)
    def sqrtvar_fun(x): return np.ones_like(x)
    mu = np.copy(y)  
  else:
    raise ValueError('Link function `%s` not recognized' % link)

  # Initialize arrays    
  NT,Np = X.shape
  pwts = np.ones([NT,1])
  b = np.ones([Np,1])
  C = np.eye(Np)
  R = np.eye(Np)
  eta = ilink_fun(mu)
  
  # Stopping parameters
  epsilon = 1e-6
  offset = 1e-3
  iter_lim = 100
  
  for iter in range(iter_lim):    
    #print 'IRLS Iteration %d' % iter
    #z = eta - offset + (y-mu) * ilink_prime(mu)   
    z = eta - offset + np.multiply((y-mu), ilink_prime(mu))
    b_old = b.copy()
    R_old = R.copy()
    deta = ilink_prime(mu)
    sqrtirls = np.multiply( np.abs(deta), sqrtvar_fun(mu) )
    sqrtw = np.divide(np.sqrt(pwts), sqrtirls)
    
    # Orthogonal (QR) decomposition of Xw
    # Avoids forming the product Xw.T * Xw
    #zw = z * sqrtw
    #Xw = X * sqrtw[:, [0 for i in range(Np)]]
    zw = np.multiply(z, sqrtw)    
    Xw = np.multiply(X, sqrtw[:, [0 for i in range(Np)]])
    Q,R = np.linalg.qr(Xw)
    try:
      b,Z1,Z2,Z3 = np.linalg.lstsq(R, np.dot(Q.T, zw))
    except ValueError:
      b = b_old.copy()
      R = R_old.copy()
      print 'ValueError at iteration %d' % iter
      break
    
    # Checks:
    # 1. Have we encountered numerical error/flat likelihood?
    cond_num = np.linalg.cond(R)
    if cond_num < 1e-8 or np.any(np.isnan(b)):
      b = np.copy(b_old)
      R = np.copy(R_old)
      break
    if cond_num < 1e-8 or np.isnan(cond_num):
      print 'Warning! Likelihood is flat.'
    # 2. Have we converged?
    if np.linalg.norm(b - b_old, np.inf) < epsilon:
      print 'Converged in %d steps.' % iter
      break
    
    # Update coefficients, covariance
    eta = offset + np.dot(X,b)
    mu = ilink_fun(eta)
    RI,Z1,Z2,Z3 = np.linalg.lstsq(R, np.eye(Np))
    C = np.dot(RI , RI.T)
    #C = np.multiply(C , s**2) # Right now: Assumes no over/under-dispersion (s=1)
    
    #  Correct bad parameter estimates
    #if eta[1] > 1.0: eta[1]=1.0
    #mu[-2] = -10.0
    
  return b,C


# #%% Spline functions


# Parameters for spline
P = 3 # degree : 
# Note: Smoothness on interior is C^P everywhere...
# Adding a knot with multiplicity k reduces the smoothness
# at that point to C^P-k
# 

# Pad end points of knot sequence to get C^0 smooth ()
def pad_knots(knots, P):
  return np.hstack([np.ones(P)*knots[0], knots, np.ones(P)*knots[-1]])

# 
def splinebasisX(knots, du=1, P=3):
  knots = pad_knots(knots, P)
  Nk = len(knots)

  # Axis along which we want to compute the basis functions
  u_axis = np.arange(knots[0], knots[-1]+du, du)
  Nu = len(u_axis)
  u_axis_spans = range(Nu)
    
  # Empty array for basis function values
  N = np.zeros([Nk - P, P+1, Nu])
  X = np.zeros([Nu, Nk - P])
  
  # Find spans
  for n,u in enumerate(u_axis):
    # Note: we need >= rather than > here to work at right-endpoints
    # with multiplicity (e.g. u=1)
    idx = np.where((knots[0:-1]<=u) & (knots[1:]>=u))[0][0]
    # ^^ Also, we can speed up this search with a counter & if statement
    #
    u_axis_spans[n] = idx
    N[idx,0,n] = 1
  #u_axis_spans[-1] = u_axis_spans[-2]+1
  
  # Compute basis functions
  # CAN WE RE-ARRANGE THE FOR LOOPS BELOW
  # AND VECTORIZE?
  for p in range(1,P+1):
    for n,u in enumerate(u_axis):
      #i = u_axis_spans[n]
      idx = u_axis_spans[n] + np.arange(-p-1, 1)
      for i in idx:
        alpha1 = np.divide( (u - knots[i]) , (knots[i+p] - knots[i]) )
        alpha2 = np.divide( (knots[i+p+1]-u), (knots[i+p+1] - knots[i+1]) )
        if np.isnan(alpha1) or np.isinf(alpha1):
          alpha1 = 0.0
        if np.isnan(alpha2) or np.isinf(alpha2):
          alpha2 = 0.0
        # Cox-deBoor recursion formula:
        N[i,p,n] = alpha1 * N[i,p-1,n] + alpha2 * N[i+1, p-1, n]
      
      #X[n,idx] = N[idx,P,n]
  X = N[:,P,:].T
  X[0,0]=1
  
  return X

def splineconf(X0, coeff, cov=0, s=0.5, Z=2):
  y = np.squeeze(np.array(np.dot(X0, coeff)))
  yhi = y + Z * np.sqrt(np.diag(np.dot(X0,np.dot(cov,X0.T)))) # Z=2: 95% CI
  ylo = y - Z * np.sqrt(np.diag(np.dot(X0,np.dot(cov,X0.T)))) # Z=2 : 95% CI
  return y, yhi, ylo

#% Fit hazard model for one player

#import statsmodels.api as sm

def fit_fg_hazard(shots):

  # Make data vector y
  y = (shots['PTS']>0).astype('int')    
    
  # Make knots & design matrix X
  #knots_x = [0, 5, 15, 36]
  #knots_y = [0, 5, 16]
  knots_x = [0, max_o_dist]
  knots_y = [0, max_d_dist]
  X_x = splinebasisX(knots_x)
  X_y = splinebasisX(knots_y)

  ix = np.round(shots['SHOT_DIST'].values).astype('int')
  iy = np.round(shots['CLOSE_DEF_DIST'].values).astype('int')
  
  X = np.hstack([X_x[ix,:], X_y[iy,:]])
  
  # Fit model
  b,C = irls(X,y,'logit')
  # break up b into b_x, b_y
  # RECONSTRUCT SURFACE
  x_axis = np.arange(knots_x[0], knots_x[-1]+1)
  y_axis = np.arange(knots_y[0], knots_y[-1]+1)
  xs, ys = np.meshgrid(x_axis, y_axis)
  Z = np.zeros(xs.shape)
  
  for i in range(Z.shape[0]):
    for j in range(Z.shape[1]):
      Z[i,j] = np.dot(np.hstack([X_x[xs[i,j], :], X_y[ys[i,j],:]]), b)
  
  Z[Z<0]=0
  return Z*100 # scale percent
  #return Z*100,Zhi*100,Zlo*100 # scale percent
  

def fit_epv(shots):

  # Make data vector y
  #y = (shots['PTS']>0).astype('int')
  y = (shots['PTS']).astype('int')
    
  # Make knots & design matrix X
  #knots_x = [0, 5, 15, 35]
  #knots_y = [0, 5, 15]
  #knots_x = [0, max_o_dist]
  #knots_y = [0, max_d_dist]
  knots_x = [0, np.round(max_o_dist/2.0), max_o_dist]
  knots_y = [0, np.round(max_d_dist/2.0), max_d_dist]
  X_x = splinebasisX(knots_x)
  X_y = splinebasisX(knots_y)

  ix = np.round(shots['SHOT_DIST'].values).astype('int')
  iy = np.round(shots['CLOSE_DEF_DIST'].values).astype('int')
  
  X = np.hstack([X_x[ix,:], X_y[iy,:]])
  
  # Fit model
  b,C = irls(X,y,'log')
  # break up b into b_x, b_y
  # RECONSTRUCT SURFACE
  x_axis = np.arange(knots_x[0], knots_x[-1]+1)
  y_axis = np.arange(knots_y[0], knots_y[-1]+1)
  xs, ys = np.meshgrid(x_axis, y_axis)
  Z = np.zeros(xs.shape)
  
  for i in range(Z.shape[0]):
    for j in range(Z.shape[1]):
      Z[i,j] = np.dot(np.hstack([X_x[xs[i,j], :], X_y[ys[i,j],:]]), b)
  
  return Z


def fit_shotchart(shots):

  # Make data vector y
  #y = (shots['PTS']>0).astype('int')
  y = shots['SHOT_MADE_FLAG'].values
    
  # Make knots & design matrix X
  #knots_x = [0, 5, 15, 35]
  #knots_y = [0, 5, 15]
  #knots_x = [0, max_o_dist]
  #knots_y = [0, max_d_dist]
  #court_dim = [50, 47]
  court_dim = [50, 30] 
  knots_x = [0, np.round(court_dim[0]/2.0), court_dim[0]]
  knots_y = [0, np.round(court_dim[1]/2.0), court_dim[1]]
  X_x = splinebasisX(knots_x)
  X_y = splinebasisX(knots_y)

  ix = [np.min([np.round((x0+250)/10.0), 50]) for x0 in shots['LOC_X'].values]
  iy = [np.min([np.round(y0/10.0), 47]) for y0 in shots['LOC_Y'].values]
  
  X = np.hstack([X_x[ix,:], X_y[iy,:]])
  X = np.hstack([np.ones([X.shape[0],1]), X])
  
  # Fit model
  b,C = irls(X,y,'log')
  # break up b into b_x, b_y
  # RECONSTRUCT SURFACE
  x_axis = np.arange(knots_x[0], knots_x[-1]+1)
  y_axis = np.arange(knots_y[0], knots_y[-1]+1)
  xs, ys = np.meshgrid(x_axis, y_axis)
  Z = np.zeros(xs.shape)
  
  for i in range(Z.shape[0]):
    for j in range(Z.shape[1]):
      #Z[i,j] = np.dot(np.hstack([X_x[xs[i,j], :], X_y[ys[i,j],:]]), b)
      Z[i,j] = np.dot(np.hstack([1, X_x[xs[i,j], :], X_y[ys[i,j],:]]), b)
  
  return Z

#%% Hazard model for all shots 2014 & 2015

# Start with all shots <= 35 ft away
shots = pd.concat((shots2014, shots2015))
max_o_dist = 35
max_d_dist = 10
shots = shots[shots['SHOT_DIST']<=max_o_dist]
shots = shots[shots['CLOSE_DEF_DIST']<=max_d_dist]

Z = fit_fg_hazard(shots)
#Z = fit_epv(shots)

## Individual heatmap
#p_id = get_player_id_by_name('James Harden')
##p_id = get_player_id_by_name('Harrison Barnes')
#shots_p = shots[shots['PERSON_ID']==p_id]
#Z = fit_fg_hazard(shots_p)

plt.figure()
plt.imshow(Z)

plt.figure()
plt.plot(Z[0,:], 'b')
plt.plot(Z[-1,:], 'r')
#plt.plot(Z[:,0], 'b')
#plt.plot(Z[:,30], 'r')


#%% Compare player heatmaps

# Start with all shots <= 35 ft away
shots = pd.concat((shots2014, shots2015))
max_o_dist = 35
max_d_dist = 10
shots = shots[shots['SHOT_DIST']<=max_o_dist]
shots = shots[shots['CLOSE_DEF_DIST']<=max_d_dist]

id1 = get_player_id_by_name('James Harden')
shots1 = shots[shots['PERSON_ID']==id1]
Z1 = fit_fg_hazard(shots1)

#id2 = get_player_id_by_name('Andre Drummond')
#id2 = get_player_id_by_name('Stephen Curry')
#id2 = get_player_id_by_name('Isaiah Thomas')
id2 = get_player_id_by_name('Tim Duncan')
shots2 = shots[shots['PERSON_ID']==id2]
Z2 = fit_fg_hazard(shots2)

plt.figure()

plt.subplot(211)
plt.imshow(Z1)
plt.colorbar()
plt.gca().invert_yaxis()

plt.subplot(212)
plt.imshow(Z2)
plt.colorbar()
plt.gca().invert_yaxis()

#%% Get nice smooth shotchart << needs work
# Specifically:  needs more control points

max_y = 30
shots = range(100)
for g in range(100):
  s = bb.get_shots('0021400001')
  sy = np.array([np.min([np.round(y0/10.0), 47]) for y0 in s['LOC_Y'].values])
  s = s[sy<=30]
  shots[g] = s
shots = pd.concat(shots)

Z = fit_shotchart(shots)

plt.figure()
plt.imshow(Z)
plt.gca().invert_yaxis()


#%% Getting offensive efficiencies for a whole team's five-man lineup.

team_players = ['Stephen Curry', 'Klay Thompson', 'Kevin Durant', 'Draymond Green', 'Zaza Pachulia']
Zs = range(5)
for n in range(5):
  id_n = get_player_id_by_name(team_players[n])
  shots_n = shots[shots['PERSON_ID']==id_n]
  Zs[n] = fit_fg_hazard(shots_n)
  
  
#%%
  
