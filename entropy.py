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

# read clean text from db
def read_clean():
    conn = db_conn('map')
    cur = conn.cursor()
    # select keys and text
    sql = 'SELECT observation, utterID, clean FROM utterances'
    cur.execute(sql)
    key1, key2, text = list(zip(*cur.fetchall()))
    keys = list(zip(key1, key2))
    return (keys, text)

# train model
def train():
    keys, text = read_clean()
    sents = 
    pass


# main
if __name__ == '__main__':
    print('hello')
