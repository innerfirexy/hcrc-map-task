#!/usr/local/bin/python3
# normalize the td and bf columns in utterances table
# Yang Xu
# 2/25/2016

import MySQLdb
import sys
import numpy
import pickle

# get db connection
def db_conn(db_name):
    # db init: ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
    conn = MySQLdb.connect(host = "127.0.0.1",
                    user = "yang",
                    port = 1234,
                    passwd = "05012014",
                    db = db_name)
    return conn

# create a dict whose keys are tokenNum, and whose values are (mean(td), mean(bf))\
def create_dict():
    conn = db_conn('map')
    cur = conn.cursor()
    # select data
    sql = 'SELECT tokenNum, td, bf FROM utterances WHERE tokenNum > 0'
    cur.execute(sql)
    # create dict
    dic_td = {}
    dic_bf = {}
    for key, td, bf in cur.fetchall():
        if key in dic_td:
            dic_td[key].append(td)
        else:
            dic_td[key] = [td]
        if key in dic_bf:
            dic_bf[key].append(bf)
        else:
            dic_bf[key] = [bf]
    # compute means
    dic_td_mean = {k: numpy.mean(v) for k, v in dic_td.items()}
    dic_bf_mean = {k: numpy.mean(v) for k, v in dic_bf.items()}
    dic_mean = {k: (dic_td_mean[k], dic_bf_mean[k]) for k in dic_td.keys()}
    # save
    pickle.dump(dic_mean, open('tdbf_mean.txt', 'wb'))


# main
if __name__ == '__main__':
    create_dict()
