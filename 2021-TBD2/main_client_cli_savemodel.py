import os
import argparse
import time
import pickle
import io
import json

import grpc
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
import tensorflow as tf
import numpy as np

import federated_pb2
import federated_pb2_grpc

FLAGS = _ = None
DEBUG = False
STIME = time.time()


def main():
    with grpc.insecure_channel(f'{FLAGS.address}:{FLAGS.port}') as channel:
        stub = federated_pb2_grpc.ManagerStub(channel)
        request = federated_pb2.ModelRequest(name=FLAGS.name,
                                             version=FLAGS.version,
                                             label=True,
                                             compile=True,
                                             architecture=True,
                                             parameter=True)
        response = stub.GetModel(request)
        name = response.name
        version = response.version
        label = response.label
        compile_ = response.compile
        architecture = response.architecture
        parameter = response.parameter
        print(f'{response.name} {response.version} {len(response.architecture)} {len(response.parameter)} {len(response.compile)}')

        if len(architecture) != 0 and len(parameter) != 0:
            parameter_bytes = pickle.loads(parameter)
            compile_dict = pickle.loads(compile_)
            for key, value in compile_dict.items():
                compile_dict[key] = eval(value)

            model = tf.keras.models.model_from_json(architecture)
            model.set_weights(parameter_bytes)
            model.compile(**compile_dict)

            model.save(FLAGS.output)
            
            label_list = pickle.loads(label)
            label_path = os.path.join(FLAGS.output, 'labels.pickle')
            with open(label_path, 'wb') as f:
                pickle.dump(label_list, f)



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
    parser.add_argument('--output', type=str, required=True,
                        help='The output path')

    FLAGS, _ = parser.parse_known_args()
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))
    DEBUG = FLAGS.debug

    main()

