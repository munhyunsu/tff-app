import os
import sys
import argparse
import time
import io
import pickle
import json
import importlib

import numpy as np
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

    if FLAGS.reset:
        cur.execute('''DROP TABLE IF EXISTS knowledges;''')
        cur.execute('''DROP TABLE IF EXISTS models;''')
        cur.execute('''DROP TABLE IF EXISTS parameters;''')
        cur.execute('''DROP TABLE IF EXISTS labels;''')
        cur.execute('''DROP TABLE IF EXISTS architectures;''')
        conn.commit()
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] DROP all tables of {secret.dbname}')

    cur.execute('''CREATE TABLE IF NOT EXISTS architectures (
                     id INT AUTO_INCREMENT,
                     architecture TEXT NOT NULL,
                     PRIMARY KEY (id),
                     UNIQUE (architecture)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS labels (
                     id INT AUTO_INCREMENT,
                     label LONGBLOB NOT NULL,
                     PRIMARY KEY (id),
                     UNIQUE (label)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS parameters (
                     id INT AUTO_INCREMENT,
                     parameter LONGBLOB NOT NULL,
                     PRIMARY KEY (id),
                     UNIQUE (parameter)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS models (
                     id INT AUTO_INCREMENT,
                     name TINYTEXT NOT NULL,
                     architecture INT NOT NULL,
                     parameter INT NOT NULL,
                     label INT NOT NULL,
                     major INT NOT NULL,
                     minor INT NOT NULL,
                     micro INT NOT NULL,
                     PRIMARY KEY (id),
                     UNIQUE (architecture, parameter, label, major, minor, micro),
                     FOREIGN KEY (architecture) REFERENCES architectures (id),
                     FOREIGN KEY (parameter) REFERENCES parameters (id)
                   );''')
    cur.execute('''CREATE INDEX IF NOT EXISTS idx_name ON models (name);''')
    cur.execute('''CREATE TABLE IF NOT EXISTS knowledges (
                     id INT AUTO_INCREMENT,
                     base INT NOT NULL,
                     parameter LONGBLOB NOT NULL,
                     PRIMARY KEY (id),
                     FOREIGN KEY (base) REFERENCES models (id)
                   );''')
    conn.commit()

    cur.execute('''SHOW TABLES;''')
    res = cur.fetchall()
    if DEBUG:
        print(f'[{int(time.time()-STIME)}] CREATE TABLES: {res}')

    if FLAGS.input is not None:
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] Read model from {FLAGS.input}')
        spec = importlib.util.spec_from_file_location('FLModel', FLAGS.input)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        model = module.FLModel()
        
        name = model.get_name()
        cur.execute('''SELECT id FROM models
                         WHERE models.name = ?;''', (name,))
        res = cur.fetchone()
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] SELECT with {name}: {res}')

        if res is None:
            if DEBUG:
                print(f'[{int(time.time()-STIME)}] Insert model to database: {name}')
            architecture = model.get_architecture()
            cur.execute('''INSERT IGNORE INTO architectures (architecture)
                             VALUES (?)
                             RETURNING (id);''', (architecture,))
            architecture_id = cur.fetchone()[0]
            if DEBUG:
                print(f'[{int(time.time()-STIME)}] Inserted architecture to database: {architecture_id}')
            #conn.commit()

            label = model.get_label()
            cur.execute('''INSERT IGNORE INTO labels (label)
                             VALUES(?)
                             RETURNING (id);''', (label,))
            label_id = cur.fetchone()[0]
            if DEBUG:
                print(f'[{int(time.time()-STIME)}] Inserted label to database: {label_id}')
            #conn.commit()

            parameter = model.get_parameter()
            cur.execute('''INSERT IGNORE INTO parameters (parameter)
                             VALUES (?)
                             RETURNING (id);''', (parameter,))
            parameter_id = cur.fetchone()[0]
            if DEBUG:
                print(f'[{int(time.time()-STIME)}] Inserted parameter to database: {parameter_id}')
            #conn.commit()

            cur.execute('''INSERT IGNORE INTO models (
                             name, architecture, parameter, label,
                             major, minor, micro)
                             VALUES (
                             ?, ?, ?, ?,
                             0, 0, 0)
                             RETURNING (id);''', (name, architecture_id, parameter_id, label_id))
            model_id = cur.fetchone()[0]
            if DEBUG:
                print(f'[{int(time.time()-STIME)}] Inserted parameter to database: {model_id}')
            #conn.commit()
        else:
            if DEBUG:
                print(f'[{int(time.time()-STIME)}] Ignore model with {res} in database already')

    if DEBUG:
        print(f'[{int(time.time()-STIME)}] Done!')


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--reset', action='store_true',
                        help='Clear exists tables before creation')
    parser.add_argument('--input', type=str,
                        help='The model class file to insert')

    FLAGS, _ = parser.parse_known_args()
    if FLAGS.input is not None:
        FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    DEBUG = FLAGS.debug

    main()

