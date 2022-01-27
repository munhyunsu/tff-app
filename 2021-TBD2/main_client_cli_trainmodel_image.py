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
    model = tf.keras.models.load_model(FLAGS.model)

    if FLAGS.freeze:
        for i in range(0, len(model.layers)-1):
            model.layers[i].trainable = False

    classes = []
    with open(os.path.join(FLAGS.model, 'labels.pickle'), 'rb') as f:
        classes = pickle.load(f)

    # prepare dataset
    image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1/255)
    train_data = image_generator.flow_from_directory(FLAGS.data,  classes=classes, 
                                                     target_size=(32, 32), shuffle=True)

    model.fit(train_data, batch_size=FLAGS.batch_size, 
              steps_per_epoch=FLAGS.steps_per_epoch,
              verbose=2)

    model.save(FLAGS.output)



if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--model', type=str, required=True,
                        help='The model for training')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='The batch size')
    parser.add_argument('--steps_per_epoch', type=int, default=None,
                        help='The steps per epoch')
    parser.add_argument('--data', type=str, required=True,
                        help='The dataset for training')
    parser.add_argument('--freeze', action='store_true',
                        help='Freeze feature layer')
    parser.add_argument('--output', type=str, required=True,
                        help='The output path')

    FLAGS, _ = parser.parse_known_args()
    FLAGS.model = os.path.abspath(os.path.expanduser(FLAGS.model))
    FLAGS.data = os.path.abspath(os.path.expanduser(FLAGS.data))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))
    DEBUG = FLAGS.debug

    main()

