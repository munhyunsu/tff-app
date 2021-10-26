import os
import sys
import argparse
import time
import io
import pickle
import json

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
        print(f'Error connecting to MariaDB: {e}')
        sys.exit(1)
    cur = conn.cursor()

    if FLAGS.reset:
        cur.execute('''DROP TABLE IF EXISTS knowledges;''')
        cur.execute('''DROP TABLE IF EXISTS models;''')
        cur.execute('''DROP TABLE IF EXISTS parameters;''')
        cur.execute('''DROP TABLE IF EXISTS architectures;''')

    cur.execute('''CREATE TABLE IF NOT EXISTS architectures (
                     id INT AUTO_INCREMENT,
                     architecture TEXT NOT NULL,
                     PRIMARY KEY (id)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS parameters (
                     id INT AUTO_INCREMENT,
                     parameter LONGBLOB NOT NULL,
                     PRIMARY KEY (id)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS models (
                     id INT AUTO_INCREMENT,
                     model TINYTEXT NOT NULL,
                     architecture INT NOT NULL,
                     parameter INT NOT NULL,
                     major INT NOT NULL,
                     minor INT NOT NULL,
                     micro INT NOT NULL,
                     PRIMARY KEY (id),
                     UNIQUE (architecture, parameter, major, minor, micro),
                     FOREIGN KEY (architecture) REFERENCES architectures (id),
                     FOREIGN KEY (parameter) REFERENCES parameters (id)
                   );''')
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
    print(res)


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--reset', action='store_true',
                        help='Clear exists tables before creation')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()

