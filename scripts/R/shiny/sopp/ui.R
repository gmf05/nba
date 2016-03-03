library(shiny)
library(ggplot2) 

shinyUI(fluidPage(
  titlePanel('NBA Scoring Opportunities'),
  mainPanel(dataTableOutput("mytable"))
)
)
