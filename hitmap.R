library(ggplot2)
library(rgdal)
library(scales)
library(dplyr)
library(maptools)
library(sp)
library(maps)
library(raster)
library(leaflet)

#Load San Francisco Census Blocks data
blocks <- shapefile("data/tl_2010_06075_tabblock10edited/tl_2010_06075_tabblock10.shp")
# blocks <- shapefile("data/cb_2014_06_tract_500k/cb_2014_06_tract_500k.shp")
blocks <- spTransform(x=blocks, CRSobj=CRS("+proj=longlat +datum=WGS84"))
names(blocks@data) <- tolower(names(blocks@data))


#Load San Francisco 2015 crime data
crime_data <- read.csv("data/SFPD_Incidents_-_Previous_Year__2015_.csv", stringsAsFactors = FALSE, header = TRUE)
crime_data$Category <- tolower(crime_data$Category)

#Load Categroy Scoring data
category_score <- read.csv("data/category_score.csv", stringsAsFactors = FALSE, header = TRUE)
category_score$Category <- tolower(category_score$Category)

#Load SF attractions data
attractions <- read.csv("data/sf-attractions.csv", stringsAsFactors = FALSE, header = TRUE)


###########################################################################


# Cleaning and Keeping only complete cases
# Loading SF 2015 and 2016 crime data -> remove unnecessary columns -> merge -> load category table -> assign (match) weights to each crime based on category
crime_data <- crime_data[complete.cases(crime_data), ]

# Assign category score to each crime
cat <- match(x=crime_data$Category, table=category_score$Category)
crime_data$Score <- category_score$Score[cat]

#Remove unncessary columns and turn crime_data in to data frame
df.crime_data <- data.frame(category=crime_data$Category, pdid=crime_data$PdId, score=crime_data$Score, latitude=crime_data$Y, longitude=crime_data$X)


###########################################################################


#Convert crime data to a spatial points object
df.crime_data <- SpatialPointsDataFrame(coords=df.crime_data[, c("longitude", "latitude")], data=df.crime_data[, c("category", "pdid", "score")], proj4string=CRS("+proj=longlat +datum=WGS84"))

#Spatial overlay to identify census polygon in which each crime point falls
#The Result `crime_blocks` is a dataframe with the block data for each point
crime_blocks <- over(x=df.crime_data, y=blocks)

#Add block data to each crime 
df.crime_data@data <- data.frame(df.crime_data@data, crime_blocks)

#Aggregate crimes by block 
agg_crimeblocks <- aggregate(cbind(df.crime_data@data$score)~geoid10, data = df.crime_data, FUN = sum)

#Format score into ranking
agg_crimeblocks$V1 <- dense_rank(agg_crimeblocks$V1)

#Add number of crimes to blocks object
m <- match(x=blocks@data$geoid10, table=agg_crimeblocks$geoid10)
blocks@data$score <- agg_crimeblocks$V1[m]

maxScore <- max(agg_crimeblocks$V1)


###########################################################################


# Hotels #
hotels_sample <- data.frame(id=1:2, 
                            name=c("Omni San Francisco Hotel", 
                                   "Holiday Inn San Francisco Golden Gateway"), 
                            lat=c(37.793344, 37.790309), 
                            lon=c(-122.403101, -122.421986), 
                            price=c(152, 105))

#Convert hotels to a spatial points object
df.hotels_sample <- SpatialPointsDataFrame(coords=hotels_sample[, c("lon", "lat")], data=hotels_sample[, c("name", "price")], proj4string=CRS("+proj=longlat +datum=WGS84"))

#Spatial overlay to identify census polygon in which each hotel falls
#The Result `crime_blocks` is a dataframe with the block data for each point
hotel_blocks <- over(x=df.hotels_sample, y=blocks)

#Add block data to each hotel
df.hotels_sample@data <- data.frame(df.hotels_sample@data, score=round(100-(hotel_blocks$score/maxScore)*100,digits=2))

###########################################################################

## Plotting an interactive map with leaflet ##

# Copying blocks df
df.blocks <- blocks

# Cleaning blocks data: replacing NA (crime rate) with 0 
df.blocks@data$score[is.na(df.blocks@data$score)] <- 0

# Legend
ATgreen <- rgb(46/255, 204/255, 113/255, 1)
ATyellow <- rgb(241/255, 196/255, 14/255, 1)
ATred <- rgb(231/255, 76/255, 60/255, 1)

polpopup <- paste0("GEOID: ", df.blocks$geoid10, "<br>", "Crime rate: ", paste(round(100-(df.blocks$score/maxScore)*100,digits=2),"%",sep=""))
markerpopup <- paste0("Hotel: ", df.hotels_sample@data$name, "<br>", "Price: $", df.hotels_sample@data$price, "<br>", "Hitmap Score: ", df.hotels_sample@data$score, "%")
attractionspopup <- paste0("Attraction: ", attractions$name, "<br>", "Address: ", attractions$address.street, "<br>", "<a href=", attractions$profile, ">", "Link", "</a>" )
pal <- colorNumeric(
  palette = c(ATgreen, ATyellow, ATred),
  domain = df.blocks$score)

map <- leaflet(data = c(hotels_sample, attractions)) %>% setView(lng = -122.401558, lat = 37.784172, zoom = 13) %>%
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
  addMarkers(hotels_sample$lon, hotels_sample$lat, popup = markerpopup) %>%
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

# Draw the map
map

