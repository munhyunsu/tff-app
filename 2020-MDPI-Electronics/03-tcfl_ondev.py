import os
from operator import itemgetter
import collections
import pickle
import statistics
import time

import matplotlib.pylab as plt
import numpy as np
import pandas as pd

import tensorflow as tf
tf.random.set_seed(99)
import tensorflow_federated as tff
# https://www.tensorflow.org/api_docs/python/tf/compat/v1/enable_v2_behavior
tf.compat.v1.enable_v2_behavior()

FLAGS = None
_ = None


def main():
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')

    # environment variables
    img_shape = (375, 4)
    batch_size = 32
    classes = ['aim', 'email', 'facebook', 'ftps', 'gmail', 
               'hangout', 'icqchat', 'netflix', 'scp', 'sftp',
               'skype', 'spotify', 'torrent', 'vimeo', 'voipbuster',
               'youtube']

    # prepare input data generator
    img_gen_op = {'classes': classes, 
                  'target_size': img_shape, 
                  'batch_size': batch_size,
                  'color_mode': 'grayscale'}
    image_generator = tf.keras.preprocessing.image.ImageDataGenerator(
                        rescale=1/255)
    def gen_fn(args):
        data_path = args.decode('utf-8')
        return image_generator.flow_from_directory(data_path,
                                                   **img_gen_op)

    # check datasize
    ## it used for improvements of federated learning experiments
    dataset_size = dict()
    queue = [FLAGS.input]
    while queue:
        path = queue.pop(0)
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    queue.append(entry.path)
                if entry.is_file():
                    name = os.path.basename(
                             os.path.dirname(
                             os.path.dirname(entry.path)))
                    dataset_size[name] = dataset_size.get(name, 0) + 1

    # dataset dict for client data generator
    dataset_dict = dict()
    with os.scandir(FLAGS.input) as it:
        for entry in it:
            if entry.is_dir():
                name = os.path.basename(entry.path)
                ds = tf.data.Dataset.from_generator(gen_fn,
                       args=[entry.path],
                       output_types=(tf.float32, tf.float32),
                       output_shapes=(
                         tf.TensorShape((None, ) + img_shape + (1, )),
                         tf.TensorShape([None, len(classes)]))
                       )
                dataset_dict[name] = ds
    
    # client dataset
    def client_fn(client_id):
        return dataset_dict[client_id]
    client_data = tff.simulation.ClientData.from_clients_and_fn(
                    client_ids=list(dataset_dict.keys()),
                    create_tf_dataset_for_client_fn=client_fn)
    
    # train and validation set
    train_ids = list(dataset_dict.keys())
    train_ids.remove('0')
    dataset = [(client_data.create_tf_dataset_for_client(x), 
                dataset_size[x]) for x in train_ids]

    # batch sample
    example_dataset = (client_data.create_tf_dataset_for_client(
                         client_data.client_ids[0]),
                       dataset_size[client_data.client_ids[0]])

    # federated dataset
    take_value = None

    def preprocess(dataset, take_value=None):
        if take_value is None:
            take_value = dataset[1]
        return dataset[0].take(np.ceil(take_value/batch_size))

    preprocessed_example_dataset = preprocess(example_dataset, take_value)
    sample_batch = tf.nest.map_structure(
                     lambda x: x.numpy(), 
                     next(iter(preprocessed_example_dataset)))
    federated_dataset = [preprocess(x, take_value) for x in dataset]
    
    # validation dataset
    test_dataset = (client_data.create_tf_dataset_for_client('0'), 
                    dataset_size['0'])
    federated_test_data = [preprocess(test_dataset, None)]

    def create_keras_model():
        # Create Deep and Wide CNN
        img_input = tf.keras.Input(shape=img_shape + (1, ))
        features1 = tf.keras.layers.Conv2D(32, (1, 1), activation='relu')(img_input)
        features1 = tf.keras.layers.Flatten()(features1)

        features2 = tf.keras.layers.Conv2D(32, (1, 2), activation='relu')(img_input)
        features2 = tf.keras.layers.Flatten()(features2)

        features3 = tf.keras.layers.Conv2D(32, (1, 4), activation='relu')(img_input)
        features3 = tf.keras.layers.Flatten()(features3)

        features4 = tf.keras.layers.Conv2D(32, (2, 2), activation='relu')(img_input)
        features4 = tf.keras.layers.MaxPooling2D((2, 2), strides=(1, 1))(features4)
        features5 = tf.keras.layers.Conv2D(32, (2, 2), activation='relu')(features4)

        features4 = tf.keras.layers.Flatten()(features4)
        features5 = tf.keras.layers.Flatten()(features5)

        x = tf.keras.layers.concatenate([features1, features2, features3, features4, features5])

        pred = tf.keras.layers.Dense(len(classes))(x)

        model = tf.keras.Model(inputs=[img_input],
                               outputs=[pred])

        return model


    def save_ckpt(state, metrics):
        keras_model = create_keras_model()
        keras_model.compile(loss=tf.keras.losses.CategoricalCrossentropy(
                                   from_logits=True),
                            metrics=[tf.keras.metrics.CategoricalAccuracy()])
        tff.learning.assign_weights_to_keras_model(keras_model, state.model)
        keras_model.save(FLAGS.output)
    
        with open(os.path.join(FLAGS.output, 'metrics.pickle'), 'wb') as f:
            pickle.dump(metrics, f)
    
    
    def load_ckpt(state):
        keras_model = tf.keras.models.load_model(FLAGS.output)
        state = tff.learning.state_with_new_model_weights(
                  state,
                  trainable_weights=
                    [v.numpy() for v in keras_model.trainable_weights],
                  non_trainable_weights=
                    [v.numpy() for v in keras_model.non_trainable_weights])
    
        with open(os.path.join(FLAGS.output, 'metrics.pickle'), 'rb') as f:
            metrics = pickle.load(f)

        return state, metrics


    def model_fn():
        keras_model = create_keras_model()
        return tff.learning.from_keras_model(keras_model, 
                 dummy_batch=sample_batch,
                 loss=tf.keras.losses.CategoricalCrossentropy(
                        from_logits=True),
                 metrics=[tf.keras.metrics.CategoricalAccuracy()])

    iterative_process = tff.learning.build_federated_averaging_process(
                          model_fn,
                          client_optimizer_fn=lambda: tf.keras.optimizers.SGD(
                                                        learning_rate=0.02),
                          server_optimizer_fn=lambda: tf.keras.optimizers.SGD(
                                                        learning_rate=1.0))
    evaluation = tff.learning.build_federated_evaluation(model_fn)
    
    state = iterative_process.initialize()
    start_round = 0
    loss = list()
    accuracy = list()
    val_loss = list()
    val_accuracy = list()
    if os.path.exists(FLAGS.output):
        state, metrics = load_ckpt(state)
        start_round = metrics[0]
        loss = metrics[1]
        accuracy = metrics[2]
        val_loss = metrics[3]
        val_accuracy = metrics[4]

    for round_num in range(start_round+1, FLAGS.round+1):
        stime = time.time()
        state, metrics = iterative_process.next(state, federated_dataset)
        save_ckpt(state, [round_num, loss, accuracy, val_loss, val_accuracy])
        val_metrics = evaluation(state.model, federated_test_data)
        loss.append(metrics.loss)
        accuracy.append(metrics.categorical_accuracy)
        val_loss.append(val_metrics.loss)
        val_accuracy.append(val_metrics.categorical_accuracy)
        dtime = time.time() - stime
        print((f'{dtime} round: {round_num:2d}, loss: {metrics.loss}, '
               f'test_accuracy: {val_metrics.categorical_accuracy}'))


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True,
                        help='Dataset directory which has clients data')
    parser.add_argument('--output', type=str, required=True,
                        help='Keras model output path (per rounds)')
    parser.add_argument('--round', type=int,
                        default=1000,
                        help='The number of rounds')

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()
