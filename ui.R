library(shiny)
library(leaflet)

shinyUI(
  navbarPage(
    windowTitle="Hitmap" ,tags$img(src="img/logo.png", class=""),
    theme = "css/full.css",
#  div(class = "busy",  
#      img(src="img/busy.gif")),
    sidebarLayout(
      mainPanel(
        leafletOutput("map", height = "620px"),
        tags$head(tags$script(src="js/busy.js")),
        tags$head(tags$script(src="js/nlform.js")),
        HTML("<script>var nlform = new NLForm( document.getElementById( 'nl-form' ) );</script>")
      ),
      sidebarPanel(
        selectizeInput(
          'position', 'I am travalling to', choices = "San francisco",
          options = list(create = TRUE)
        ),
        selectizeInput(
          'people', 'with', choices = list("Family"=1, "friend(s)" = 2, "sweetheart" = 3,"colleague" = 4),
          options = list(create = TRUE)
        ),
        selectizeInput(
          'goal', 'for', choices = list("sightseeing"=1, "shopping" = 2, "have fun" = 3,"romantic trip" = 4, "business" = 5),
          options = list(create = TRUE)
        )
      )
    )
    
  )
)