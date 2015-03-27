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

# keep only covariates of interest
vars = c("pts", "fgpct", "ofgpct", "X3ppct", "o3ppct", "to", "oto", "win") # 87% accuracy (no FT or reb)
vars = c("pts", "fgpct", "ofgpct", "X3ppct", "o3ppct", "to", "oto", "otot", "win") # 92% accuracy (no FT, just opp reb)
vars = c("pts", "fgpct", "ofgpct", "ftpct", "oftpct", "X3ppct", "o3ppct", "to", "oto", "win") # 91% accuracy
vars = c("pts", "fgpct", "X3ppct", "to", "tot", "win") # ~80% accuracy
nbaSub = nba[,vars]

# break into train/test data
library("caTools")
split = sample.split(nbaSub$win, SplitRatio=0.7)
nbaTrain = subset(nbaSub, split==TRUE)
nbaTest = subset(nbaSub, split==FALSE)

#nbaLog = glm(win ~ fgpct + ofgpct, data=nba0, family="binomial")
nbaLog = glm(win ~ ., data=nbaTrain, family="binomial")
summary(nbaLog)

# now predict wins for test data
# nbaLog = glm(win ~ ., data=nbaTrain, family="binomial")
nbaPredict = predict(nbaLog, newdata=nbaTest, type="response")
cm = table(nbaTest$win, nbaPredict>0.5)
cm
library("matrixcalc")
matrix.trace(cm) / sum(cm)

