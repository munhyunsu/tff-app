import os
import pickle

import tensorflow as tf
import tensorflow_federated as tff
import pandas as pd
import numpy as np


def load_dataset(path_root):
    dpath = os.path.join(path_root, 'sampled_dataset.pickle')
    dataset = pd.read_pickle(dpath)

    ipath = os.path.join(path_root, 'get_index.pickle')
    with open(ipath, 'rb') as f:
        idx2lab, idx2cnt = pickle.load(f)
    
    return dataset, idx2lab, idx2cnt


def preprocess(img_shape):
    def func(x):
        return np.array(x).reshape(img_shape)/255
    return func


def create_fl_dataset(dataset, idx2lab, nclients, val_size, printable=False):
    nlab = len(idx2lab.keys())
    nrow = len(dataset)

    flt = dict()
    flt_val = pd.Index([])
    for idx in np.array(list(idx2lab.keys())):
        nrow = len(dataset[dataset['y'] == idx])
        idx_val = [int(nrow*(1-val_size)), nrow-1]
    
        idx_trains = list()
        nrow = idx_val[0]
        tick = nrow//nclients
        for j in range(0, nclients):
            idx_trains.append(dataset[dataset['y'] == idx].index[tick*j:tick*(j+1)])
        idx_val[0] = tick*nclients
        flt[idx] = idx_trains
        flt_val = flt_val.union(dataset[dataset['y'] == idx].index[idx_val[0]:idx_val[1]])

    train_datasets = list()
    for _ in range(0, nclients):
        train_idx = pd.Index([])
        for j in idx2lab.keys():
            train_idx = train_idx.union(flt[j].pop())
        train_dataset = tf.data.Dataset.from_tensor_slices((dataset['x'][train_idx].values.tolist(),
                                                            dataset['y'][train_idx].values.tolist()))
        train_datasets.append(train_dataset)
        if printable:
            print(f'split train dataset {len(train_idx)}')
    test_dataset = tf.data.Dataset.from_tensor_slices((dataset['x'][flt_val].values.tolist(), 
                                                       dataset['y'][flt_val].values.tolist()))
    if printable:
        print(f'split test dataset {len(flt_val)}')

    return train_datasets, test_dataset


def create_model(nclass, img_shape):
    img_input = tf.keras.Input(shape=img_shape)
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

    pred = tf.keras.layers.Dense(nclass)(x)

    model = tf.keras.Model(inputs=[img_input],
                           outputs=[pred])
    return model


def save_ckpt(path, state, metrics, func, *args):
    keras_model = func(*args)
    keras_model.compile(loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                        metrics=[tf.keras.metrics.CategoricalAccuracy()])
    tff.learning.assign_weights_to_keras_model(keras_model, state.model)
    keras_model.save(path)

    with open(os.path.join(path, 'metrics.pickle'), 'wb') as f:
        pickle.dump(metrics, f)


def load_ckpt(path, state):
    keras_model = tf.keras.models.load_model(path)
    state = tff.learning.state_with_new_model_weights(
              state,
              trainable_weights=[v.numpy() for v in keras_model.trainable_weights],
              non_trainable_weights=[v.numpy() for v in keras_model.non_trainable_weights])

    with open(os.path.join(path, 'metrics.pickle'), 'rb') as f:
        metrics = pickle.load(f)

    return state, metrics


def early_stop(loss, min_delta=0.001, patience=3):
    if len(loss) < patience:
        return False
    ptr = loss[-patience]
    delta = 0
    for value in loss[-patience:]:
        delta = delta + max(0, ptr-value)
        ptr = value
    delta = delta / (patience-1)
    if delta < min_delta:
        return True
    return False