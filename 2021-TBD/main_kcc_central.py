import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf

# prepare dataset
dataset_root = os.path.abspath(os.path.expanduser('/home/harny/Github/tff-app/framework_grpc/'))

image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1/255)
train_data = image_generator.flow_from_directory(os.path.join(dataset_root, 'kcc_train'),
                                                 target_size=(32, 32), shuffle=True)
test_data = image_generator.flow_from_directory(os.path.join(dataset_root, 'kcc_test'),
                                                target_size=(32, 32), shuffle=True)

model = tf.keras.models.Sequential([
                       tf.keras.layers.Conv2D(32, (1, 3), activation='relu', input_shape=(32, 32, 3)),
                       tf.keras.layers.MaxPooling2D((2, 2)),
                       tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                       tf.keras.layers.MaxPooling2D((2, 2)),
                       tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                       tf.keras.layers.Flatten(),
                       tf.keras.layers.Dense(64, activation='relu'),
                       tf.keras.layers.Dense(len(classes))])
model.compile(optimizer=tf.keras.optimizers.Adam(),
              loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

epochs = 100
history = model.fit(train_data,
                    epochs=epochs,
                    validation_data=test_data,
                    verbose=2)

model.save('kcc/central')
