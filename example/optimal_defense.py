# -*- coding: utf-8 -*-
"""
Created on Sat Sep 24 13:36:36 2016

@author: gmf
"""
##%%

#import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from scipy.spatial import Voronoi, Delaunay, ConvexHull

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
#box2014 = pd.read_table(box2014_file, delimiter='\t')
#box2015 = pd.read_table(box2015_file, delimiter='\t')
#reb2014 = pd.read_table(reb2014_file, delimiter=' ')
#reb2015 = pd.read_table(reb2015_file, delimiter=' ')
shots2014 = pd.read_table(shots2014_file, delimiter=' ')
shots2015 = pd.read_table(shots2015_file, delimiter=' ')

#%% Make spatial map of shot values
# May need slight tweaking around 3-pt line edge

court_shot_value = np.zeros([court_dim[3], court_dim[1]])

for i in range(court_dim[3]):
  for j in range(court_dim[1]):
    dist_ij = player_dist_basket([i,j])
    if dist_ij < 22: # inside (short) 3 pt line 22'
      court_shot_value[i,j] = 2.0
    elif dist_ij >= 23.75: # outside (far) 3 pt line 23' 9"
      court_shot_value[i,j] = 3.0
    else: # mid-range (between short and long 3-pt line)
      if i<=14: # corner 3 in effect
        if dist_ij < 22: # inside (short) 3 pt line 22'
          court_shot_value[i,j] = 2.0
        else: # outside (far) 3 pt line 23' 9"
          court_shot_value[i,j] = 3.0
      else: # corner 3 *NOT* in effect
        if dist_ij < 23.75: # inside (short) 3 pt line 22'
          court_shot_value[i,j] = 2.0
        elif dist_ij >= 23.75: # outside (far) 3 pt line 23' 9"
          court_shot_value[i,j] = 3.0
            
draw_halfcourt()
plt.imshow(court_shot_value, alpha=0.5)

    


#%% Getting offensive efficiencies for a whole team's five-man lineup.

# Helper functions

# Data grabbing functions for player info
players_file = 'Hackathon_player_names_matched_team.txt'
players = pd.read_table(players_file, delimiter=' ')
def get_player_id_by_name(p_name):  
  return players[players['Name']==p_name].iloc[0]['Person_id']

def get_player_name_by_id(p_id):  
  return players[players['Person_id']==p_id].iloc[0]['Name']

def player_dist(coord1, coord2):
  return np.linalg.norm(np.array(coord1)-np.array(coord2))

def player_dist_basket(coord1):
  return np.linalg.norm(np.array(coord1)-np.array([5.25, 25]))
  
court_dim = [0, 50, 0, 47]
def draw_halfcourt(axis=court_dim):
  img = mpimg.imread('HalfCourt.jpeg')
  img = img[:-22, :, :] # crop top
  plt.imshow(img,extent=axis, zorder=0)
  #plt.gca().axis('off')
  
# Stats functions

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
  
  
def plot_player_efficiency(player_name):
  pid = get_player_id_by_name(player_name)
  shots_p = shots[shots['PERSON_ID']==pid]
  eff = fit_fg_hazard(shots_p)
  plt.imshow(eff)
  plt.title(player_name)
  plt.xlabel('FG Distance')
  plt.ylabel('Defender Distance')
  plt.clim([0,100])
  plt.colorbar()
  
#%% Preliminary steps: Find offensive efficiencies,
# initialize coordinates, compute initial inter-player 
# distances.

# Get list of shots to be used for estimating
# efficiecnies
shots = pd.concat((shots2014, shots2015))
max_o_dist = 35
max_d_dist = 10
shots = shots[shots['SHOT_DIST']<=max_o_dist]
shots = shots[shots['CLOSE_DEF_DIST']<=max_d_dist]

# Get efficiencies for a team
team_players = ['Stephen Curry', 'Klay Thompson', 'Kevin Durant', 'Draymond Green', 'Zaza Pachulia']
#team_players = ['Shaun Livingston', 'Klay Thompson', 'Kevin Durant', 'Draymond Green', 'Zaza Pachulia']
#team_players = ['Shaun Livingston', 'Klay Thompson', 'Andre Iguodala', 'Draymond Green', 'Zaza Pachulia']
#team_players = ['Shaun Livingston', 'Ian Clark', 'Andre Iguodala', 'Draymond Green', 'Zaza Pachulia']
efficiencies = range(5)
for n in range(5):
  id_n = get_player_id_by_name(team_players[n])
  shots_n = shots[shots['PERSON_ID']==id_n]
  efficiencies[n] = fit_fg_hazard(shots_n)

# Set player coordinates. 
# O are fixed. D will change with algorithm
#o_coord = np.array([[30,25], [28,40], [19,17], [3,3], [15,30]])
#o_coord = np.array([[30,25], [19,17], [28,40], [3,3], [15,30]])
o_coord = np.array([[30,25], [3,3], [28,40], [17,17], [15,30]])
#d_coord = np.array([[30,25], [19,17], [28,40], [3,3], [19,17]])
d_coord = np.array([[0,0], [0,0], [0,0], [0,0], [0,0]])

# Initialize inter-player distance matrix
inter_player_dist = np.zeros([5,5])
for i in range(5):
  for j in range(5):
    inter_player_dist[i,j] = player_dist(o_coord[i,:], d_coord[j,:])

#%% Run optimizer

# dist_efficiency = fit_fg_hazard(shots) # defense distance x offense distance

#update_i+=1

#update_i=np.random.randint(5)
#update_i = 4
#def optimal_def_coord(o_coord, d_coord, inter_player_dist, update_i):

#for update_i in [0,1,0,1,2,0,1,2,3,0,1,2,3,4]:
for update_i in [0]:
  
  # Arrays for storing EPV, defenders' distance.
  # Optimal position will search for min's across these arrays
  epv = np.zeros([court_dim[3], court_dim[1]])
  d_dist_basket = np.copy(epv)
  
  # Get offensive players' potential FG values
  # TODO: find this automatically from offense positions
  # make a grid with shot-values
  o_shot_value = court_shot_value[o_coord[:,0], o_coord[:,1]]
  #o_shot_value = np.array([3.0, 3.0, 3.0, 2.0, 2.0])
  
  # Get offensive players' distance from the basket
  o_dist = np.zeros(5)
  for n in range(5):
    o_dist[n] = player_dist_basket(o_coord[n,:]).round()
    #o_shot_value[n] = 0.0
  
  # Populate EPV, distance arrays
  for i in range(court_dim[3]):
    for j in range(court_dim[1]):
      d_coord_test = np.array([i,j]) # x,y format
      # get inter-player distances
      for n in range(5):      
        inter_player_dist[n,update_i] = player_dist(o_coord[n,:], d_coord_test)
      
      # get addiitonal offense-to-defense distances
      # for each offensive player, take "pressured" D distance to be min
      # 
      epv_by_o = np.zeros(5)
      for n in range(5):
        d_dist_n = np.min([inter_player_dist[n,:].min().round(), 10])
        epv_by_o[n] = efficiencies[n][d_dist_n, o_dist[n]]/100.0 * o_shot_value[n]
      
      # NOTE: How we compute this is critical
      # TODO: Should be thoughtfully re-assessed
      epv[i,j] = epv_by_o.max()  # THIS NEEDS TWEAKING
      #epv[i,j] = epv_by_o.mean()
      d_dist_basket[i,j] = player_dist_basket(d_coord_test)
      
  # Primary optimization: Where is EPV minimized?
  imax, jmax = np.where(epv==np.min(epv))
  #print len(imax),len(jmax) # debug: "is the optimum unique?"
  
  # Secondary optimization:
  # if there are multiple optima, next minimize distance to basket 
  # TODO?: (1) Instead find max player "real estate"  i.e. area in a Voronoi diagram
  # OR (2) instead, sag towards the midpoint of basket and next-nearest offender
  #
  # 
  # Trying (1):
  #d_area = polyarea2D(ConvexHull(d_coord).points)
  if len(imax)>=0:
    dual_max = np.argmin([d_dist_basket[imax[n],jmax[n]] for n in range(len(imax))])
    # Pick randomly if there are many?
    imax = imax[dual_max]
    jmax = jmax[dual_max]
  
  # Save optimal coordinates.
  # Update inter-player distance matrix.
  d_coord[update_i, :] = [imax, jmax]
  for n in range(5):
    inter_player_dist[n,update_i] = player_dist(o_coord[n,:], d_coord[update_i,:])
    
  #  return d_coord, inter_player_dist, epv # note: row, column (y, x) format returned
  
  #% Plotting optimal position over iterations
  # QUESTION:
  # How can we cycle through all 5 players and not have them matched up man-to-man??
  # Is there a bug??
  # Somehow it seems players still don't "know" when offenders are already covered...
  # 
  # 
#%
  # 
  #rand_i = np.random.randint(5)
  #d_coord, inter_player_dist, epv = optimal_def_coord(o_coord, d_coord, inter_player_dist, rand_i)
  
  # Plotting
  #plt.cla()
  plt.figure()
  draw_halfcourt()
  #plt.imshow(epv, alpha=0.5)
  plt.gca().invert_yaxis()
  
  for n in range(5):
    plt.plot(o_coord[n,1], o_coord[n,0], 'o', color='b', markersize=10)
    #plt.text(o_coord[n,1], o_coord[n,0], str(n+1), color='w')
    plt.text(o_coord[n,1]-5.0, o_coord[n,0]+2.5, team_players[n].split(' ')[1], color='w', fontsize=16)
    
    plt.plot(d_coord[n,1], d_coord[n,0], 'o', color='r', markersize=10)
    #plt.text(d_coord[n,1]-0.5, d_coord[n,0]+1.5, str(n+1), color='w')
    
    #idx = np.argmin(inter_player_dist[:,n])    
    #plt.text(o_coord[idx,1]+2.5, o_coord[idx,0]-1.0, str(n+1), color='w')
    
  plt.xlim([court_dim[0], court_dim[1]])
  plt.ylim([court_dim[2], court_dim[3]])
  #plt.axis('off')
  
  #plt.clim([0.5,1.5])
  #plt.axis('off')
  #plt.colorbar()
  
  #for n,t in enumerate(team_players): print n+1,t
  #plt.pause(2)



# # Voronoi scraps  
#from scipy.spatial import Voronoi, voronoi_plot_2d
#vor = Voronoi(np.vstack([o_coord,d_coord]))
#voronoi_plot_2d(vor)
#plt.show()



#%% Simulated Annealing example
#% Initialization 

#o_shot_value[o_coord[:,0],o_coord[:,1]]
o_shot_value = np.array([3.0, 2.0, 3.0, 3.0, 2.0])

# Set player coordinates. 
# O are fixed. D will change with algorithm
#o_coord = np.array([[30,25], [28,40], [19,17], [3,3], [15,30]])
#o_coord = np.array([[30,25], [19,17], [28,40], [3,3], [15,30]])
o_coord = np.array([[30,25], [3,3], [28,40], [17,17], [15,30]])

# Get offensive players' distance from the basket
o_dist = np.zeros(5)
for n in range(5):
  o_dist[n] = player_dist_basket(o_coord[n,:]).round()

# Get offensive players' efficiencies
# First, grab training data
shots = pd.concat((shots2014, shots2015))
max_o_dist = 35
max_d_dist = 10
shots = shots[shots['SHOT_DIST']<=max_o_dist]
shots = shots[shots['CLOSE_DEF_DIST']<=max_d_dist]

# Now fit models
team_players = ['Stephen Curry', 'Klay Thompson', 'Kevin Durant', 'Draymond Green', 'Zaza Pachulia']
#team_players = ['Shaun Livingston', 'Klay Thompson', 'Kevin Durant', 'Draymond Green', 'Zaza Pachulia']
#team_players = ['Shaun Livingston', 'Klay Thompson', 'Andre Iguodala', 'Draymond Green', 'Zaza Pachulia']
#team_players = ['Shaun Livingston', 'Ian Clark', 'Andre Iguodala', 'Draymond Green', 'Zaza Pachulia']
efficiencies = range(5)
for n in range(5):
  id_n = get_player_id_by_name(team_players[n])
  shots_n = shots[shots['PERSON_ID']==id_n]
  efficiencies[n] = fit_fg_hazard(shots_n)


#% Simulated annealing

# Helper functions 

def polyarea2D(pts):
    lines = np.hstack([pts,np.roll(pts,-1,axis=0)])
    area = 0.5*abs(sum(x1*y2-x2*y1 for x1,y1,x2,y2 in lines))
    return area

# Draw intiial state
def initial_state(court_dim=[0,50,0,47]):
  xs = np.random.randint(court_dim[0], court_dim[1]+1, [5,1])
  ys = np.random.randint(court_dim[0], court_dim[1]+1, [5,1])
  return np.hstack([xs,ys])

# Draw potential new state
def neighbor_state(d_coord, court_dim=[0,50,0,47]):
  # One possibility : move randomly  
#  d_coord += np.random.randint(-1, 2, [5,2])
  
  # Or, instead of moving randomly
  # Pull (random) d player towards (random) o player
  # 
  i,j = np.random.randint(0,5,2)
  d_coord[i,:] += np.random.randint(-1, 2, 2)
  #d_coord[i,:] += np.round(0.5 * (o_coord[j,:] - d_coord[i,:]))
  #d_coord[i,:] += np.round(0.1 * (o_coord[j,:] - d_coord[i,:]))
  #d_coord[i,:] += np.round( (1-np.exp(T)) * (o_coord[j,:] - d_coord[i,:]))

#  # Make sure no one is off of court
  d_coord[ d_coord[:,0]<court_dim[0], 0] = court_dim[0]
  d_coord[ d_coord[:,0]>court_dim[1], 0] = court_dim[1]
  d_coord[ d_coord[:,1]<court_dim[2], 1] = court_dim[2]
  d_coord[ d_coord[:,1]>court_dim[3], 1] = court_dim[3]

  return d_coord

# Simulated Annealing functions
# Cooling schedule
# T(t) = d*log(t)
def temperature(t):  
  return 10.0 / np.log(t)
  
# Energy function depending on temperature T
# and EPV's (& Voronoi??)
def energy(d_coord):
  # Compute distances b/w players
  # and compute EPV of each offensive player
  inter_player_dist = np.zeros([5,5])
  epv_by_o = np.zeros(5)
  basket_dist = np.zeros(5)
  for i in range(5):
    for j in range(5):
      inter_player_dist[i,j] = player_dist(o_coord[i], d_coord[j])
    d_dist_i = np.min([inter_player_dist[i,:].min().round(), 10])
    basket_dist[i] = player_dist_basket(d_coord[i,:])
    epv_by_o[i] = efficiencies[i][d_dist_i, o_dist[i]]/100.0 * o_shot_value[i]
  

  # Now Energy = max EPV
  # However we could add penalty terms
  #d_area = polyarea2D(ConvexHull(d_coord).points)
  #my_energy = epv_by_o.max() #+ 0.01*np.sum(basket_dist)
  my_energy = epv_by_o.mean() #- 1e-4*d_area + 0.01*np.sum(basket_dist)
  return my_energy

# Acceptance probability function
# Defined here same as Kilpatrick et al., 
def acceptance_prob(energy_old, energy_new, T):
  if energy_old > energy_new:
    return 1
  else:
    return np.exp(-1.3 * (energy_new-energy_old)/T)

d_coord = initial_state()
print d_coord

# Find state 
max_iter = 5000
for iter in range(max_iter):
  #Pick a random neighbor state, snew ← neighbour(s)  
  d_coord_new = neighbor_state(d_coord)

  # Compute energy
  T = temperature( 1.0*iter / max_iter )  
  E1 = energy(d_coord)
  E2 = energy(d_coord_new)
  #print iter,E1,E2 
  
  #If P(E(s), E(snew), T) ≥ random(0, 1), move to the new state:
  #s ← snew
  p = np.random.uniform()
  if acceptance_prob(E1, E2, T) >= p:
    d_coord = d_coord_new
    #print 'Updated'
  
print d_coord

inter_player_dist = np.zeros([5,5])
epv_by_o = np.zeros(5)
basket_dist = np.zeros(5)
for i in range(5):
  for j in range(5):
    inter_player_dist[i,j] = player_dist(o_coord[i], d_coord[j])


