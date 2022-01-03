import os
import argparse
import time
import pickle
import io
import json

import grpc
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
import numpy as np

import federated_pb2
import federated_pb2_grpc

FLAGS = _ = None
DEBUG = False
STIME = time.time()


def main():
    model = tf.keras.models.load_model(FLAGS.model)
    weights_bytes = io.BytesIO()
    pickle.dump(model.get_weights(), weights_bytes)
    weights_bytes.seek(0)
    parameter = weights_bytes.getvalue()

    with grpc.insecure_channel(f'{FLAGS.address}:{FLAGS.port}') as channel:
        stub = federated_pb2_grpc.ManagerStub(channel)
        request = federated_pb2.TrainResult(name=FLAGS.name,
                                            version=FLAGS.version,
                                            parameter=parameter)
        response = stub.PushTrainResult(request)
        print(f'{response.value}')


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
                        help='The base name variable')
    parser.add_argument('--version', type=str, required=True,
                        help='The base version variable')
    parser.add_argument('--model', type=str, required=True,
                        help='The trained model')

    FLAGS, _ = parser.parse_known_args()
    FLAGS.model = os.path.abspath(os.path.expanduser(FLAGS.model))
    DEBUG = FLAGS.debug

    main()

