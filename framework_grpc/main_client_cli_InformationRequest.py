import grpc
import os
import argparse
import time

import numpy as np

import federated_pb2
import federated_pb2_grpc

FLAGS = _ = None
DEBUG = False
STIME = time.time()


def main():
    with grpc.insecure_channel(f'{FLAGS.address}:{FLAGS.port}') as channel:
        stub = federated_pb2_grpc.ManagerStub(channel)
        request = federated_pb2.InformationRequest(name=FLAGS.name)
        response = stub.GetInformation(request)
        for model in response.models:
            print(f'{model.name} {model.version}')


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--address', type=str, default='localhost',
                        help='The bind address')
    parser.add_argument('--port', type=int, default=50000,
                        help='The bind port number')
    parser.add_argument('--name', type=str,
                        help='The name variable')

    FLAGS, _ = parser.parse_known_args()
    if FLAGS.name is None:
        FLAGS.name = ''
    DEBUG = FLAGS.debug

    main()

