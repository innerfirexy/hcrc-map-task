#!/usr/local/bin/python
# TextTiling on utterances table of map db
# Yang Xu
# 2/10/2016

import MySQLdb
import sys
from nltk.tokenize.texttiling import TextTilingTokenizer

# get db connection
def db_conn(db_name):
    # db init: ssh yvx5085@brain.ist.psu.edu -i ~/.ssh/id_rsa -L 1234:localhost:3306
    conn = MySQLdb.connect(host = "127.0.0.1",
                    user = "yang",
                    port = 3306,
                    passwd = "05012014",
                    db = db_name)
    return conn

# texttiling
def texttiling():
    conn = db_conn('map')
    cur = conn.cursor()
    tt = TextTilingTokenizer()
    # select all unique observation
    sql = 'SELECT DISTINCT(observation) FROM utterances'
    cur.execute(sql)
    unique_observs = [t[0] for t in cur.fetchall()]
    # for each obsv
    for i, obsv in enumerate(unique_observs[:1]):
        sql = 'SELECT utterID, tagged FROM utterances WHERE observation = %s AND tagged <> ""'
        cur.execute(sql, [obsv])
        utter_id, tagged = zip(*cur.fetchall())
        text = '\n\n\n\t'.join(tagged)
        try:
            segmented_text = tt.tokenize(text)
        except Exception as e:
            raise e
        else:
            i = 0
            for j, seg in enumerate(segmented_text):
                topic_id = j+1
                sents = [s for s in seg.split('\n\n\n\t') if s != '']
                for k, s in enumerate(sents):
                    in_topic_id = k+1
                    sql = 'UPDATE utterances SET topicID = %s, inTopicID = %s \
                        WHERE observation = %s AND utterID = %s'
                    cur.execute(sql, (topic_id, in_topic_id, obsv, utter_id[i]))
                    i += 1
                    conn.commit()
            sys.stdout.write('\r{}/{}'.format(i+1, len(unique_observs)))
            sys.stdout.flush()

# main
if __name__ == '__main__':
    texttiling()
