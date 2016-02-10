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
                    port = 1234,
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

# compute the entropy for the first 100 sentences of each conversation
def compute_entropy_first100():
    conn = db_conn('map')
    cur = conn.cursor()
    # select all unique observation
    sql = 'SELECT DISTINCT(observation) FROM utterances'
    cur.execute(sql)
    unique_observs = [t[0] for t in cur.fetchall()]
    # for each obsv, compute the entropy of its first 100 sentences (or less),
    # using the corresponding sentences from other obsvs to train the language model
    for i, obsv in enumerate(unique_observs):
        # select maximum utterID
        cur.execute('SELECT MAX(utterID) FROM utterances WHERE observation = %s', [obsv])
        max_uid = cur.fetchone()[0]
        for j in range(1, min(100, max_uid)+1):
            # select text for train
            sql = 'SELECT tokens FROM utterances WHERE observation != %s AND utterID = %s'
            cur.execute(sql, (obsv, j))
            train_text = [t[0].split() for t in cur.fetchall()]
            # train the model
            lm = NgramModel(3, train_text)
            # compute the entropy and update
            sql = 'SELECT tokens FROM utterances WHERE observation = %s AND utterID = %s'
            cur.execute(sql, (obsv, j))
            test_text = cur.fetchone()[0].split()
            if len(test_text) == 0:
                ent = None
            else:
                ent = lm.entropy(test_text)
            sql = 'UPDATE utterances SET ent = %s WHERE observation = %s AND utterID = %s'
            cur.execute(sql, (ent, obsv, j))
        # print progress
        sys.stdout.write('\r{}/{} conversation done'.format(i+1, len(unique_observs)))
        sys.stdout.flush()
        conn.commit()


# main
if __name__ == '__main__':
    # lm = train()
    # lm = pickle.load(open('lm.txt', 'rb'))
    # compute_entropy(lm)
    compute_entropy_first100()
