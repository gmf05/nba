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
vars = c("win", "line", "ishome")
#lagvars = c("fgpct")
#lagvars = c("fgpct", "ofgpct")
lagvars = c("fgpct", "ofgpct", "tot", "otot")

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
#split = sample.split(nbaSub$win, SplitRatio=0.7)
#nbaTrain = subset(nbaSub, split==TRUE)
#nbaTest = subset(nbaSub, split==FALSE)
nbaTrain = subset(nba0, nba0$season==2013)
nbaTest = subset(nba0, nba0$season==2014)

### estimate model & predict test game outcomes
# logistic regression
nbaMod = glm(win ~ ., data=nbaTrain[,vars], family="binomial")
nbaPredict = predict(nbaMod, newdata=nbaTest[,vars], type="response")

### assess accuracy (test set)
thresh = 0.5
cm = table(nbaTest$win, nbaPredict > thresh) # if thresholding needed to classify, e.g. log regression
#cm = table(nbaTest$win, nbaPredict) # if classifications are given, e.g. decision tree
print(cm) # confusion matrix
#cm # confusion matrix
cm[2,2] / (cm[1,2]+cm[2,2]) # % of predicted wins that are correct
#matrix.trace(cm) / sum(cm) # accuracy
summary(nbaMod)

### compute expected return if we had bet on test games
# which games to bet on?
# plus accuracy & expected return
bets = which(nbaPredict>thresh) # if threshold needed
#bets = which(nbaPredict==TRUE) # for classification
sum(nbaTest$win[bets])/length(bets) # accuracy on subset of games
length(bets)
sum(nbaTest$profit[bets],na.rm=TRUE)
#summary(nbaMod)
nbaTest[bets,c("gameid", "tm", "win", "pts", "opts","profit")]

length(nbaPredict)
# assess accuracy (training set)
# thresh = 0.65
# cm = table(nbaTrain$win, nbaPredict > thresh) # if thresholding needed to classify, e.g. log regression
# print(cm) # confusion matrix
# cm[2,2] / (cm[1,2]+cm[2,2]) # % of predicted wins that are correct
#matrix.trace(cm) / sum(cm) # accuracy
#summary(nbaMod)
# bets = which(nbaPredict>thresh) # if threshold needed
# #bets = which(nbaPredict==TRUE) # for classification
# sum(nbaTrain$win[bets])/length(bets) # accuracy on subset of games
# length(bets)
# sum(nbaTrain$profit[bets],na.rm=TRUE)
# nbaTrain[bets,c("gameid", "tm", "win", "pts", "opts","payout")]
# summary(nbaMod)

# # predict wins based on the line
# nbaMod2 = glm(win ~ line, data=nbaTrain, family="binomial")
# summary(nbaMod2)
# nbaPredict = predict(nbaMod2, newdata=nbaTest, type="response")
# sum(nbaTest$profit[bets]*nbaPredict[bets],na.rm=TRUE)


## try to predict what factors influence a big payout
nba$bigpay = (nba$profit>=1.5)
table(nba$bigpay,nba$ishome)
sum(nba$profit[nba$bigpay])
sum(nba$bigpay)
length(nba$win)

# how much are big payouts from "good" teams
# vs. "bad" teams?
# plot
plot(nba$profit)
par(las=2) # make y-label text perpundicular to y-axis
par(mar=c(5,8,4,2))
# reverse y range?
barplot(rev(tmpay), horiz=TRUE, names.arg=rev(teams))
summary(tmpay)
# how much is each team involved in a big pay?
C<-table(nba$tm,nba$bigpay)[,2]
C
barplot(rev(C), horiz=TRUE, names.arg=rev(teams))
mytms = teams[C>5] # teams that have paid out a lot
mytms = teams[C>8] # teams that have paid out a lot
mytms
length(mytms)
ind0 = which((nba$tm %in% mytms) & nba$bigpay)
sum(nba$profit[nba$win]) # total money available thus far for all games
sum(nba$profit[nba$bigpay]) # total money available in bigpay games
sum(C[which(teams %in% mytms)]) # how many big pay games total among mytms?
sum(nba$profit[ind0]) # money taken by "bad" teams in bigpay games
# this leads us to try, e.g....
# BKN BOS DET MIN NOP ORL PHI SAC UTA
mytms = c("BKN","BOS","DET","MIN","NOP","ORL","PHI","SAC","UTA")
#sum(tmpay[which(teams %in% mytms)]) # betting indiscriminately on mytms
# how much bigpay was available from them?
ind0 = which((nba$tm %in% mytms) & nba$bigpay)
length(ind0) # total number of bigpay wins for "mytms"
sum(nba$profit[ind0]) # money taken by "mytms" in bigpay games
# total number of games for "mytms"
mytmgms = which((nba$tm %in% mytms))
ngms = length(mytmgms)

sum(nba$profit[mytmgms]) # if we bet indiscriminately on mytms
86/1058

# for each team in mytms, estimate logistic regression model on wins
profits = rbind()
for (tm in mytms) {    
  tmData = nba0[which(nba0$tm==tm),]
  spl = sample.split(tmData$win, SplitRatio=0.7)
  tmTrain = subset(tmData, spl==TRUE)
  tmTest = subset(tmData, spl==FALSE)
  tmMod = glm(win ~ ., data=tmTrain[,vars], family="binomial")
  tmPredict = predict(tmMod, newdata=tmTest[,vars], type="response")
  tmTest$pred = tmPredict
  length(tmPredict)
  
  #plot(tmPredict)
  #thresh = 0.65
  #th = 0.65
  th = 1/(1+tmTest$lineodds)
  bets = which(tmPredict>th) # if threshold needed
  #bets = which(tmPredict>th) # if threshold needed
  nw = sum(tmTest$win[bets])
  nbets = length(bets) # number of bets
  prf = sum(tmTest$profit[bets]) # total profit on bets
  acc = nw/nbets # accuracy on bet games
  
  tmTest[bets,c("gameid","away","home","tm","win","line","pred", "profit")]
  #allprofit = allprofit + sum(tmTest$profit[bets]) # total profit on bets
  profits = rbind(profits, c(tm, nw, nbets, acc, prf))
}
print(profits)
sum(as.numeric(profits[,2]))
sum(as.numeric(profits[,3]))
sum(as.numeric(profits[,5]))
