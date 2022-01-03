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

    classes = []
    with open(os.path.join(FLAGS.model, 'labels.pickle'), 'rb') as f:
        classes = pickle.load(f)

    # prepare dataset
    image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1/255)
    test_data = image_generator.flow_from_directory(FLAGS.data,  classes=classes, 
                                                    target_size=(32, 32), shuffle=True)

    metric = model.evaluate(test_data, verbose=0)

    print(metric)


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--model', type=str, required=True,
                        help='The model for training')
    parser.add_argument('--data', type=str, required=True,
                        help='The dataset for training')

    FLAGS, _ = parser.parse_known_args()
    FLAGS.model = os.path.abspath(os.path.expanduser(FLAGS.model))
    FLAGS.data = os.path.abspath(os.path.expanduser(FLAGS.data))
    DEBUG = FLAGS.debug

    main()

