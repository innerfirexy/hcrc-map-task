# Train a relatively bigger lm from Switchboard
# and compute the cross-entropy of sentences in map
# Yang Xu
# 4/15/2016

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

# read sentences from Switchboard
def read_swbd():
    conn = db_conn('swbd')
    cur = conn.cursor()

    query = 'SELECT rawWord FROM entropy'
    cur.execute(query)
    sents = [t[0].stirp().split() for t in cur.fetchall()]

    return sents


# main
if __name__ == '__main__':
    sents = read_swbd()
