import os
import argparse
import time
import concurrent
import io
import pickle
import json

import grpc
import numpy as np

import federated_pb2
import federated_pb2_grpc

FLAGS = _ = None
DEBUG = False
STIME = time.time()

class Server(federated_pb2_grpc.Manager):
    def __init__(self):
        if DEBUG:
            print(f'Load models by {FLAGS.model}')

    def GetModel(self, request, context):
        reply = federated_pb2.ModelReply()
        print(f'Information: {request.information}')
        if request.information == request.Information.VERSION:
            reply.version = '1.3.2'
        elif request.information == request.Information.PARAMETER:
            reply.parameter = np.asarray([1, 2, [3, 4, 5]], dtype=object).tobytes()
            print('PARAMETER')
        elif request.information == request.Information.ARCHITECTURE:
            print('ARCHITECTURE')
        return reply


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
    parser.add_argument('--model', type=str, required=True,
                        help='The model configuration file')

    FLAGS, _ = parser.parse_known_args()
    FLAGS.model = os.path.abspath(os.path.expanduser(FLAGS.model))
    DEBUG = FLAGS.debug

    main()

