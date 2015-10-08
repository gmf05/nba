## libraries
library("xtable")

## load data

# player stats per 36 min
nba2 = read.csv("temp/player_stats_2014.csv")

# player shot distributions
nba = read.csv("csv/player_shot_dist.csv")
vars = c("min_gm","ast","oreb","dreb","stl","bs","tov","pts")
nba$ast = 0
nba$oreb = 0
nba$dreb = 0
nba$stl = 0
nba$tov = 0
nba$bs = 0
nba$min_gm = 0
nba$pts = 0
nba$fgpct = 0
for (p in levels(nba$player)) {
  ind1 = which(nba$player==p)
  ind2 = which(nba2$player==p)
  if (length(ind1) & length(ind2)>0) {
    nba[ind1,vars] = nba2[ind2, vars]
    nba[ind1,"fgpct"] = nba2[ind2,"fgm"]/nba2[ind2,"fga"] * 100
  }
}


# convert FGA -> % FGA by location
vars = c("fga_5ft", "fga_10ft", "fga_15ft", "fga_20ft", "fga_21ft")
for (v in vars) {
  nba[,v] = nba[,v] / nba$fga_total * 100
}


# cluster
vars = c("min_gm", "pts", "fgpct", "fga_5ft", "fga_10ft", "fga_15ft", "fga_20ft", "fga_21ft", "ast", "oreb", "dreb", "stl", "bs")
vars2 = c("player", vars, "cluster")
nbaClust = kmeans(nba[,vars], 10, iter.max=20, nstart=1)
nba$cluster = nbaClust$cluster

write.csv(nba, file="nbaclusters2.csv")

x = xtable(nba[,vars2])
print.xtable(x, type="html", file="nbaclusters2.txt")

x = xtable(nbaClust$centers)
print.xtable(x, type="html", file="nbaclusters2_centers.txt")

## how many clusters is good?
# bw = c()
# for (k in seq(2,50)) {
#   cl = kmeans(stats[,vars], k, iter.max=10, nstart=1)
#   bw = c(bw, cl$tot.withinss)
# }
# cl$betweenss
# plot(seq(2,50), bw, xlab="Number of clusters", ylab="Total within cluster distance")

