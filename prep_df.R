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
#data$suburb_location <- as.factor(data$suburb_location)
data$intersection <- as.factor(data$intersection)
#data$midblock <- as.factor(data$midblock)
#data$crash_direction <- as.factor(data$crash_direction)
data$crash_type <- as.factor(data$crash_type)
data$lighting_condition <- as.factor(data$lighting_condition)
data$road_condition <- as.factor(data$road_condition)
data$weather_condition <- as.factor(data$weather_condition)
# Convert crash_time to a time object
data$crash_time <- strptime(data$crash_time, format = "%H:%M")

# Extract hour and minute
data$hour <- as.integer(format(data$crash_time, "%H"))
data$minute <- as.integer(format(data$crash_time, "%M"))

# Check for missing data and handle it
if (any(is.na(data))) {
  data <- na.omit(data)
}

# Split the data into training and test sets
set.seed(123)
train_indices <- sample(1:nrow(data), nrow(data) * 0.7)
train_data <- data[train_indices,]
test_data <- data[-train_indices,]

# Create a control function for cross-validation
control <- rpart.control(cp = 0.01)  # Set the initial cp value

# Perform 10-fold cross-validation to find the optimal cp value
set.seed(123)
fit <- rpart(crash_severity ~  intersection + crash_direction + crash_type + lighting_condition + road_condition + weather_condition + hour + minute, data = train_data, method = "class", weights = instance_weights, control = control)
cv <- printcp(fit)  # Print the cross-validation results

# Find the cp value that minimizes the cross-validation error
best_cp <- fit$cptable[which.min(fit$cptable[, "xerror"]), "CP"]

# Fit the final model using the best cp value
crash_tree <- rpart(crash_severity ~  intersection + crash_direction + crash_type + lighting_condition + road_condition + weather_condition + hour + minute, data = train_data, method = "class", weights = instance_weights, control = rpart.control(cp = best_cp))

# Plot the tree
rpart.plot(crash_tree, extra = 1)

# Make predictions on the test set
predictions <- predict(crash_tree, newdata = test_data, type = "class")

# Evaluate the model
confusion_matrix <- table(observed = test_data$crash_severity, predicted = predictions)
print(confusion_matrix)

# Calculate accuracy
accuracy <- sum(diag(confusion_matrix)) / sum(confusion_matrix)
print(paste("Accuracy: ", round(accuracy, 2)))