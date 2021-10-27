import os
import sys
import argparse
import time
import importlib

import mariadb

import secret

FLAGS = _ = None
DEBUG = False
STIME = time.time()


def main():
    try:
        conn = mariadb.connect(
                user=secret.dbuser,
                password=secret.dbpassword,
                host=secret.dbhost,
                port=secret.dbport,
                database=secret.dbname)
    except mariadb.Error as e:
        print(f'[{int(time.time()-STIME)}] Error connecting to MariaDB: {e}')
        sys.exit(1)
    cur = conn.cursor()

    if DEBUG:
        print(f'[{int(time.time()-STIME)}] Read model from {FLAGS.input}')
    spec = importlib.util.spec_from_file_location('FLModel', FLAGS.input)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    model = module.FLModel()

    name = model.get_name()
    cur.execute('''SELECT id FROM names
                     WHERE name = ?
                     LIMIT 1;''', (name,))
    res = cur.fetchall()
    if len(res) != 0:
        print(f'[{int(time.time()-STIME)}] Already Inserted model to database: {res[0][0]}')
    #    return

    cur.execute('''INSERT IGNORE INTO names (name)
                     VALUES (?)
                     RETURNING (id);''', (name,))
    res = cur.fetchall()
    if len(res) == 0:
        cur.execute('''SELECT id FROM names
                         WHERE name = ?;''', (name,))
        res = cur.fetchall()
    name_id = res[0][0]
    if DEBUG:
        print(f'[{int(time.time()-STIME)}] Inserted name to database: {name_id}')

    label = model.get_label()
    cur.execute('''INSERT IGNORE INTO labels (
                     name, label)
                     VALUES (?, ?)
                     RETURNING (id);''', (name_id, label))
    res = cur.fetchall()
    if len(res) == 0:
        cur.execute('''SELECT id FROM labels
                         WHERE label = ?;''', (label,))
        res = cur.fetchall()
    label_id = res[0][0]
    if DEBUG:
        print(f'[{int(time.time()-STIME)}] Inserted label to database: {label_id}')

    architecture = model.get_architecture()
    cur.execute('''INSERT IGNORE INTO architectures (
                     name, architecture)
                     VALUES (?, ?)
                     RETURNING (id);''', (name_id, architecture))
    res = cur.fetchall()
    if len(res) == 0:
        cur.execute('''SELECT id FROM architectures
                         WHERE architecture = ?;''', (architecture,))
        res = cur.fetchall()
    architecture_id = res[0][0]
    if DEBUG:
        print(f'[{int(time.time()-STIME)}] Inserted architecture to database: {architecture_id}')

    
    cur.execute('''SELECT id FROM parameters
                     WHERE name = ?;''', (name_id,))
    res = cur.fetchall()
    if len(res) == 0:
        parameter = model.get_parameter()
        cur.execute('''INSERT IGNORE INTO parameters (
                         name, parameter)
                         VALUES (?, ?)
                         RETURNING (id);''', (name_id, parameter))
        res = cur.fetchall()
        if len(res) == 0:
            cur.execute('''SELECT id FROM parameters
                             WHERE parameter = ?;''', (parameter,))
            res = cur.fetchall()
        parameter_id = res[0][0]
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] Inserted parameter to database: {parameter_id}')
    else:
        parameter_id = res[0][0]
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] Skipped inserting parameter to database: {parameter_id}')

    cur.execute('''INSERT IGNORE INTO models (
                     name, label, architecture, parameter,
                     major, minor, micro)
                     VALUES (
                     ?, ?, ?, ?,
                     0, 0, 0)
                     RETURNING (id);''', (name_id, label_id, architecture_id, parameter_id))
    res = cur.fetchall()
    if len(res) == 0:
        cur.execute('''SELECT id FROM models
                         WHERE name = ?
                           AND major = 0
                           AND minor = 0
                           AND micro = 0;''', (name_id,))
        res = cur.fetchall()
    model_id = res[0][0]
    if DEBUG:
        print(f'[{int(time.time()-STIME)}] Inserted model to database: {model_id} with {name}')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--input', type=str, required=True,
                        help='The model class file to insert')

    FLAGS, _ = parser.parse_known_args()
    if FLAGS.input is not None:
        FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    DEBUG = FLAGS.debug

    main()

