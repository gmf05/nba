## libraries
library("matrixcalc")
library("caTools")
library("randomForest")

## load data
#nba = read.csv("scores_team_00213.csv") # team box scores 2013-14
# concatenate with box scores from 2014-15
#nba = read.csv("scores_team_00214.csv") # team box scores 2014-15
#nba = read.csv("scorelines_00213.csv") # team box scores 2013-14 + betting lines
#nba = read.csv("scorelines_00214.csv") # team box scores 2013-14 + betting lines

nba = read.csv("scorelines_00213.csv") # team box scores 2013-14 + betting lines
nba0 = read.csv("scorelines_00214.csv") # team box scores 2013-14 + betting lines
nba = rbind(nba, nba0)

## add data fields
# add game number into season
nba$gamenum = 0
for (n in levels(nba$tm)) {
  ind = which(nba$tm==n)
  nba$gamenum[ind] = 1:length(ind)
}

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
# compare to lines 
## assume nba$spread has the spread
#nba$winspread = (nba$pts - nba$opts) > nba$spread

# add home status
nba$ishome = (nba$tm == nba$home)

# add profit from a $1 moneyline bet
# profit in positive spread = spread/100 - 1
# for negative spread = -100/spread- 1
nba$profit = exp(sign(nba$line)*(log(abs(nba$line)) - log(100))) - as.numeric((nba$line>0))
nba$profit[which(nba$win==FALSE)] = -1
### make lagged variables
nlags = 2
nba0 = subset(nba, nba$gamenum>nlags)
teams = levels(nba$tm)
vars = c("win", "line", "ishome")
#lagvars = c("fgpct")
#lagvars = c("fgpct", "ofgpct")
lagvars = c("fgpct", "ofgpct", "tot", "otot")

# NOTE: There are multiple ways to get lagged "opponent FG%"
# e.g. we could take the prev opponents of the team of interest
# or the upcoming opponent's past three game's...
# Right now the former is impelemented. Can we switch to the latter?
# 
#lagvars = c("fgpct", "ofgpct", "to", "oto", "tot", "otot")
#lagvars = c("fgpct", "ofgpct", "ftpct", "oftpct", "X3ppct", "o3ppct", "win", "to", "oto", "tot", "otot")

# for each lagged covariate, loop over lags
# and initialize empty columns
for (v in lagvars){
  for (n in 1:nlags){
    vr = paste(v, as.character(n), sep="")
    nba0[,vr] = 0
    vars = c(vars, vr)
  }
}

# for each team, get indices of games, 
# loop over lags/lagged covars & fill empty columns
for (t in teams) {
  ind0 = which(nba0$tm==t)
  ngames = length(which(nba$tm==t))
  for (n in 1:nlags) {
    ind1 = which(nba$tm==t & nba$gamenum>=(nlags+1-n) & nba$gamenum<=(ngames-n))
    for (v in lagvars) {
      vr = paste(v, as.character(n), sep="")
      nba0[ind0,vr] = nba[ind1,v]
    }
  }
}

### break into train/test data
library("caTools")
nbaSub = nba0
split = sample.split(nbaSub$win, SplitRatio=0.7)
nbaTrain = subset(nbaSub, split==TRUE)
nbaTest = subset(nbaSub, split==FALSE)
#nbaTest = nba0


### estimate model & predict test game outcomes
# logistic regression
nbaMod = glm(win ~ ., data=nbaTrain[,vars], family="binomial")
nbaPredict = predict(nbaMod, newdata=nbaTest[,vars], type="response")
nbaTest$pred = nbaPredict
summary(nbaMod)
thresh = 0.8
cm = table(nbaTest$win, nbaPredict > thresh) # if thresholding needed to classify, e.g. log regression
#cm = table(nbaTest$win, nbaPredict) # if classifications are given, e.g. decision tree
print(cm) # confusion matrix
#cm # confusion matrix
cm[2,2] / (cm[1,2]+cm[2,2]) # % of predicted wins that are correct
matrix.trace(cm) / sum(cm) # accuracy
summary(nbaMod)

bets = which(nbaPredict>thresh) # if threshold needed
#bets = which(nbaPredict==TRUE) # for classification
nbaTest[bets,c("gameid", "tm", "win", "pred", "profit")]
