import os
import pickle

import tensorflow as tf
import tensorflow_federated as tff


def save_ckpt(state: tff.learning.framework.ServerState, 
              metrics: list, 
              model_fn: Callable,
              path: str):
    keras_model = model_fn()
    keras_model.compile(loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
                        metrics=[tf.keras.metrics.CategoricalAccuracy()])
    tff.learning.assign_weights_to_keras_model(keras_model, state.model)
    keras_model.save(path)
    
    with open(os.path.join(path, 'metrics.pickle'), 'wb') as f:
        pickle.dump(metrics, f)

        
def load_ckpt(state, path='./ckpt'):
    keras_model = tf.keras.models.load_model(path)
    state = tff.learning.state_with_new_model_weights(
              state,
              trainable_weights=[v.numpy() for v in keras_model.trainable_weights],
              non_trainable_weights=[v.numpy() for v in keras_model.non_trainable_weights])

    with open(os.path.join(path, 'metrics.pickle'), 'rb') as f:
        metrics = pickle.load(f)
    
    return state, metrics
