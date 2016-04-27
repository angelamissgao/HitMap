library(ggplot2)
library(rgdal)
library(scales)
library(dplyr)
library(maptools)
library(sp)
library(maps)
library(raster)
library(leaflet)
library(shiny)


#Load San Francisco Census Blocks data
df.blocks <- shapefile("data/df.blocks/df.blocks.shp")

#Load SF attractions data
attractions <- read.csv("data/sf-attractions.csv", stringsAsFactors = FALSE, header = TRUE)


###########################################################################

maxScore <- max(df.blocks@data$score)

###########################################################################

## Plotting an interactive map with leaflet ##

# Cleaning blocks data: replacing NA (crime rate) with 0 
df.blocks@data$score[is.na(df.blocks@data$score)] <- 0

# Legend
ATgreen <- rgb(46/255, 204/255, 113/255, 1)
ATyellow <- rgb(241/255, 196/255, 14/255, 1)
ATred <- rgb(231/255, 76/255, 60/255, 1)

polpopup <- paste0("GEOID: ", df.blocks$geoid10, "<br>", "Hitmap score: ", paste(round(100-(df.blocks$score/maxScore)*100,digits=2),"%",sep=""))
attractionspopup <- paste0("Attraction: ", attractions$name, "<br>", "Address: ", attractions$address.street, "<br>", "<a href=", attractions$profile, ">", "Link", "</a>" )
pal <- colorNumeric(
  palette = c(ATgreen, ATyellow, ATred),
  domain = df.blocks$score)


shinyServer(function(input, output, session) {

  output$map <- renderLeaflet({
    leaflet(data = c(attractions)) %>% setView(lng = -122.447902, lat = 37.761886, zoom = 12) %>%
      addTiles() %>%
      addPolygons(data = df.blocks, 
                  fillColor = ~pal(score), 
                  color = NA,
                  fillOpacity = 0.7, 
                  weight = 1, 
                  smoothFactor = 0.5,
                  popup = polpopup) %>%
      addLegend(
        colors = c('#e74c3c', '#fdae61', '#fee08b', '#ffffbf', '#d9ef8b', '#59d285'), 
        labels = c("<span style='font-size:11px'>Less safe</span>","","","","","<span style='font-size:11px'>Safer</span>"),
        values = df.blocks$score, 
        position = "bottomright", 
        title = "Crime Risk",
        opacity = 0.6) %>%
#      addMarkers(hotels_sample$lon, hotels_sample$lat, popup = markerpopup) %>%
      addCircleMarkers(attractions$longitude, attractions$latitude, 
                       popup = attractionspopup,
                       radius = 5,
                       color = "#9b59b6",
                       stroke = FALSE, fillOpacity = 0.5,
                       group = "Attractions") %>%
      addLayersControl(
        overlayGroups = c("Attractions"),
        options = layersControlOptions(collapsed = FALSE)
      )
  })

  
})