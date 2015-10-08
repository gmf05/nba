## load data
nba = read.csv("scores_team_00213.csv") # team box scores 2013-14
# concatenate with box scores from 2014-15
#nba2 = read.csv("scores_team_00214.csv") # team box scores 2014-15

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

#summary(nba) 
#str(nba)

# keep covariates of interest
vars = c("ishome", "fgpct", "ofgpct", "to", "oto", "tot", "otot", "win")
nbaSub = nba[,vars]

## break into train/test data
#library("caTools")
#split = sample.split(nbaSub$win, SplitRatio=0.7)
#nbaTrain = subset(nbaSub, split==TRUE)
#nbaTest = subset(nbaSub, split==FALSE)

###
# fit multivariate model for whole league
nbaLog = glm(win ~ ., data=nbaSub, family="binomial")

##fit multivariate models for each team
teams = levels(nba$tm)
#teams = c("ATL")

models = rbind(c("NBA", nbaLog$coefficients))
for (t in teams) {
  teamdata = subset(nbaSub, nba$tm==t)
  modelOK = TRUE
  tryCatch(teamLog <- glm(win ~ ., data=teamdata, family="binomial"), warning=function(w){modelOK <<- FALSE})
  #teamLog$coefficients = teamLog$coefficients - nbaLog$coefficients # subtract "average" nba team
  #print(summary(teamLog))
  if (modelOK) {
    print(t)    
    models = rbind(models, c(t, teamLog$coefficients))
  }
}

#summary(teamLog)
#tms = seq(1,6)
#coeff = 5
#plot(models[tms,coeff], xaxt="n", xlab="Team")
#axis(1, at=seq(1,length(tms)), labels=models[tms,1])

# export to matlab
library(R.matlab)
R.matlab::writeMat(con="asdf.mat", x=models)
summary(nbaLog)

