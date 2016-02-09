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
def tokenize():
    pass

# postag
def postag():
    nlp = English(parser = False)
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



# main
if __name__ == '__main__':
    parse()
