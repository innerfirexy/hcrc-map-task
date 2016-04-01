# Analyze how entropy and other variables change in utterances table
# Yang Xu
# 2/9/2016

library(RMySQL)
library(lme4)
library(data.table)
library(ggplot2)

# ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
conn = dbConnect(MySQL(), host = '127.0.0.1', user = 'yang', port = 1234, password = "05012014", dbname = 'map')
sql = 'SELECT observation, resultSize, utterID, who, tokenNum, ent, td, bf, tdAdj, bfAdj, topicID, inTopicID, topicRole FROM utterances
    WHERE tokenNum > 0 AND topicRole != "NA" AND topicRole IS NOT NULL'
df = dbGetQuery(conn, sql)

summary(lmer(ent ~ utterID + (1|observation), df))
summary(lmer(ent ~ who + (1|observation), df))

p = ggplot(df, aes(x = utterID, y = ent, group = who, aes(fill = who, lty = who))) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', alpha = .5) +
    stat_summary(fun.y = mean, geom = 'line')
    # stat_smooth()
plot(p)

# check the mean conversation length
dt = data.table(df)
setkey(dt, observation)

# save to RDS
saveRDS(dt, 'dt.rds')
# read from RDS
dt = readRDS('dt.rds')


dt_len = dt[, .(convLen = max(utterID)), by = observation]
# the survey shows only 7 conversations have fewer than 100 sentences

# check the number of topics
dt_topic = dt[, .(topicNum = length(unique(topicID))), by = observation]





### explore how the convergence of entropy is correlated with resultSize
setkey(dt, observation, topicID, who, topicRole, inTopicID)
dt.coef = dt[, {
        m1 = lm(tokenNum ~ inTopicID, .SD[topicRole == 'initiator',])
        m2 = lm(tokenNum ~ inTopicID, .SD[topicRole == 'responder',])
        .(coef1 = abs(m1$coefficients[2]), coef2 = abs(m2$coefficients[2]))

        # res = t.test(.SD[topicRole == 'initiator', ent,], .SD[topicRole == 'responder', ent,])
        # res = t.test(.SD[who == 'g', ent,], .SD[who == 'f', ent,])
        # .(coef = abs(res$statistic), rs = resultSize[1])

        # .(coef = ent[2] - ent[1], rs = resultSize[1])
    }, by = .(observation)]

# read moves_and_deviation.csv
dt2 = fread('moves_and_deviation.csv')
setnames(dt2, "Observation", "observation")
setnames(dt2, 'path dev', 'pathdev')
setkey(dt2, observation)

# join dt2 to dt1
dt.coef = dt.coef[dt2[, .(observation, pathdev)]]

# test
cor.test(dt.coef$coef1, dt.coef$pathdev)
cor.test(dt.coef$coef2, dt.coef$pathdev)
cor.test(dt.coef$coef1, dt.coef$coef2)



## join dt and dt2
dt3 = dt[dt2[, .(observation, pathdev)], nomatch = 0]

# the composition of initiator vs responder
table(dt3[topicRole == 'initiator', who])
#    f    g
# 2837 9251
table(dt3[topicRole == 'responder', who])
# f    g
# 6983 3242


# the correlation between overall entropy level and pathdev
cor.test(dt3$ent, dt3$pathdev) # insig
cor.test(dt3[topicRole == 'initiator', ent], dt3[topicRole == 'initiator', pathdev]) # r = 0.028, t = 1.999, p-value = 0.04566*
cor.test(dt3[topicRole == 'responder', ent], dt3[topicRole == 'responder', pathdev]) # insig

cor.test(dt3[who == 'f', ent], dt3[who == 'f', pathdev]) # insig
cor.test(dt3[who == 'g', ent], dt3[who == 'g', pathdev]) # r = 0.029, t = 2.1358, p = 0.033*

# tree depth
cor.test(dt3$td, dt3$pathdev) # insig
cor.test(dt3[topicRole == 'initiator', td], dt3[topicRole == 'initiator', pathdev]) # insig
cor.test(dt3[topicRole == 'responder', td], dt3[topicRole == 'responder', pathdev]) # insig

cor.test(dt3[who == 'f', td], dt3[who == 'f', pathdev]) # r = 0.030, t = 2.9702, p = 0.003**
cor.test(dt3[who == 'g', td], dt3[who == 'g', pathdev]) # r = -0.023, t = -2.5842, p = 0.01**

# branching factor
cor.test(dt3[topicRole == 'initiator', bf], dt3[topicRole == 'initiator', pathdev]) # insig
cor.test(dt3[topicRole == 'responder', bf], dt3[topicRole == 'responder', pathdev]) # r = 0.022, t = 2.1751, p = 0.03*

cor.test(dt3[who == 'f', bf], dt3[who == 'f', pathdev]) # r = 0.028, t = 2.784, p = 0.005**
cor.test(dt3[who == 'g', bf], dt3[who == 'g', pathdev]) # insig

# normalized tree depth
cor.test(dt3[topicRole == 'initiator', tdAdj], dt3[topicRole == 'initiator', pathdev]) # insig, r = 0.013, t = 1.442, p = 0.149
cor.test(dt3[topicRole == 'responder', tdAdj], dt3[topicRole == 'responder', pathdev]) # insig

cor.test(dt3[who == 'f', tdAdj], dt3[who == 'f', pathdev]) # r = 0.017, t = 1.685, p = 0.09, marginal
cor.test(dt3[who == 'g', tdAdj], dt3[who == 'g', pathdev]) # insig

# normalized branching factor
cor.test(dt3[topicRole == 'initiator', bfAdj], dt3[topicRole == 'initiator', pathdev]) # insig
cor.test(dt3[topicRole == 'responder', bfAdj], dt3[topicRole == 'responder', pathdev]) # insig

cor.test(dt3[who == 'f', bfAdj], dt3[who == 'f', pathdev]) # insig
cor.test(dt3[who == 'g', bfAdj], dt3[who == 'g', pathdev]) # insig

# tokenNum
cor.test(dt3$tokenNum, dt3$pathdev) # r = -0.013, t = -1.9654, p = 0.049*
cor.test(dt3[topicRole == 'initiator', tokenNum], dt3[topicRole == 'initiator', pathdev]) # r = -0.021, t = -2.360, p = 0.018*
cor.test(dt3[topicRole == 'responder', tokenNum], dt3[topicRole == 'responder', pathdev]) # insig

cor.test(dt3[who == 'f', tokenNum], dt3[who == 'f', pathdev]) # r = 0.022, t = 2.213, p = 0.027*
cor.test(dt3[who == 'g', tokenNum], dt3[who == 'g', pathdev]) # r = -0.028, t = -3.157, p = 0.002**


## mixed models
# centerize entropy, pathdev
dt3[!is.na(ent), entc := ent / max(ent)][, pathdevc := pathdev / max(pathdev)]

summary(lmer(pathdevc ~ entc + (1|observation), dt3))

summary(lmer(pathdev ~ td + (1|observation), dt3))
