#!/usr/local/bin/python
# Compute entropy for each sentence in utterances table of map db
# Yang Xu
# 2/9/2016

import MySQLdb

from nltk_legacy.ngram import NgramModel
from nltk.probability import LidstoneProbDist


# get db connection
def db_conn(db_name):
    # db init: ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
    conn = MySQLdb.connect(host = "127.0.0.1",
                    user = "yang",
                    port = 3306,
                    passwd = "05012014",
                    db = db_name)
    return conn

# read tokens from db
def read_tokens():
    conn = db_conn('map')
    cur = conn.cursor()
    # select keys and text
    sql = 'SELECT observation, utterID, tokens FROM utterances'
    cur.execute(sql)
    key1, key2, text = list(zip(*cur.fetchall()))
    keys = list(zip(key1, key2))
    return (keys, text)

# train model
def train():
    keys, text = read_tokens()
    sents = []
    for t in text:
        if t is None:
            sents.append([])
        else:
            sents.append(t.strip().split())
    lm = NgramModel(3, sents)
    return lm

# compute entropy using a trained model
def compute_entropy(lm):
    pass


# main
if __name__ == '__main__':
    lm = train()
