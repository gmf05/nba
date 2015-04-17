## load data
nba = read.csv("scores_team_00213.csv") # team box scores 2013-14

## add data fields
# set opponent stats in each game:
ngames = nrow(nba)
for (game in seq(1,ngames/2)){
  nba$opts[2*game-1] = nba$pts[2*game]
  nba$opts[2*game] = nba$pts[2*game-1]
  
  nba$ofgm[2*game-1] = nba$fgm[2*game]
  nba$ofgm[2*game] = nba$fgm[2*game-1]

  nba$ofga[2*game-1] = nba$fga[2*game]
  nba$ofga[2*game] = nba$fga[2*game-1]
  
  nba$o3pm[2*game-1] = nba$X3pm[2*game]
  nba$o3pm[2*game] = nba$X3pm[2*game-1]

  nba$o3pa[2*game-1] = nba$X3pa[2*game]
  nba$o3pa[2*game] = nba$X3pa[2*game-1]
  
  nba$oftm[2*game-1] = nba$ftm[2*game]
  nba$oftm[2*game] = nba$ftm[2*game-1]
  
  nba$ofta[2*game-1] = nba$fta[2*game]
  nba$ofta[2*game] = nba$fta[2*game-1]
  
  nba$oto[2*game-1] = nba$to[2*game]
  nba$oto[2*game] = nba$to[2*game-1]
  
  nba$otot[2*game-1] = nba$tot[2*game]
  nba$otot[2*game] = nba$tot[2*game-1]
}

# add shooting percentages
nba$fgpct=nba$fgm/nba$fga * 100
nba$X3ppct=nba$X3pm/nba$X3pa * 100
nba$ftpct=nba$ftm/nba$fta * 100
nba$ofgpct=nba$ofgm/nba$ofga * 100
nba$o3ppct=nba$o3pm/nba$o3pa * 100 
nba$oftpct=nba$oftm/nba$ofta * 100

# add wins
nba$win = nba$pts > nba$opts

# add home status
nba$ishome = (nba$tm == nba$home)

summary(nba) 
str(nba)

# fit models across whole nba
# which game stats sig influence odds of winning?
# from bivariate models:
#  x. being home team
#  x. pts, opts
#  x. fgm, fga, fgpct
#  x. 3pm, 3ppct
#  x. ftm, fta, ftpct
#  x. off, def, tot, otot rebounds
#  x. to, oto
#  x. st, bs, ba
#  x. 
#
#
# Also a multivariate model with
# shooting %s + turnovers (team & opponent) gives...
#
# Coefficients:
#   Estimate Std. Error z value Pr(>|z|)    
# (Intercept)  -1.383272   1.113768  -1.242    0.214    
# pts           0.085460   0.008618   9.916  < 2e-16 ***
#   fgpct        31.590181   2.185455  14.455  < 2e-16 ***
#   ofgpct      -43.356726   2.186711 -19.827  < 2e-16 ***
#   ftpct         3.709523   0.713809   5.197 2.03e-07 ***
#   oftpct       -5.291026   0.702147  -7.535 4.86e-14 ***
#   X3ppct        4.807746   0.774271   6.209 5.32e-10 ***
#   o3ppct       -6.455729   0.765346  -8.435  < 2e-16 ***
#   to           -0.248792   0.021066 -11.810  < 2e-16 ***
#   oto           0.237050   0.020934  11.324  < 2e-16 ***
#   ---
#   Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1


# keep covariates of interest
nba0 = nba[,vars]

str(nba0)

#nbaLog = glm(win ~ fgpct + ofgpct, data=nba0, family="binomial")
nbaLog = glm(win ~ ., data=nba0, family="binomial")

summary(nbaLog)

#####
# fit models for Atlanta Hawks
# which game stats sig influence odds of winning?
# according to multivariate model:
#  * pts ofgpct oto otot
#  . to
atl = subset(nba0, nba$tm=='ATL')
str(atl)
atlLog = glm(win ~ ., data=atl, family="binomial")
summary(atlLog)

###
##fit multivariate models for each team
teams = levels(nba$tm)
teams = c("ATL")
for (t in teams){
  print(t)
  teamdata = subset(nba0, nba$tm==t)
  teamLog = glm(win ~ ., data=teamdata, family="binomial")
  summary(teamLog)
}





## load team of interest
atl = subset(nba0, nba$tm=='ATL')
str(atl)

# fit models
# which game stats sig influence odds of winning?
# from bivariate models:
#  x. fgm, fgpct
#  x. 
#  x. 
#  x. 
#  x. 
atlLog = glm(win ~ ., data=atl, family="binomial")
summary(atlLog)



