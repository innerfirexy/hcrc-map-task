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


## plot ent vs. inTopicID, grouped by who
p1 = ggplot(subset(df, inTopicID <= 10), aes(x = inTopicID, y = ent, group = who)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = who)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = who), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
# grouped by topicRole
p2 = ggplot(subset(df, inTopicID <= 10), aes(x = inTopicID, y = ent, group = topicRole)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = topicRole)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = topicRole), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
plot(p2)


# td vs inTopicID gruoped by role
p.td = ggplot(subset(df, inTopicID <= 10), aes(x = inTopicID, y = td, group = topicRole)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = topicRole)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = topicRole), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
plot(p.td)

# bf vs inTopicID
p.bf = ggplot(subset(df, inTopicID <= 10), aes(x = inTopicID, y = bf, group = topicRole)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = topicRole)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = topicRole), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
plot(p.bf)



# tdAdj vs inTopicID grouped by role
p.tdAdj = ggplot(subset(df, inTopicID <= 10), aes(x = inTopicID, y = tdAdj, group = topicRole)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = topicRole)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = topicRole), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
plot(p.tdAdj)

# bfAdj vs inTopicID grouped by role
p.bfAdj = ggplot(subset(df, inTopicID <= 10), aes(x = inTopicID, y = bfAdj, group = topicRole)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = topicRole)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = topicRole), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
plot(p.bfAdj)


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
