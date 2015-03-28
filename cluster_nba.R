## libraries
library("matrixcalc")
library("caTools")
library("randomForest")

## load data

# player data
nba = read.csv("scores_00213.csv")
# drop team totals
nba = subset(nba, !(player_code=="total"))
# for now, ommitting min & +/- ("X...") since not int format
#vars = c("min", "fgm", "fga", "X3pm", "X3pa", "ftm", "fta", "X...", "off", "def", "ast", "pf", "st", "to", "bs", "ba", "pts")
vars = c("fgm", "fga", "X3pm", "X3pa", "ftm", "fta", "off", "def", "ast", "pf", "st", "to", "bs", "ba", "pts")
str(nba)

# get average stat line for each player code...
players = levels(nba$player_code)
players = subset(players, !(players=="total"))
stats = data.frame()
for (p in players) {
  plstats = colMeans(subset(nba, player_code==p)[,vars])
  c(p, plstats)
  stats = rbind(stats,plstats)
}
stats = cbind(stats, players)
names(stats) <- c(vars, "player_code")

# cluster
nbaClust = kmeans(stats[,vars], 10, iter.max=20, nstart=1)

## how many clusters is good?
# bw = c()
# for (k in seq(2,50)) {
#   cl = kmeans(stats[,vars], k, iter.max=10, nstart=1)
#   bw = c(bw, cl$tot.withinss)
# }
# cl$betweenss
# plot(seq(2,50), bw, xlab="Number of clusters", ylab="Total within cluster distance")

