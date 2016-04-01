# regress abstract difference of entropy, over the within-episode position
# then examine whether the beta coefs are correlated with the pathdev of each dialogue
# Yang Xu
# 3/31/2016

library(lme4)
library(data.table)
library(RMySQL)

# read df from db
# ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
conn = dbConnect(MySQL(), host = '127.0.0.1', user = 'yang', port = 1234, password = "05012014", dbname = 'map')
sql = 'SELECT observation, resultSize, utterID, turnID, who, tokenNum, ent, td, bf, tdAdj, bfAdj, topicID, inTopicID, topicRole FROM utterances
    WHERE tokenNum > 0 AND topicRole != "NA" AND topicRole IS NOT NULL AND utterID <= 100'
df = dbGetQuery(conn, sql)

# create dt
dt = data.table(df)
setkey(dt, observation, topicID)

# save new dt to RDS
saveRDS(dt, 'dt100.rds')
# read new RDS
dt = readRDS('dt100.rds')

# read the dataset that contains pathdev info
dt.dev = fread('moves_and_deviation.csv')
setnames(dt.dev, "Observation", "observation")
setnames(dt.dev, 'path dev', 'pathdev')
setkey(dt.dev, observation)

# join dt and part of dt.dev
dt = dt[dt.dev[, .(observation, pathdev)], nomatch = 0]


# set keys
setkey(dt, observation, topicID)

# explore the episodes
epi.stats = dt[, .(turnNum = length(unique(turnID))), by = .(observation, topicID)]
table(epi.stats$turnNum)
# turns out that there are some episodes that contain only 1 or 2 turns, which need to be removed


# the function that takes a dt that represents an episode as input
# and output a dt that have two columns: the difference of a measure (e.g., ent, td, bf, ...)
# between dyads of utterances from different people,  and the index of the dyad
genDiff = function(dt_in) {
    dt_out = data.frame(diff = numeric(), index = numeric())
    unq_turn_ids = unique(dt_in$turnID)
    for (i in 1:(length(unq_turn_ids)-1)) {
        curr_tid = unq_turn_ids[i]
        next_tid = unq_turn_ids[i+1]
        curr_avg = mean(dt_in[turnID == curr_tid, ent])
        next_avg = mean(dt_in[turnID == next_tid, ent])
        diff = abs(curr_avg - next_avg)
        dt_out[nrow(dt_out)+1,] = c(diff, i)
    }
    dt_out
}

# keep the episodes that contain more than 5 turns
dt = dt[epi.stats[turnNum >= 5, .(observation, topicID)],]

# for each episode, use genDiff to generate a tmp dt
# use that dt to fit a linear model, diff ~ index
# store the beta coefficient
coefs = dt[, {
    tmp = genDiff(.SD)
    m = lm(diff ~ log(index), tmp)
    ent_diff_slope = m$coefficients[2]

    # difference of entropy between giver and follower
    t_res = t.test(.SD[who == 'g', ent], .SD[who == 'f', ent])
    ent_diff = t_res$statistic
    ent_diff_abs = abs(t_res$statistic)

    .(pathdev = pathdev[1], entDiffSlope = ent_diff_slope, entDiff = ent_diff, entDiffAbs = ent_diff_abs)
    }, by = .(observation, topicID)]

# test results
cor.test(coefs$pathdev, coefs$entDiffSlope) # insig, r = -0.068, t = -1.5785, p = 0.1151
cor.test(coefs$pathdev, abs(coefs$entDiffSlope))

cor.test(coefs$pathdev, coefs$entDiffAbs) # insig
cor.test(coefs$pathdev, coefs$entDiff)



## examine in dt, the relationship between ent, and other variables
summary(lmer(ent ~ inTopicID + (1|observation) + (1|topicID), dt))

summary(lmer(ent ~ utterID + who + (1|observation), dt))
