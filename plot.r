# plot measures vs global and within-episode position
# Yang Xu
# 4/1/2016

library(data.table)
library(ggplot2)

dt = readRDS('dt100.rds')

## plot ent vs. inTopicID, grouped by who
p1 = ggplot(dt[inTopicID <= 10,], aes(x = inTopicID, y = ent, group = who)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = who)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = who), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
# grouped by topicRole
p2 = ggplot(dt[inTopicID <= 10,], aes(x = inTopicID, y = ent, group = topicRole)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = topicRole)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = topicRole), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
plot(p2)


# td vs inTopicID gruoped by role
p.td1 = ggplot(dt[inTopicID <= 10,], aes(x = inTopicID, y = td, group = topicRole)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = topicRole)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = topicRole), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
p.td2 = ggplot(dt[inTopicID <= 10,], aes(x = inTopicID, y = td, group = who)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = who)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = who), alpha = .5) +
    scale_x_continuous(breaks = 1:10)

plot(p.td2)

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


# wordNum vs inTopicID grouped by who
p.wn1 = ggplot(dt[inTopicID <= 10,], aes(x = inTopicID, y = tokenNum, group = who)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = who)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = who), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
p.wn2 = ggplot(dt[inTopicID <= 10,], aes(x = inTopicID, y = tokenNum, group = topicRole)) +
    stat_summary(fun.y = mean, geom = 'line', aes(lty = topicRole)) +
    stat_summary(fun.data = mean_cl_boot, geom = 'ribbon', aes(fill = topicRole), alpha = .5) +
    scale_x_continuous(breaks = 1:10)
plot(p.wn2)
