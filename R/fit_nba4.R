## libraries
library("matrixcalc")
library("caTools")
library("randomForest")

## load data
nba = read.csv("scores_team_00213.csv") # team box scores 2013-14
# concatenate with box scores from 2014-15
nba = read.csv("scores_team_00214.csv") # team box scores 2014-15

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
# keep only covariates of interest
#vars = c("fgpct", "ofgpct", "win") # 83% accuracy
vars = c("ishome", "fgpct", "ofgpct", "to", "oto", "tot", "otot", "win") # 88% accuracy
nbaSub = nba[,vars]

# break into train/test data
split = sample.split(nbaSub$win, SplitRatio=0.7)
nbaTrain = subset(nbaSub, split==TRUE)
nbaTest = subset(nbaSub, split==FALSE)
nbaTest = nba # if loaded new data

## now predict wins for test data using diff methods
# logistic regression
nbaMod = glm(win ~ ., data=nbaTrain, family="binomial")
nbaPredict = predict(nbaMod, newdata=nbaTest, type="response")

# k-nearest neighbors
nbaPredict = knn3Train(nbaTrain[,vars], nbaTest[,vars], cl=nbaTrain$win, k=10)

# decision tree
nbaMod = rpart(win ~ ., data=nbaTrain, method="class", minbucket=30)
prp(nbaMod) # plot tree
nbaPredict = predict(nbaMod, newdata=nbaTest, type="class")

# random forest
nbaMod <- randomForest(win ~ ., data=nbaTrain, nodesize=25, ntree=200)
nbaPredict = predict(nbaMod, newdata=nbaTest)

cm = table(nbaTest$win, nbaPredict > 0.5) # if thresholding needed to classify, e.g. log regression
cm = table(nbaTest$win, nbaPredict) # if classifications are given, e.g. decision tree
print(cm) # confusion matrix
cm # confusion matrix
cm[2,2] / (cm[1,2]+cm[2,2]) # % of predicted wins that are correct
#summary(nbaMod)
