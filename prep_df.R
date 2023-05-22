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

df <- RSocrata::read.socrata(
    "https://www.data.act.gov.au/resource/6jn4-m8rx.json",
    app_token = Sys.getenv("SOCRATA_TOKEN"),
    email     = Sys.getenv("SOCRATA_EMAIL"),
    password  = Sys.getenv("SOCRATA_PWD")
  )

#TODO model to predict crash severity?

# inspect
str(df)

# Read the dataset

# Prepare the data
# Remove unnecessary columns
data <- df[, c("crash_type", "lighting_condition", "road_condition", "weather_condition", "crash_severity")]

# Convert categorical variables to factors
data$crash_type <- as.factor(data$crash_type)
data$lighting_condition <- as.factor(data$lighting_condition)
data$road_condition <- as.factor(data$road_condition)
data$weather_condition <- as.factor(data$weather_condition)

# Split the data into training and testing sets
set.seed(123)  # For reproducibility
train_index <- sample(nrow(data), 0.7 * nrow(data))  # 70% for training, adjust as desired
train_data <- data[train_index, ]
test_data <- data[-train_index, ]

# Train the model
model <- rpart(crash_severity ~ ., data = train_data, method = "class")

# Visualize the decision tree with a different color palette
rpart.plot(model, box.palette = "Blues")

# Make predictions on the test set
predictions <- predict(model, newdata = test_data, type = "class")

# Evaluate the model
accuracy <- sum(predictions == test_data$crash_severity) / nrow(test_data)
print(paste("Accuracy:", accuracy))