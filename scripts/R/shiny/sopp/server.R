library(shiny)

## load data
nba = read.csv("shiny_table.csv")

shinyServer(function(input, output) {
  output$mytable = renderDataTable({nba })
})
