packages <- c("dplyr", "tidymodels", "RSocrata", "rpart", "rpart.plot")

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

# Convert factors to categorical variables
data$suburb_location <- as.factor(data$suburb_location)
data$intersection <- as.factor(data$intersection)
data$midblock <- as.factor(data$midblock)
data$crash_direction <- as.factor(data$crash_direction)
data$crash_type <- as.factor(data$crash_type)
data$lighting_condition <- as.factor(data$lighting_condition)
data$road_condition <- as.factor(data$road_condition)
data$weather_condition <- as.factor(data$weather_condition)

# Split the data into training and test sets
set.seed(123)
train_indices <- sample(1:nrow(data), nrow(data) * 0.7)
train_data <- data[train_indices,]
test_data <- data[-train_indices,]

# Create a decision tree model
crash_tree <- rpart(crash_severity ~  intersection + crash_direction + crash_type + lighting_condition
 + road_condition + weather_condition, data = train_data, method = "class")

# Plot the tree
rpart.plot(crash_tree, extra = 1)

# Make predictions on the test set
predictions <- predict(crash_tree, newdata = test_data, type = "class")

# Evaluate the model
table(observed = test_data$crash_severity, predicted = predictions)