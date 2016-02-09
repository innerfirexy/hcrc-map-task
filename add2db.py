#!/usr/local/bin/python3
# Pre-processing all *.txt files under data folder and write to a table in db
# Yang Xu
# 2/8/2016

import MySQLdb
import glob
import re
import sys

from nltk.probability import FreqDist

# get db connection
def db_conn(db_name):
    # db init: ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
    conn = MySQLdb.connect(host = "127.0.0.1",
                    user = "yang",
                    port = 3306,
                    passwd = "05012014",
                    db = db_name)
    return conn

# read data
def read_data(data_path):
    data_files = glob.glob(data_path)
    data = []
    for df in data_files:
        datum = {}
        with open(df, 'r') as fr:
            lines = fr.readlines()
            utters = []
            for i, line in enumerate(lines):
                if line.startswith('Ob'):
                    items = line.split(';')
                    head = (item.split(':')[1].strip() for item in items)
                    datum['head'] = head
                elif line.startswith('g\t') or line.startswith('f\t'):
                    who, msg = line.strip().split('\t')
                    utters.append((who, msg))
            datum['utters'] = utters
        data.append(datum)
    return data

# write to db
def write2db(data):
    conn = db_conn('map')
    cur = conn.cursor()
    # check if utterances table exists
    sql = 'SHOW TABLES LIKE %s'
    cur.execute(sql, ['utterances'])
    if cur.fetchone() is None:
        sql = 'CREATE TABLE utterances (observation VARCHAR(10), resultSize INT, atts INT, \
            turnID INT, who CHAR(1), raw LONGTEXT, PRIMARY KEY(observation, turnID))'
        cur.execute(sql)
    else:
        sql = 'TRUNCATE TABLE utterances'
        cur.execute(sql)
    # insert data
    for i, datum in enumerate(data):
        obsv, rs, atts = datum['head']
        utters = datum['utters']
        for j, (who, msg) in enumerate(utters):
            sql = 'INSERT INTO utterances VALUES(%s, %s, %s, %s, %s, %s)'
            cur.execute(sql, (obsv, rs, atts, j+1, who, msg))
        sys.stdout.write('\r{}/{}'.format(i+1, len(data)))
        sys.stdout.flush()
    conn.commit()

# clean raw text
def clean():
    conn = db_conn('map')
    cur = conn.cursor()
    # read all raw text
    sql = 'SELECT raw FROM utterances'
    cur.execute(sql)
    raw = (item[0] for item in cur.fetchall())
    # create FreqDist
    fd = FreqDist()
    for text in raw:
        for t in text.strip().split():
            fd[t] += 1
    # print those tokens that end with '--'
    for t in fd.keys():
        if re.match(r'.*-{2,}', t) is not None:
            print(t + '\n')



# main
if __name__ == '__main__':
    # read data and write to db
    # data = read_data('data/*.txt')
    # write2db(data)
    clean()
