import argparse
import os
import pickle

import tensorflow as tf


def get_model_iterator(model, start, end):
    for micro in range(start, end):
        path = f'./models/{model}/v0.0.{micro}'
        yield path


def do_evaluate(model_name, test_root, start, end):
    loss = []
    acc = []
    classes = []
    for path in get_model_iterator(model_name, start, end):
        with open(os.path.join(path, 'labels.pickle'), 'rb') as f:
            classes = pickle.load(f)
        break
    image_generator = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1/255)
    test_data = image_generator.flow_from_directory(test_root, classes=classes,
                                                    target_size=(32, 32), shuffle=True)
    for path in get_model_iterator(model_name, start, end):
        model = tf.keras.models.load_model(os.path.abspath(os.path.expanduser(path)))
        metric = model.evaluate(test_data, verbose=0)
        loss.append(metric[0])
        acc.append(metric[1])
        if DEBUG:
            print(f'{path} {metric}')
    return loss, acc


def main():
    result = do_evaluate(FLAGS.model, FLAGS.data, FLAGS.start, FLAGS.end)
    with open(FLAGS.output, 'wb') as f:
        pickle.dump(result, f)
    print(result)


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--model', type=str, required=True,
                        help='The model for testing')
    parser.add_argument('--data', type=str, required=True,
                        help='The dataset for testing')
    parser.add_argument('--start', type=int, required=True)
    parser.add_argument('--end', type=int, required=True)
    parser.add_argument('--output', type=str, required=True,
                        help='The output path for pickle')

    FLAGS, _ = parser.parse_known_args()
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))
    DEBUG = FLAGS.debug

    main()
