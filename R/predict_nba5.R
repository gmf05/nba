## libraries
# none so far

## preprocessing functions
# set parameters
nlags = 2
lagvars = c("fgpct", "to", "tot")
#lagvars = c("fgpct", "ofgpct", "tot", "otot")

## add some data fields
addNBAData <- function(nba) {
  
  # set opponent stats in each game:
  ind0 = which(nba$tm==nba$home)
  ind1 = which(nba$tm==nba$away)
  vars = c("pts", "fgm", "fga", "ftm", "fta", "X3pm", "X3pa", "to", "tot")
  for (v in vars) {
    ov = paste("o",v,sep="")
    nba[ind0,ov] = nba[ind1,v]
    nba[ind1,ov] = nba[ind0,v]
  }
  
  # add shooting percentages
  nba$fgpct=nba$fgm/nba$fga * 100
  nba$X3ppct=nba$X3pm/nba$X3pa * 100
  nba$ftpct=nba$ftm/nba$fta * 100
  nba$ofgpct=nba$ofgm/nba$ofga * 100
  nba$oX3ppct=nba$oX3pm/nba$oX3pa * 100 
  nba$oftpct=nba$oftm/nba$ofta * 100
  
  # add number of games into season
  nba$gamenum = 0
  for (n in levels(nba$tm)) {
    ind = which(nba$tm==n)
    nba$gamenum[ind] = 1:length(ind)
   }
  
  # add wins & home/away status
  nba$ishome = (nba$tm == nba$home)
  nba$win = nba$pts > nba$opts
  
  # add profit based on moneyline bets
  nba$profit = exp(sign(nba$line)*(log(abs(nba$line)) - log(100))) - as.numeric((nba$line>0))
  nba$profit[which(nba$win==FALSE)] = -1
  nba$lineodds = exp(sign(nba$line)*(log(abs(nba$line)) - log(100))) - as.numeric((nba$line>0))
  
  return(nba)  
}

### make lagged variables
makeLagData <- function(dat, nlags, lagvars) {
  teams = levels(dat$tm)  
  # for each lagged covariate, loop over lags
  # and initialize empty columns
  dat2 = subset(dat, dat$gamenum>nlags)
  for (v in lagvars){
    for (n in 1:nlags){
      vr = paste(v, as.character(n), sep="")
      dat2[,vr] = 0
    }
  }
  # for each team, get indices of games, 
  # loop over lags/lagged covars & fill empty columns
  for (t in teams) {
    ind0 = which(dat2$tm==t)
    ngames = length(which(dat$tm==t))
    for (n in 1:nlags) {
      ind1 = which(dat$tm==t & dat$gamenum>=(nlags+1-n) & dat$gamenum<=(ngames-n))
      for (v in lagvars) {
        vr = paste(v, as.character(n), sep="")
        dat2[ind0,vr] = dat[ind1,v]
      }
    }
  }
  return(dat2)
}

## load data
nba2013 = read.csv("scorelines_00213.csv") # team box scores 2013-14 + betting lines
nba2013$season = 2013
nba2013 = addNBAData(nba2013)
nba2013 = makeLagData(nba2013, nlags, lagvars)

nba2014 = read.csv("scorelines_00214.csv") # team box scores 2013-14 + betting lines
nba2014b = read.csv("scorelines_latest_00214.csv") # team box scores 2013-14 + betting lines
nba2014 = rbind(nba2014, nba2014b)
nba2014$season = 2014
nba2014 = addNBAData(nba2014)
nba2014 = makeLagData(nba2014, nlags, lagvars)

# combine 2013-2014 seasons
nba = rbind(nba2013, nba2014)

# ## now reshape into new data set where each game
# ## is only represented once
nbaH = subset(nba,nba$tm==nba$home)
nbaA = subset(nba,nba$tm==nba$away)
games = which(nbaH$gameid %in% nbaA$gameid)
lagvars = c("fgpct", "tot")
# for each gameid
# set opponent lagged stats as away team lagged stats
for (g in games){
#   print(g) # debug
  for (v in lagvars){
    for (n in 1:nlags){
      vr = paste(v, as.character(n), sep="")
      ovr = paste("o", vr, sep="")
      nbaH[g,ovr] = nbaA[nbaA$gameid==nbaH$gameid[g],vr] 
    }  
  }
}
nba = nbaH[games,]

### estimate logistic regression model 
nbaTrain = nba
vars = c("win", "line")
for (v in lagvars){
  for (n in 1:nlags){
    vr = paste(v, as.character(n), sep="")
    vars = c(vars, vr)
    vars = c(vars, paste("o", vr, sep=""))
  }
}
nbaMod = glm(win ~ ., data=nbaTrain[,vars], family="binomial")
# summary(nbaMod)

# # how do we do on training games?
# nbaTrain$prob = predict(nbaMod, newdata=nbaTrain[,vars], type="response")
# nbaTrain$thresh = 0.7
# bets = which(nbaTrain$prob>nbaTrain$thresh | nbaTrain$prob<1-nbaTrain$thresh)
# # cm1 = table(nbaTrain$win, nbaTrain$prob > nbaTrain$thresh) # home wins
# # print(cm1) # confusion matrix for home wins
# # cm1[2,2] / (cm1[1,2]+cm1[2,2]) # accuracy for home wins
# # cm2 = table(!nbaTrain$win, nbaTrain$prob < 1-nbaTrain$thresh) # away wins
# # print(cm2) # confusion matrix for away wins
# #cm2[2,2] / (cm2[1,2]+cm2[2,2]) # accuracy for away wins
# 
# # what are predictions? 1 = home win, -1 = away win
# nbaTrain$pred = 0
# nbaTrain$pred[nbaTrain$prob>nbaTrain$thresh] = 1
# nbaTrain$pred[nbaTrain$prob<1-nbaTrain$thresh] = -1
# ncorrect = sum(nba$win[nbaTrain$pred==1]) + sum(!(nbaTrain$win[nbaTrain$pred==-1]))
# nbets = length(bets)
# ncorrect / nbets
# # nbaTrain[bets,c("gameid", "away", "home", "prob", "pred", "win")]
# tail(nbaTrain[bets,c("gameid", "away", "home", "prob", "pred", "win")])

## make new data frame for tonight's games
teams = levels(nbaTrain$tm)
nbaTest = read.csv("linestoday.csv")
# for each game in nbaTest
# initalize empty data
for (v in vars){nbaTest[,v] = 0}
nbaTest$line = nbaTest$homeline
# make sure teams are factors of 30 levels
nbaTest$away = factor(match(nbaTest$away,teams), levels=1:30, labels=teams)
nbaTest$home = factor(match(nbaTest$home,teams), levels=1:30, labels=teams)
str(nbaTest)

# get lagged stats from nbaTrain...
for (g in 1:nrow(nbaTest)){
  for (v in lagvars){
    vr = paste(v, "1", sep="")
    ovr = paste(v, "1", sep="")
    g1 = tail(which(nbaTrain$tm==nbaTest$home[g]),n=1)
    g2 = tail(which(nbaTrain$tm==nbaTest$away[g]),n=1)
    nbaTest[g,vr] = nbaTrain[g1,v]
    nbaTest[g,ovr] = nbaTrain[g2,v]
    for (n in 1:nlags-1){
      vrlag = paste(v, as.character(n), sep="")
      ovrlag = paste("o", vr, sep="")
      vr = gsub(as.character(n), as.character(n+1), vrlag)
      ovr = paste("o", vr, sep="")
      # get lagged n+1 game for home & away
      g1 = tail(which(nbaTrain$tm==nbaTest$home[g]),n=n+1)[1]
      g2 = tail(which(nbaTrain$tm==nbaTest$away[g]),n=n+1)[1]
      nbaTest[g,vr] = nbaTrain[g1,v]
      nbaTest[g,ovr] = nbaTrain[g2,v]
    }
  }
}

### predict test game outcomes
nbaTest$prob = predict(nbaMod, newdata=nbaTest[,vars], type="response")
nbaTest$lineodds = exp(sign(nbaTest$line)*(log(abs(nbaTest$line)) - log(100))) - as.numeric((nbaTest$line>0))
nbaTest$thresh = 1/(1+nbaTest$lineodds)
# print expected winners
#thresh = 0.5
nbaOut = nbaTest[,c("gameid", "away", "home", "prob", "thresh")]
nbaOut$pred = factor(1, levels=1:30, labels=teams)
for (g in 1:nrow(nbaOut)){
  if(nbaOut$prob[g] >= 0.5) nbaOut$pred[g] = nbaOut$home[g]
  else {
    nbaOut$pred[g] = nbaOut$away[g]
    nbaOut$prob[g] = 1 - nbaOut$prob[g]
  }
}

# summary(nbaMod)
print(nbaOut[,c("gameid", "pred", "prob", "thresh")])

