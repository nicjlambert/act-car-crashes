packages <- c("dplyr", "leaflet", "RSocrata")

# Check if packages are installed, and install them if necessary
install_missing_packages <- function(packages) {
  missing_packages <- packages[!sapply(packages, requireNamespace, quietly = TRUE)]
  
  if (length(missing_packages) > 0) {
    install.packages(missing_packages)
  }
}

# Install missing packages
install_missing_packages(packages)

# Load packages
lapply(packages, library, character.only = TRUE)

data <- RSocrata::read.socrata(
    "https://www.data.act.gov.au/resource/6jn4-m8rx.json",
    app_token = Sys.getenv("SOCRATA_TOKEN"),
    email     = Sys.getenv("SOCRATA_EMAIL"),
    password  = Sys.getenv("SOCRATA_PWD")
  )

# head(data)
#crash_id crash_date crash_time suburb_location           x            y intersection midblock   crash_direction                       crash_type       crash_severity lighting_condition   road_condition  weather_condition   location.latitude location.longitude
# 1221565 2020-01-03      10:18       SYMONSTON 149.1639071 -35.34049121          YES       NO       South bound               Rear end collision Property Damage Only           Daylight Good dry surface               Fine -35.340491212684185 149.16390712589399
# 1221566 2020-01-06      19:44           LYONS 149.0710365 -35.34796466          YES       NO East / West bound Right turn into oncoming vehicle Property Damage Only           Daylight      Wet surface Cloudy or Overcast  -35.34796465694476   149.071036508782
# 1221567 2020-01-07      14:00            CITY 149.1293898 -35.27948844          YES       NO       South bound        Same direction side swipe               Injury           Daylight Good dry surface               Fine  -35.27948844333742  149.1293898164764
# 1221568 2020-01-07      14:15     NARRABUNDAH 149.1387471 -35.34417984          YES       NO       South bound               Rear end collision Property Damage Only           Daylight Good dry surface      Smoke or dust -35.344179839851094 149.13874707018067
# 1221569 2020-01-07      17:30         PHILLIP 149.0901224 -35.34874646          YES       NO       South bound               Rear end collision Property Damage Only           Daylight Good dry surface               Fine  -35.34874646376222 149.09012244646124
# 1221570 2020-01-08      17:40          WESTON 149.0538768 -35.32874856          YES       NO       South bound               Rear end collision Property Damage Only           Daylight Good dry surface      Smoke or dust  -35.32874855786724 149.05387681883587

#str(data)
#'data.frame':   71796 obs. of  17 variables:
# $ crash_id              : chr  "1221565" "1221566" "1221567" "1221568" ...
# $ crash_date            : POSIXct, format: "2020-01-03" "2020-01-06" "2020-01-07" "2020-01-07" ...
# $ crash_time            : chr  "10:18" "19:44" "14:00" "14:15" ...
# $ suburb_location       : chr  "SYMONSTON" "LYONS" "CITY" "NARRABUNDAH" ...
# $ x                     : chr  "149.1639071" "149.0710365" "149.1293898" "149.1387471" ...
# $ y                     : chr  "-35.34049121" "-35.34796466" "-35.27948844" "-35.34417984" ...
# $ intersection          : chr  "YES" "YES" "YES" "YES" ...
# $ midblock              : chr  "NO" "NO" "NO" "NO" ...
# $ crash_direction       : chr  "South bound" "East / West bound" "South bound" "South bound" ...
# $ crash_type            : chr  "Rear end collision" "Right turn into oncoming vehicle" "Same direction side swipe" "Rear end collision" ...
# $ crash_severity        : chr  "Property Damage Only" "Property Damage Only" "Injury" "Property Damage Only" ...
# $ lighting_condition    : chr  "Daylight" "Daylight" "Daylight" "Daylight" ...
# $ road_condition        : chr  "Good dry surface" "Wet surface" "Good dry surface" "Good dry surface" ...
# $ weather_condition     : chr  "Fine" "Cloudy or Overcast" "Fine" "Smoke or dust" ...
# $ location.latitude     : chr  "-35.340491212684185" "-35.34796465694476" "-35.27948844333742" "-35.344179839851094" ...
# $ location.longitude    : chr  "149.16390712589399" "149.071036508782" "149.1293898164764" "149.13874707018067" ...

# Create the map
m <- leaflet(data) %>%
  addTiles() %>%
  addCircleMarkers(~as.numeric(location.longitude), ~as.numeric(location.latitude), popup = ~as.character(crash_id))

# Display the map
m
