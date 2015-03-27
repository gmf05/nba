library(shiny)

# player data
nba = read.csv("scores_00213.csv")
# drop team totals
nba = subset(nba, !(player_code=="total"))
# for now, ommitting min & +/- ("X...") since not int format
#vars = c("min", "fgm", "fga", "X3pm", "X3pa", "ftm", "fta", "X...", "off", "def", "ast", "pf", "st", "to", "bs", "ba", "pts")
vars = c("fgm", "fga", "X3pm", "X3pa", "ftm", "fta", "off", "def", "ast", "pf", "st", "to", "bs", "ba", "pts")
str(nba)

# get average stat line for each player code...
#stats = data.frame()
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
nbaClust = kmeans(stats[,vars], 5, iter.max=10, nstart=1)
stats$cluster = nbaClust$cluster

runApp(list(
  ui = basicPage(
    h2('NBA play-by-play data'),
    dataTableOutput('mytable')
  ),
  server = function(input, output) {
    output$mytable = renderDataTable({
      stats #nba
    })
  }
))