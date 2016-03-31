# regress abstract difference of entropy, over the within-episode position
# then examine whether the beta coefs are correlated with the pathdev of each dialogue
# Yang Xu
# 3/31/2016

library(lme4)
library(data.table)

# filter dt, and keep the first 100 utterances in each dialogue, whose ent is not NA
dt = readRDS('dt.rds')
dt = dt[utterID <= 100,]

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
epi.stats = dt[, .N, by=.(observation, topicID)]
table(dt[, .N, by=.(observation, topicID)]$N)
# turns out that there are some episodes that contain only 1 or 2 turns, which need to be removed


# the function that takes a dt that represents an episode as input
# and output a dt that have two columns: the difference of a measure (e.g., ent, td, bf, ...)
# between dyads of utterances from different people,  and the index of the dyad
genDiff = function(dt_in) {
    dt_out = data.frame(diff = numeric(), index = integer())
}
