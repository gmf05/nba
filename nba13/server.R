library(shiny)


### function to add some data fields
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
  
  return(nba)  
}

### box score data ###
## load data
nba = read.csv("scorelines_00213.csv") # team box scores 2013-14
nba = addNBAData(nba)

shinyServer(function(input, output) {
 output$mytable = renderDataTable({nba })
})
