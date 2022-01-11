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
        self.get_connector()
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] Connected to MariaDB')

    def get_connector(self):
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

    def close_connector(self):
        self.conn.close()

    def GetInformation(self, request, context):
        self.get_connector()
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

        self.conn.close()
        return federated_pb2.InformationReply(models=models)


    def GetModel(self, request, context):
        self.get_connector()
        req_name = request.name
        req_version = request.version
        req_label = request.label
        req_compile = request.compile
        req_architecture = request.architecture
        req_parameter = request.parameter
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] GetModel with {req_name} {req_version} {req_label} {req_compile} {req_architecture} {req_parameter}')

        major, minor, micro = map(int, req_version[1:].split('.'))
        
        label = b''
        if req_label:
            self.cur.execute('''SELECT labels.label FROM labels
                                  INNER JOIN models ON labels.id = models.label
                                  INNER JOIN names ON models.name = names.id
                                  WHERE names.name = ?
                                    AND models.major = ?
                                    AND models.minor = ?
                                    AND models.micro = ?;''', (req_name, major, minor, micro))
            res = self.cur.fetchall()
            if len(res) != 0:
                label = res[0][0]

        compile_ = b''
        if req_compile:
            self.cur.execute('''SELECT compiles.compile FROM compiles
                                  INNER JOIN models ON compiles.id = models.compile
                                  INNER JOIN names ON models.name = names.id
                                  WHERE names.name = ?
                                    AND models.major = ?
                                    AND models.minor = ?
                                    AND models.micro = ?;''', (req_name, major, minor, micro))
            res = self.cur.fetchall()
            if len(res) != 0:
                compile_ = res[0][0]

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

        self.conn.close()
        return federated_pb2.ModelReply(name=req_name, version=req_version,
                                        label=label, compile=compile_, architecture=architecture, parameter=parameter)

    def PushTrainResult(self, request, context):
        self.get_connector()
        req_name = request.name
        req_version = request.version
        req_parameter = request.parameter
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] PushTrainResult with {req_name} {req_version} {len(req_parameter)}')

        major, minor, micro = map(int, req_version[1:].split('.'))
        self.cur.execute('''SELECT models.id FROM models
                              INNER JOIN names ON models.name = names.id
                              WHERE names.name = ?
                                AND models.major = ?
                                AND models.minor = ?
                                AND models.micro = ?;''', (req_name, major, minor, micro))
        res = self.cur.fetchall()
        if len(res) != 0:
            base_id = res[0][0]
        else:
            return federated_pb2.Note(value='Not found')

        self.cur.execute('''INSERT IGNORE INTO knowledges (
                              base, parameter)
                              VALUES (
                              ?, ?)
                              RETURNING (id);''', (base_id, req_parameter))
        res = self.cur.fetchall()
        if len(res) != 0:
            knowledge_id = res[0][0]
            self.conn.commit()
            self.conn.close()
            return federated_pb2.Note(value=f'Knowledge {knowledge_id}')
        else:
            self.conn.close()
            return federated_pb2.Note(value='Some error')

    def GetStatus(self, request, context):
        self.get_connector()
        req_name = request.name
        req_version = request.version
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] GetStatus with {req_name} {req_version}')

        major, minor, micro = map(int, req_version[1:].split('.'))

        self.cur.execute('''SELECT models.id FROM models
                              INNER JOIN names ON models.name = names.id
                              WHERE names.name = ?
                                AND models.major = ?
                                AND models.minor = ?
                                AND models.micro = ?;''', (req_name, major, minor, micro))
        res = self.cur.fetchall()
        if len(res) != 0:
            base_id = res[0][0]
        else:
            self.conn.close()
            return federated_pb2.Note(value='Not found')

        knowledge = 0
        self.cur.execute('''SELECT COUNT(*) FROM knowledges
                              WHERE base = ?;''', (base_id,))
        res = self.cur.fetchall()
        if len(res) != 0:
            knowledge = res[0][0]

        self.conn.close()
        return federated_pb2.StatusReply(name=req_name,
                                         version=req_version,
                                         knowledge=knowledge)

    def PushControl(self, request, context):
        self.get_connector()
        req_name = request.name
        req_version = request.version
        req_job = request.job
        if DEBUG:
            print(f'[{int(time.time()-STIME)}] GetStatus with {req_name} {req_version} {req_job}')

        major, minor, micro = map(int, req_version[1:].split('.'))

        if req_job == federated_pb2.Control.Job.AGGREGATION:
            self.cur.execute('''SELECT models.id, models.name, models.label, models.compile, models.architecture FROM models
                                  INNER JOIN names ON models.name = names.id
                                  INNER JOIN labels ON models.label = labels.id
                                  WHERE names.name = ?
                                    AND models.major = ?
                                    AND models.minor = ?
                                    AND models.micro = ?;''', (req_name, major, minor, micro))
            res = self.cur.fetchall()
            if len(res) != 0:
                base_id, name_id, label_id, compile_id, architecture_id = res[0]
            else:
                self.conn.close()
                return federated_pb2.Note(value='Not found')

            knowledges = []
            self.cur.execute('''SELECT parameter FROM knowledges
                                  WHERE base = ?;''', (base_id,))
            res = self.cur.fetchall()
            if len(res) == 0:
                self.conn.close()
                return federated_pb2.Note(value='Not found knowledges')
            elif len(res) == 1:
                self.conn.close()
                return federated_pb2.Note(value='Just one result')
            else:
                for row in res:
                    knowledge = pickle.loads(row[0])
                    knowledges.append(knowledge)

            merge = knowledges[0]
            for knowledge in knowledges[1:]:
                for i in range(len(knowledge)):
                    merge[i] = merge[i] + knowledge[i]

            for i in range(len(merge)):
                merge[i] = merge[i] / len(knowledges)

            weights_bytes = io.BytesIO()
            pickle.dump(merge, weights_bytes)
            weights_bytes.seek(0)

            new_parameter = weights_bytes.getvalue()
            new_major = major
            new_minor = minor
            new_micro = micro + 1
            new_version = f'{new_major}.{new_minor}.{new_micro}'
            
            self.cur.execute('''INSERT IGNORE INTO parameters (
                                  name, parameter)
                                  VALUES (?, ?)
                                  RETURNING (id);''', (name_id, new_parameter))
            res = self.cur.fetchall()
            self.conn.commit()
            if len(res) == 0:
                self.cur.execute('''SELECT id FROM parameters
                                      WHERE name = ?
                                        AND parameter = ?;''', (name_id, new_parameter))
                res = self.cur.fetchall()
            new_parameter_id = res[0][0]
            if DEBUG:
                print(f'[{int(time.time()-STIME)}] Inserted parameter to database: {new_parameter_id}')

            self.cur.execute('''INSERT IGNORE INTO models (
                                  name, label, compile, architecture, parameter,
                                  major, minor, micro)
                                  VALUES (
                                  ?, ?, ?, ?, ?,
                                  ?, ?, ?)
                                  RETURNING (id);''', (name_id, label_id, compile_id, architecture_id, new_parameter_id,
                                                       new_major, new_minor, new_micro))
            res = self.cur.fetchall()
            self.conn.commit()
            new_model_id = res[0][0]
            if DEBUG:
                print(f'[{int(time.time()-STIME)}] Inserted model to database: {new_model_id} with {req_name} ({new_version})')

            self.conn.close()
            return federated_pb2.Note(value=f'New model ({new_model_id}) created with {req_name} ({new_version})')



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

