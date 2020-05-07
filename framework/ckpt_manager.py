import os
import pickle

import tensorflow as tf
import tensorflow_federated as tff


def save_ckpt_fl(state: tff.learning.framework.ServerState, 
                 model_fn: Callable,
                 model_loss: tf.keras.losses,
                 model_metrics: list,
                 metrics: list, 
                 path: str):
    keras_model = model_fn()
    keras_model.compile(loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                        metrics=[tf.keras.metrics.CategoricalAccuracy()])
    tff.learning.assign_weights_to_keras_model(keras_model, state.model)
    save_ckpt(keras_model, metrics, path)


def load_ckpt_fl(state, path='./ckpt'):
    keras_model, metrics = load_ckpt(path)
    state = tff.learning.state_with_new_model_weights(
              state,
              trainable_weights=[v.numpy() for v in keras_model.trainable_weights],
              non_trainable_weights=[v.numpy() for v in keras_model.non_trainable_weights])

    return state, metrics


def save_ckpt(model: tf.keras.models
              metrics: dict,
              path: str):
    model.save(path)
    with open(os.path.join(path, 'metrics.pickle') 'wb') as f:
        pickle.dump(metrics, f)


def load_ckpt(path: str):
    model = tf.keras.models.load_model(path)
    with open(os.path.join(path, 'metrics.pickle'), 'rb') as f:
        metrics = pickle.load(f)

    return model, metrics
