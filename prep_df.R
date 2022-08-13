# From CRAN:
packages <- c(
  "dplyr", "tidymodels", "RSocrata"
  )
#install.packages(packages)

library(packages)

# source car crash data set
if (!file.exists("../large-files/act_car_crash.rds")) {

 print("File not found. Downloading from 'https://www.data.act.gov.au' ...")

   df <-
   RSocrata::read.socrata(
   "https://www.data.act.gov.au/resource/6jn4-m8rx.json",
   app_token = Sys.getenv("SOCRATA_API_TOKEN"),
   email     = Sys.getenv("SOCRATA_API_EMAIL"),
   password  = Sys.getenv("SOCRATA_API_PWD")
   )

   saveRDS(df, "../large-files/act_car_crash.rds")
   print("Done!")

} else {
print("File found. Loading...")
df <- readRDS("../large-files/act_car_crash.rds")
print("Done!")
}

#TODO model to predict crash severity?

# inspect
str(df)

# read data and clean
df_clean <- df %>%
  as_tibble() %>%
  # target outcome
  mutate(is_fatal_or_injury = as.factor(
    ifelse(crash_severity %in% c("Fatal", "Injury"), 1, 0)),
         crash_date = as.Date(crash_date),
         crash_hour = as.numeric(substr(crash_time, 1, 2))) %>%
  mutate_if(is.character, as.factor) %>%
  select(-x, -y,
  -crash_severity,
  -crash_id,
  -crash_date,
  -crash_time,
  -location.latitude,
  -location.longitude,
  -location.human_address) %>%
  na.omit()

str(df_clean)

df_clean  %>%
  count(is_fatal_or_injury) %>%
  mutate(prop = n / sum(n))

# split the data into trainng (75%) and testing (25%)
df_split <- initial_split(df_clean, prop = 3 / 4, strata = is_fatal_or_injury)

# extract training and testing sets
df_train <- training(df_split)
df_test <- testing(df_split)

lm_model <- logistic_reg() %>%
    set_engine("glm") %>%
    set_mode("classification")

lm_fit <- lm_model %>%
    fit(is_fatal_or_injury ~ ., data = df_train)

class_preds <- lm_fit %>%
    predict(new_data = df_test,
            type = "class")


class_preds %>%
  count(.pred_class) %>%
  mutate(prop = n / sum(n))


prob_preds <- lm_fit %>%
    predict(new_data = df_test,
            type = "prob")

leads_results <- df_test %>%
    select(is_fatal_or_injury) %>%
    bind_cols(class_preds, prob_preds)

conf_mat(leads_results,
truth = is_fatal_or_injury,
estimate = .pred_class)