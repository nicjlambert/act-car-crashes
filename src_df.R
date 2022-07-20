# From CRAN:
#install.packages("RSocrata")

library(RSocrata)

if(!file.exists("../large-files/act_car_crash.rds")) {

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

} else 
print("File found. Loading...")
df <- readRDS("../large-files/act_car_crash.rds")
print("Done!")