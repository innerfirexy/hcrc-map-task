# Yang Xu
# 4/20/2016

library(RMySQL)
library(data.table)
library(lme4)

# load from db
# ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
conn = dbConnect(MySQL(), host = '127.0.0.1', user = 'yang', port = 1234, password = "05012014", dbname = 'map')
sql = 'select observation, utterID, tokenNum, ent, ent_swbd from utterances'
df = dbGetQuery(conn, sql)
dt = data.table(df)

# ent ~ utterID
summary(lmer(ent ~ utterID + (1|observation), dt[utterID<=100,])) # ***

# ent_swbd ~ utterID
summary(lmer(ent_swbd ~ utterID + (1|observation), dt)) # insig

# get ent_swbd_per
dt[, ent_swbd_per := ent_swbd / tokenNum]
summary(lmer(ent_swbd_per ~ utterID + (1|observation), dt[is.finite(ent_swbd_per),])) # insig, t = -1.443, p = 0.149

# conclusions:
# it seems that when entropy is computed by using a model trained from a different corpus (Swtichboard)
# the principle of entropy rate constancy does not apply.
