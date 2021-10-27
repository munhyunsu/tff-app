import os
import argparse
import time
import concurrent
import io
import pickle
import json

import grpc
import numpy as np
import mariadb

import secret
import federated_pb2
import federated_pb2_grpc

FLAGS = _ = None
DEBUG = False
STIME = time.time()


class Server(federated_pb2_grpc.Manager):
    def __init__(self):
        try:
            self.conn = mariadb.connect(
                        user=secret.dbuser,
                        password=secret.dbpassword,
                        host=secret.dbhost,
                        port=secret.dbport,
                        database=secret.dbname)
        except mariadb.Error as e:
            print(f'[{int(time.time()-STIME)}] Error connecting to MariaDB: {e}')
            sys.exit(1)
        self.cur = self.conn.cursor()
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] Connected to MariaDB')

    def GetInformation(self, request, context):
        req_name = request.name
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] GetInformation with {req_name}')
        
        names = []
        if len(req_name) == 0:
            self.cur.execute('''SELECT DISTINCT name FROM names;''')
            for row in self.cur.fetchall():
                names.append(row[0])
        else:
            names.append(req_name)

        models = []
        for name in names:
            self.cur.execute('''SELECT names.name, models.major, models.minor, models.micro FROM models
                                  INNER JOIN names ON models.name = names.id
                                  WHERE names.name = ?
                                  ORDER BY models.major DESC, models.minor DESC, models.micro DESC
                                  LIMIT 1;''', (name,))
            res = self.cur.fetchall()
            if len(res) != 0:
                major = res[0][1]
                minor = res[0][2]
                micro = res[0][3]
                version = f'v{major}.{minor}.{micro}'
                model = federated_pb2.InformationReply.Model(name=name,
                                                             version=version)
                models.append(model)

        return federated_pb2.InformationReply(models=models)


    def GetModel(self, request, context):
        req_name = request.name
        req_version = request.version
        req_architecture = request.architecture
        req_parameter = request.parameter
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] GetModel with {req_name} {req_version} {req_architecture} {req_parameter}')

        major, minor, micro = map(int, req_version[1:].split('.'))
        
        architecture = ''
        if req_architecture:
            self.cur.execute('''SELECT architectures.architecture FROM architectures
                                  INNER JOIN models ON architectures.id = models.architecture
                                  INNER JOIN names ON models.name = names.id
                                  WHERE names.name = ?
                                    AND models.major = ?
                                    AND models.minor = ?
                                    AND models.micro = ?;''', (req_name, major, minor, micro))
            res = self.cur.fetchall()
            if len(res) != 0:
                architecture = res[0][0]

        parameter = b''
        if req_parameter:
            self.cur.execute('''SELECT parameters.parameter FROM parameters
                                  INNER JOIN models ON parameters.id = models.parameter
                                  INNER JOIN names ON models.name = names.id
                                  WHERE names.name = ?
                                    AND models.major = ?
                                    AND models.minor = ?
                                    AND models.micro = ?;''', (req_name, major, minor, micro))
            res = self.cur.fetchall()
            if len(res) != 0:
                parameter = res[0][0]

        return federated_pb2.ModelReply(name=req_name, version=req_version,
                                        architecture=architecture, parameter=parameter)


def main():
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    federated_pb2_grpc.add_ManagerServicer_to_server(Server(), server)
    server.add_insecure_port(f'{FLAGS.address}:{FLAGS.port}')
    server.start()
    if DEBUG:
        print(f'[{int(time.time()-STIME)}] Start server')
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.wait_for_termination(1)
    if DEBUG:
        print(f'[{int(time.time()-STIME)}] End server')


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--address', type=str, default='[::]',
                        help='The bind address')
    parser.add_argument('--port', type=int, default=50000,
                        help='The bind port number')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()

