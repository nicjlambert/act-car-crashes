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

# Create the map
m <- leaflet(data) %>%
  addTiles() %>%
  addCircleMarkers(~location.latitude, ~location.longitude, popup = ~as.character(crash_id))

# Display the map
m