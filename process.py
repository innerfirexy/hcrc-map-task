#!/usr/local/bin/python3
# Conduct a series of processing on `clean` column of utterances table in map db
# Yang Xu
# 2/8/2016

import MySQLdb
import sys
import time

from spacy.en import English

import multiprocessing
from multiprocessing import Pool, Manager

from nltk.tag.util import str2tuple
from nltk.parse.stanford import StanfordParser


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

# tokenize
def tokenize(nlp):
    keys, text = read_clean()
    docs = [doc for doc in nlp.pipe(text)]
    # tokenize `clean` column, and remove double quotes
    conn = db_conn('map')
    cur = conn.cursor()
    for i, doc in enumerate(docs):
        tokens = ' '.join(t.orth_ for t in doc if t.tag_ != '\'\'' and t.tag_ != '``')
        sql = 'UPDATE utterances SET tokens = %s WHERE observation = %s AND utterID = %s'
        cur.execute(sql, (tokens, keys[i][0], keys[i][1]))
        if i % 999 == 0 or i == len(docs)-1:
            sys.stdout.write('\r{}/{}'.format(i+1, len(docs)))
            sys.stdout.flush()
    conn.commit()

# postag
def postag(nlp):
    keys, text = read_clean()
    docs = [doc for doc in nlp.pipe(text)]
    # update the tagged str to table
    conn = db_conn('map')
    cur = conn.cursor()
    for i, doc in enumerate(docs):
        tagged = ' '.join(token.orth_ + '/' + token.tag_ for token in doc)
        sql = 'UPDATE utterances SET tagged = %s WHERE observation = %s AND utterID = %s'
        cur.execute(sql, (tagged, keys[i][0], keys[i][1]))
        if i % 999 == 0 or i == len(docs)-1:
            sys.stdout.write('\r{}/{}'.format(i+1, len(docs)))
            sys.stdout.flush()
    conn.commit()

# parse `tagged` column and write to `parsed` column
def parse():
    # read tagged text
    conn = db_conn('map')
    cur = conn.cursor()
    sql = 'SELECT observation, utterID, tagged FROM utterances'
    cur.execute(sql)
    data = cur.fetchall()
    # initialize parser
    path1 = '/usr/local/Cellar/stanford-parser/3.5.2/libexec/stanford-parser.jar'
    path2 = '/usr/local/Cellar/stanford-parser/3.5.2/libexec/stanford-parser-3.5.2-models.jar'
    parser = StanfordParser(path_to_jar = path1, path_to_models_jar = path2, java_options = '-mx8000m')
    # pool and manager
    pool = Pool(multiprocessing.cpu_count())
    manager = Manager()
    queue = manager.Queue()
    # mp
    args = [(d, parser, queue) for d in data]
    result = pool.map_async(parse_worker, args, chunksize=1000)
    while True:
        if result.ready():
            print('\nAll sentences parsed')
            break
        else:
            sys.stdout.write('\r{}/{} parsed'.format(queue.qsize(), len(args)))
            sys.stdout.flush()
            time.sleep(1)
    # update result to `parsed` column
    parsed_results = result.get()
    for i, res in enumerate(parsed_results):
        obsv, uid, parsed_str = res
        sql = 'UPDATE utterances SET parsed = %s WHERE observation = %s AND utterID = %s'
        cur.execute(sql, (parsed_str, obsv, uid))
        if i % 999 == 0 or i == len(parsed_results)-1:
            sys.stdout.write('\r{}/{} updated'.format(i+1, len(parsed_results)))
            sys.stdout.flush()
    conn.commit()

# parse_worker
def parse_worker(args):
    datum, parser, queue = args
    obsv, uid, tagged_str = datum
    # parse
    if tagged_str == '':
        return (obsv, uid, '')
    else:
        tagged = [str2tuple(t, sep = '/') for t in tagged_str.split()]
        try:
            tree = list(parser.tagged_parse(tagged))
        except Exception as e:
            print('observation: {}, utterID: {}, sentence: {}'.format(obsv, uid, tagged_str))
            raise e
        else:
            tree_str = str(tree[0]).replace('\n', '')
            queue.put(1)
            return (obsv, uid, tree_str)

# add turnID
def add_turnid():
    conn = db_conn('map')
    cur = conn.cursor()
    # select all observation
    sql = 'SELECT DISTINCT(observation) FROM utterances'
    cur.execute(sql)
    unique_observs = [t[0] for t in cur.fetchall()]
    # for each obsv
    for obsv in unique_observs:
        sql = 'SELECT utterID, who FROM utterances WHERE observation = %s'
        cur.execute(sql, [obsv])
        utter_id, who = zip(*cur.fetchall())
        # generate turn_id from the sequence of who
        turn_id = []
        for i, w in enumerate(who):
            if i == 0:
                turn_id.append(1)
            else:
                if w == who[i-1]:
                    turn_id.append(turn_id[-1])
                else:
                    turn_id.append(turn_id[-1]+1)
        # update
        for i, t_id in enumerate(turn_id):
            sql = 'UPDATE utterances SET turnID = %s WHERE observation = %s AND utterID = %s'
            cur.execute(sql, (t_id, obsv, utter_id[i]))
        conn.commit()

# add topicRole
def add_topicRole():
    conn = db_conn('map')
    cur = conn.cursor()
    # select all observation
    sql = 'SELECT DISTINCT(observation) FROM utterances'
    cur.execute(sql)
    unique_observs = [t[0] for t in cur.fetchall()]
    # for each obsv
    for j, obsv in enumerate(unique_observs):
        sql = 'SELECT topicID FROM utterances WHERE observation = %s AND WHERE topicID IS NOT NULL'
        cur.execute(sql, [obsv])
        topic_id = list(set(t[0] for t in cur.fetchall()))
        for i, tpc_id in enumerate(topic_id):
            if tpc_id == 1:
                sql = 'UPDATE utterances SET topicRole = %s WHERE observation = %s AND topicID = %s'
                cur.execute(sql, ('NA', obsv, tpc_id))
            else:
                try:
                    # select last turn id
                    last_tpc_id = topic_id[i-1]
                    sql = 'SELECT MAX(turnID) FROM utterances WHERE observation = %s AND topicID = %s'
                    cur.execute(sql, (obsv, last_tpc_id))
                    last_turn_id = cur.fetchone()[0]
                    # select current turn id and who
                    sql = 'SELECT turnID, who FROM utterances WHERE observation = %s AND topicID = %s LIMIT 1'
                    cur.execute(sql, (obsv, tpc_id))
                    turn_id, who = cur.fetchone()
                    # check whether the boundary is within-turn or between-turn
                    if turn_id == last_turn_id:
                        sql = 'UPDATE utterances SET topicRole = %s WHERE observation = %s AND topicID = %s AND who = %s'
                        cur.execute(sql, ('initiator', obsv, tpc_id, who))
                        sql = 'UPDATE utterances SET topicRole = %s WHERE observation = %s AND topicID = %s AND who != %s'
                        cur.execute(sql, ('responder', obsv, tpc_id, who))
                    else:
                        # select the first `who` whose tokenNum is above 5
                        sql = 'SELECT who FROM utterances WHERE observation = %s AND topicID = %s AND tokenNum > %s LIMIT 1'
                        cur.execute(sql, (obsv, tpc_id, 5))
                        initiator = cur.fetchone()[0]
                        sql = 'UPDATE utterances SET topicRole = %s WHERE observation = %s AND topicID = %s AND who = %s'
                        cur.execute(sql, ('initiator', obsv, tpc_id, initiator))
                        sql = 'UPDATE utterances SET topicRole = %s WHERE observation = %s AND topicID = %s AND who != %s'
                        cur.execute(sql, ('responder', obsv, tpc_id, initiator))
                except Exception as e:
                    print('observation: {}, topicID: {}'.format(obsv, topic_id))
                    raise e
            conn.commit()
        # print process
        sys.stdout.write('\r{}/{}'.format(j+1, len(unique_observs)))
        sys.stdout.flush()

# add tokenNum
def add_tokenNum():
    conn = db_conn('map')
    cur = conn.cursor()
    sql = 'SELECT observation, utterID, tokens FROM utterances'
    cur.execute(sql)
    key1, key2, tokens_str = zip(*cur.fetchall())
    for i, ts in enumerate(tokens_str):
        tn = len(ts.split())
        sql = 'UPDATE utterances SET tokenNum = %s WHERE observation = %s AND utterID = %s'
        cur.execute(sql, (tn, key1[i], key2[i]))
    conn.commit()


# main
if __name__ == '__main__':
    # nlp = English(parser = False)
    # parse()
    # tokenize(nlp)
    # add_turnid()
    # add_tokenNum()
    add_topicRole()
