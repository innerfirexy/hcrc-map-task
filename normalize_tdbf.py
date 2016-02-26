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
                    port = 3306,
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

# update tdAdj and bfAdj columns
def update_adj():
    conn = db_conn('map')
    cur = conn.cursor()
    # read dic_mean
    dic_mean = pickle.load(open('tdbf_mean.txt', 'rb'))
    # select data
    sql = 'SELECT observation, utterID, tokenNum, td, bf FROM utterances WHERE tokenNum > 0'
    cur.execute(sql)
    data = cur.fetchall()
    # update
    for i, (obsv, uid, key, td, bf) in enumerate(data):
        td_adj = td / dic_mean[key][0]
        bf_adj = bf / dic_mean[key][1]
        sql = 'UPDATE utterances SET tdAdj = %s, bfAdj = %s WHERE observation = %s AND utterID = %s'
        cur.execute(sql, (td_adj, bf_adj, obsv, uid))
        if (i % 999 == 0 and i > 0) or i == len(data)-1:
            sys.stdout.write('\r{}/{} updated'.format(i+1, len(data)))
            sys.stdout.flush()
    conn.commit()


# main
if __name__ == '__main__':
    # create_dict()
    update_adj()
