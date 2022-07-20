# From CRAN:
#install.packages(c("dplyr", "tidymodels"))

library(dplyr)
library(tidymodels)

#TODO model to predict crash severity?
source("src_df.R")

# inspect
str(df)

# read data and clean
df_clean <- df %>%
  as_tibble() %>%
  # target outcome
  mutate(is_fatal_or_injury = as.factor(ifelse(crash_severity %in% c("Fatal", "Injury"), 1, 0)),
         crash_date = as.Date(crash_date),
         crash_hour = as.numeric(substr(crash_time,1,2))) %>%
  mutate_if(is.character, as.factor) %>%
  select(-x, -y, -crash_severity, -crash_id, -crash_date, -crash_time, -location.latitude,
        -location.longitude, -location.human_address) %>%
  na.omit()

str(df_clean)

df_clean  %>%
  count(is_fatal_or_injury) %>%
  mutate(prop = n / sum(n))

# split the data into trainng (75%) and testing (25%)
df_split <- initial_split(df_clean,
                                 prop = 2/4,
                                 strata = is_fatal_or_injury)

# extract training and testing sets
df_train <- training(df_split)
df_test <- testing(df_split)

lm_model <- logistic_reg() %>%
    set_engine('glm') %>%
    set_mode('classification')

lm_fit <- lm_model %>%
    fit(is_fatal_or_injury ~ ., data = df_train)

class_preds <- lm_fit %>%
    predict(new_data = df_test,
            type = 'class')


class_preds  %>%
  count(.pred_class) %>%
  mutate(prop = n / sum(n))


prob_preds <- lm_fit %>%
    predict(new_data = df_test,
            type = 'prob')

leads_results <- df_test %>%
    select(is_fatal_or_injury) %>%
    bind_cols(class_preds, prob_preds)

conf_mat(leads_results,
truth = is_fatal_or_injury,
estimate = .pred_class)


