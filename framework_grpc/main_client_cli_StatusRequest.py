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
        request = federated_pb2.StatusRequest(name=FLAGS.name,
                                              version=FLAGS.version)
        response = stub.GetStatus(request)
        print(f'{response.name} {response.version} has {response.knowledge}')


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
    parser.add_argument('--name', type=str, required=True,
                        help='The name variable')
    parser.add_argument('--version', type=str, required=True,
                        help='The version variable')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()

