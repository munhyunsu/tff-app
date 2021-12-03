import os
import io
import pickle

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

import model


class FLModel(model.Model):
    def __init__(self, **kwargs):
        self.name = 'CNN-CIFAR10'
        self.label = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']
        self.model = tf.keras.models.Sequential([
                       tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
                       tf.keras.layers.MaxPooling2D((2, 2)),
                       tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                       tf.keras.layers.MaxPooling2D((2, 2)),
                       tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                       tf.keras.layers.Flatten(),
                       tf.keras.layers.Dense(64, activation='relu'),
                       tf.keras.layers.Dense(len(self.label))])
        self.compile_ = {'optimizer': 'tf.keras.optimizers.Adam()',
                         'loss': 'tf.keras.losses.CategoricalCrossentropy(from_logits=True)',
                         'metrics': "['accuracy']"}

    def get_name(self):
        return self.name

    def get_compile(self):
        compile_bytes = io.BytesIO()
        pickle.dump(self.compile_, compile_bytes)
        compile_bytes.seek(0)
        return compile_bytes.getvalue()

    def get_label(self):
        labels_bytes = io.BytesIO()
        pickle.dump(self.label, labels_bytes)
        labels_bytes.seek(0)
        return labels_bytes.getvalue()

    def get_architecture(self):
        return self.model.to_json()

    def get_parameter(self):
        weights_bytes = io.BytesIO()
        pickle.dump(self.model.get_weights(), weights_bytes)
        weights_bytes.seek(0)
        return weights_bytes.getvalue()

