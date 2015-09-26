## libraries
library("matrixcalc")
library("caTools")
library("randomForest")

## load data
nba = read.csv("scorelines_00213.csv") # team box scores 2013-14 + betting lines
nba$season = 2013
nba2 = read.csv("scorelines_00214.csv") # team box scores 2013-14 + betting lines
nba2$season = 2014
nba = rbind(nba, nba2)

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

# add home status
nba$ishome = (nba$tm == nba$home)

# add profit from a $1 moneyline bet
# profit in positive spread = spread/100 - 1
# for negative spread = -100/spread- 1
nba$profit = exp(sign(nba$line)*(log(abs(nba$line)) - log(100))) - as.numeric((nba$line>0))
nba$profit[which(nba$win==FALSE)] = -1
nba$lineodds = exp(sign(nba$line)*(log(abs(nba$line)) - log(100))) - as.numeric((nba$line>0))

### make lagged variables
nlags = 2
nba0 = subset(nba, nba$gamenum>nlags)
teams = levels(nba$tm)

# NOTE: There are multiple ways to get lagged "opponent FG%"
# e.g. we could take the prev opponents of the team of interest
# or the upcoming opponent's past three game's...
# Right now the former is impelemented. Can we switch to the latter?
# 
vars = c("win", "line")
#lagvars = c("fgpct")
lagvars = c("fgpct", "to", "tot")

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

## now reshape into new data set where each game is only represented once
# and has home fg%, away fg%, homewins, etc as covariates
nba1 = nba0[nba0$home==nba0$tm,] # cut # games in half
nba1a = nba0[nba0$away==nba0$tm,] # cut # games in half
ind = which(nba1$gameid==nba1a$gameid)
nba1 = nba1[ind,]
nba1a = nba1a[ind,]
# now switch opponent stats in nba1 to reg stats from nba1a
for (v in lagvars){
  for (n in 1:nlags){
    vr = paste(v, as.character(n), sep="")
    ovr = paste("o", vr, sep="")
    nba1[,ovr] = nba1a[,vr]
    vars = c(vars, ovr)
  }
}

### break into train/test data
# plus classify expected win/loss
nbaTrain = subset(nba1, nba1$season==2013)
nbaTest = subset(nba1, nba1$season==2014)
### estimate model & predict test game outcomes
nbaMod = glm(win ~ ., data=nbaTrain[,vars], family="binomial")
summary(nbaMod)
nbaPredict = predict(nbaMod, newdata=nbaTest[,vars], type="response")
nbaTest$pred = nbaPredict

### compute expected return if we had bet on test games
# which games to bet on?
# plus accuracy & expected return
#thresh = 0.5
thresh = 1 / (1+nbaTest$lineodds)
bets = which(nbaPredict>thresh) # if threshold needed
#bets = which(nbaPredict==TRUE) # for classification
sum(nbaTest$win[bets])/length(bets) # accuracy on subset of games
cm = table(nbaTest$win, nbaPredict > thresh) # if thresholding needed to classify, e.g. log regression
#cm = table(nbaTest$win, nbaPredict) # if classifications are given, e.g. decision tree
print(cm) # confusion matrix
cm[2,2] / (cm[1,2]+cm[2,2]) # % of predicted wins that are correct
#matrix.trace(cm) / sum(cm) # accuracy
length(bets)
sum(nbaTest$profit[bets],na.rm=TRUE)
nbaTest[bets,c("gameid", "tm", "win", "pred", "lineodds", "profit")]


