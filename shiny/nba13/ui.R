library(shiny)
library(ggplot2) 

shinyUI(fluidPage(
  titlePanel('NBA team box scores 2013-14'),
  mainPanel(dataTableOutput("mytable"))
  )
)
