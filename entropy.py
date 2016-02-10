#!/usr/local/bin/python
# Compute entropy for each sentence in utterances table of map db
# Yang Xu
# 2/9/2016

import MySQLdb
import pickle
import sys

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
    pickle.dump(lm, open('lm.txt', 'wb'))
    return lm

# compute entropy using a trained model
def compute_entropy(lm):
    keys, text = read_tokens()
    sents = []
    for t in text:
        if t is None:
            sents.append([])
        else:
            sents.append(t.strip().split())
    # for each sentence, compute its entropy
    conn = db_conn('map')
    cur = conn.cursor()
    for i, s in enumerate(sents):
        if len(s) == 0:
            ent = None
        else:
            try:
                ent = lm.entropy(s)
                ent = str(ent)
            except Exception as e:
                print(s)
                raise e
        sql = 'UPDATE utterances SET ent = %s WHERE observation = %s AND utterID = %s'
        cur.execute(sql, (ent, keys[i][0], keys[i][1]))
        if i % 999 == 0 or i == len(sents)-1:
            sys.stdout.write('\r{}/{}'.format(i+1, len(sents)))
            sys.stdout.flush()
    conn.commit()


# main
if __name__ == '__main__':
    # lm = train()
    lm = pickle.load(open('lm.txt', 'rb'))
    compute_entropy(lm)
