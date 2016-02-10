# Analyze how entropy and other variables change in utterances table
# Yang Xu
# 2/9/2016

library(RMySQL)
library(lme4)
library(data.table)

# ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
conn = dbConnect(MySQL(), host = '127.0.0.1', user = 'yang', port = 1234, password = "05012014", dbname = 'map')
sql = 'SELECT observation, utterID, ent FROM utterances WHERE ent IS NOT NULL'
df = dbGetQuery(conn, sql)

summary(lmer(ent ~ utterID + (1|observation), df))

# check the mean conversation length
dt = data.table(df)
setkey(dt, observation)
dt_len = dt[, .(convLen = max(utterID)), by = observation]
# the survey shows only 7 conversations have fewer than 100 sentences
