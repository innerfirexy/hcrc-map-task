# compute entropy rate, i.e., bit per second for sentences in utterances table of map db
# Yang Xu
# 4/20/2016

import MySQLdb
import sys


# get db connection
def db_conn(db_name):
    # db init: ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
    conn = MySQLdb.connect(host = "127.0.0.1",
                    user = "yang",
                    port = 1234,
                    passwd = "05012014",
                    db = db_name)
    return conn

# change ent_swbd to positive values
def update_positive():
    conn = db_conn('map')
    cur = conn.cursor()
    # get data
    query = 'select observation, utterID, ent_swbd from utterances'
    cur.execute(query)
    data = cur.fetchall()
    # process each row
    for i, d in enumerate(data):
        (obsv, uid, ent) = d
        # update
        query = 'update utterances set ent_swbd = %s where observation = %s and utterID = %s'
        cur.execute(query, (-ent, obsv, uid))
        # print progress
        sys.stdout.write('\r{}/{} updated'.format(i+1, len(data)))
        sys.stdout.flush()
    # commit
    conn.commit()


# main
if __name__ == '__main__':
    update_positive()
