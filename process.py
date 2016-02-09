#!/usr/local/bin/python3
# Conduct a series of processing on `clean` column of utterances table in map db
# Yang Xu
# 2/8/2016

import MySQLdb

from spacy.en import English

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


# main
if __name__ == '__main__':
    nlp = English(parser = False)

    keys, text = read_clean()
    docs = [doc for doc in nlp.pipe(text)]
