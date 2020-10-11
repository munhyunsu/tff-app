import os
import time

import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_federated as tff

import learning_util

FLAGS = _ = None
STIME = time.time()


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')
    
    dataset, idx2lab, lab2cnt = learning_util.load_dataset(FLAGS.input)
    if DEBUG:
        print(dataset)

        
    img_shape = (FLAGS.img_height, FLAGS.img_width, 1) # gray scale
    
    dataset['x'] = dataset['vector'].apply(learning_util.preprocess(img_shape))
    dataset['y'] = dataset['idx']
    
    dataset = dataset.sample(frac=1, random_state=FLAGS.random_state).reset_index(drop=True)

    if DEBUG:
        print(dataset)
    
    
    raw_train_datasets, raw_test_dataset = learning_util.create_fl_dataset(
        dataset, idx2lab, FLAGS.nclients, FLAGS.val_size, printable=DEBUG)

    def client_fn(client_id):
        return raw_train_datasets[client_id].repeat(FLAGS.num_epochs).shuffle(FLAGS.shuffle_buffer).batch(FLAGS.batch_size)

    client_data = tff.simulation.ClientData.from_clients_and_fn(
        client_ids=range(0, len(raw_train_datasets)),
        create_tf_dataset_for_client_fn=client_fn)
    client_data = [client_data.create_tf_dataset_for_client(x) for x in range(0, len(raw_train_datasets))]

    test_dataset = raw_test_dataset.shuffle(FLAGS.shuffle_buffer).batch(FLAGS.batch_size)
    
    sample_batch = tf.nest.map_structure(lambda x: x.numpy(), next(iter(test_dataset)))

    def model_fn():
        keras_model = learning_util.create_model(len(idx2lab), img_shape)
        return tff.learning.from_keras_model(
            keras_model,
            input_spec=test_dataset.element_spec,
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=[tf.keras.metrics.SparseCategoricalAccuracy()])


    iterative_process = tff.learning.build_federated_averaging_process(
            model_fn,
            client_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=0.02),
            server_optimizer_fn=lambda: tf.keras.optimizers.SGD(learning_rate=1.0))

    state = iterative_process.initialize()
    evaluation = tff.learning.build_federated_evaluation(model_fn)


    metrics = {
        'rounds': 0,
        'loss': list(),
        'accuracy': list(),
        'val_loss': list(),
        'val_accuracy': list(),
    }
    path_output = os.path.join(FLAGS.output, f'c{FLAGS.nclients}_e{FLAGS.num_epochs}_r{FLAGS.max_rounds}')
    if FLAGS.ckpt_load is not None:
        state, metrics = learning_util.load_ckpt(FLAGS.ckpt_load, state)
        if DEBUG:
            print(f'Load completed: rounds {metrics["rounds"]}')


    for rounds in range(metrics['rounds']+1, FLAGS.max_rounds+1):
        state, output = iterative_process.next(state, client_data)
        val_output = evaluation(state.model, [test_dataset])
        metrics['rounds'] = rounds
        metrics['loss'].append(output['train']['loss'])
        metrics['accuracy'].append(output['train']['sparse_categorical_accuracy'])
        metrics['val_loss'].append(val_output['loss'])
        metrics['val_accuracy'].append(val_output['sparse_categorical_accuracy'])
        if DEBUG:
            print((f'[{int(time.time()-STIME)}] rounds: {rounds}, '
                   f'output: {output["train"]}, '
                   f'val_output: {val_output}'))
        if rounds%FLAGS.ckpt_term == 0:
            learning_util.save_ckpt(path_output, state, metrics, learning_util.create_model, len(idx2lab), img_shape)
        if FLAGS.early_stop and learning_util.early_stop(metrics['val_loss'], min_delta=0.0001, patience=5):
            break
    learning_util.save_ckpt(path_output, state, metrics, learning_util.create_model, len(idx2lab), img_shape)


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse

    parser = argparse.ArgumentParser()
    
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--img_width', type=int, default=4,
                        help='The width of dataset image')
    parser.add_argument('--img_height', type=int, default=375,
                        help='The height of dataset image')
    parser.add_argument('--input', type=str, required=True,
                        help='The input preprocessed directory')
    parser.add_argument('--nclients', type=int, default=10,
                        help='The number of clients')
    parser.add_argument('--cclients', type=int,
                        help='The number of clients for this learning')
    parser.add_argument('--val_size', type=float, default=0.1,
                        help='The fraction of validation set')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='The size of batch')
    parser.add_argument('--shuffle_buffer', type=int, default=1024,
                        help='The size of shuffle buffer')
    parser.add_argument('--num_epochs', type=int, default=1,
                        help='The number of epochs')
    parser.add_argument('--max_rounds', type=int, default=10,
                        help='The number of rounds')
    parser.add_argument('--random_state', type=int,
                        help='The random state for dataframe sample')
    parser.add_argument('--early_stop', action='store_true',
                        help='The on / off early stop')
    parser.add_argument('--output', type=str, default=os.path.splitext(__file__)[0],
                        help='The output directory')
    parser.add_argument('--ckpt_load', type=str,
                        help='The path of checkpoint load')
    parser.add_argument('--ckpt_term', type=int, default=10,
                        help='The checkpoint save term')

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))
    if FLAGS.ckpt_load is not None:
        FLAGS.ckpt_load = os.path.abspath(os.path.expanduser(FLAGS.ckpt_load))

    DEBUG = FLAGS.debug

    main()
