library(shiny)
library(leaflet)

shinyUI(navbarPage(windowTitle="Hitmap" ,tags$img(src="img/logo.png", class=""),
  theme = "css/full.css",
#  div(class = "busy",  
#      img(src="img/busy.gif")),
  
  mainPanel(
    leafletOutput("map", height = "620px"),
    tags$head(tags$script(src="js/busy.js")),
    tags$head(tags$script(src="js/nlform.js")),
    HTML("<script>var nlform = new NLForm( document.getElementById( 'nl-form' ) );</script>")
    
)))