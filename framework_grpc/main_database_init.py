import os
import sys
import argparse
import time

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
        cur.execute('''DROP TABLE IF EXISTS architectures;''')
        cur.execute('''DROP TABLE IF EXISTS labels;''')
        cur.execute('''DROP TABLE IF EXISTS names;''')
        cur.execute('''DROP TABLE IF EXISTS users;''')
        conn.commit()
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] DROP all tables of {secret.dbname}')

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                     id INT AUTO_INCREMENT,
                     user TEXT NOT NULL,
                     salt TEXT NOT NULL,
                     password TEXT NOT NULL,
                     PRIMARY KEY (id),
                     UNIQUE (user)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS names (
                     id INT AUTO_INCREMENT,
                     name TEXT NOT NULL,
                     PRIMARY KEY (id),
                     UNIQUE (name)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS labels (
                     id INT AUTO_INCREMENT,
                     name INT NOT NULL,
                     label LONGBLOB NOT NULL,
                     PRIMARY KEY (id),
                     FOREIGN KEY (name) REFERENCES names (id),
                     UNIQUE (label)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS architectures (
                     id INT AUTO_INCREMENT,
                     name INT NOT NULL,
                     architecture TEXT NOT NULL,
                     PRIMARY KEY (id),
                     FOREIGN KEY (name) REFERENCES names (id),
                     UNIQUE (architecture)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS parameters (
                     id INT AUTO_INCREMENT,
                     name INT NOT NULL,
                     parameter LONGBLOB NOT NULL,
                     PRIMARY KEY (id),
                     FOREIGN KEY (name) REFERENCES names (id),
                     UNIQUE (parameter)
                   );''')
    cur.execute('''CREATE TABLE IF NOT EXISTS models (
                     id INT AUTO_INCREMENT,
                     name INT NOT NULL,
                     label INT NOT NULL,
                     architecture INT NOT NULL,
                     parameter INT NOT NULL,
                     major INT NOT NULL,
                     minor INT NOT NULL,
                     micro INT NOT NULL,
                     PRIMARY KEY (id),
                     UNIQUE (name, major, minor, micro),
                     FOREIGN KEY (name) REFERENCES names (id),
                     FOREIGN KEY (label) REFERENCES labels (id),
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
    if DEBUG:
        print(f'[{int(time.time()-STIME)}] CREATE TABLES: {res}')

    conn.commit()
    conn.close()


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
