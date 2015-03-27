library(shiny)

# load data in csv format
#nba = read.csv("playbyplay_example.csv") # one game
#nba = read.csv("playbyplay_R.csv") # whole season
#nba = read.csv("shots_example.csv") # whole season

### box score data ###
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
nba$fgpct=nba$fgm/nba$fga
nba$X3ppct=nba$X3pm/nba$X3pa
nba$ftpct=nba$ftm/nba$fta
nba$ofgpct=nba$ofgm/nba$ofga
nba$o3ppct=nba$o3pm/nba$o3pa
nba$oftpct=nba$oftm/nba$ofta

# add wins
nba$win = nba$pts > nba$opts

# add home status
nba$ishome = (nba$tm == nba$home)
### end box score data###

runApp(list(
  ui = basicPage(
    h2('NBA play-by-play data'),
    dataTableOutput('mytable')
  ),
  server = function(input, output) {
    output$mytable = renderDataTable({
      nba
    })
  }
))