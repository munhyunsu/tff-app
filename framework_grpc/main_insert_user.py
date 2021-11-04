import os
import sys
import argparse
import time
import getpass
import hashlib
import random
import string

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

    print(f'[{int(time.time()-STIME)}] Authenticated user creation')
    user = input('Username: ').strip()
    password_plain = getpass.getpass().strip()
    salt = ''.join(random.choices(string.digits+string.ascii_letters, k=64))
    password_hash = hashlib.sha256((password_plain+salt).encode('utf-8')).hexdigest()

    cur.execute('''INSERT INTO users (
                     user, salt, password) VALUES (
                     ?, ?, ?) ON DUPLICATE KEY UPDATE
                     salt = ?,
                     password = ?
                     RETURNING (id);''', (user, salt, password_hash, salt, password_hash))
    res = cur.fetchall()[0][0]
    print(f'[{int(time.time()-STIME)}] Insertd user {user} ({res}) with {password_hash} ({salt})')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()

