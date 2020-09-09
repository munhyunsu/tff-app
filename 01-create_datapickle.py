# Load library
import os
import subprocess
import shlex
import shutil

from scapy.all import *
from PIL import Image
import numpy as np

import tensorflow as tf

FLAGS = None
DEBUG = None
_ = None


def get_data(path_root):
    tfrecords = list()
    for entry in os.scandir(path_root):
        if not entry.name.startswith('.') and entry.is_file():
            tfrecords.append(entry.path)
    return tf.data.TFRecordDataset(tfrecords)


def get_index(dataset):
    idx2lab = dict()
    lab2cnt = dict()
    for raw_record in dataset:
        data = tf.train.Example.FromString(raw_record.numpy())
        idx = data.features.feature['idx'].int64_list.value[0]
        lab = data.features.feature['label'].bytes_list.value[0].decode('utf-8')
        idx2lab[idx] = lab
        lab2cnt[lab] = lab2cnt.get(lab, 0) + 1
    return idx2lab, lab2cnt


def get_weight(path_weight, idx2lab):
    weights = dict()
    # initialize
    for lab in idx2lab.values():
        weights[lab] = 1
    if path_weight is not None:
        with open(path_weight, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                weights[row['label']] = int(row['weight'])
    return weights


def get_datatick(lab2cnt, weights):
    def is_pass(tick):
        for lab in weights.keys():
            if weights[lab]*tick > lab2cnt[lab]:
                return False
        return True
    # find tick
    left = 0
    right = max(lab2cnt.values())
    datatick = 0
    while left < right:
        cur = (left+right)//2
        if is_pass(cur):
            datatick = cur
            if left == cur + 1:
                break
            left = cur + 1
        else:
            if right == cur - 1:
                break
            right = cur - 1
    return datatick


def get_sample_size(weights, datatick):
    sample_size = dict()
    for k, v in weights.items():
        sample_size[k] = datatick*v
    return sample_size


def get_dataframe(dataset, sample_size):
    global FLAGS
    global DEBUG
    df = pd.DataFrame(columns=['x', 'y'])
    cnt = dict()
    done = set()
    
    for raw_record in dataset.shuffle(FLAGS.buffersize):
        ## parse data
        data = tf.train.Example.FromString(raw_record.numpy())
        vector = data.features.feature['vector'].int64_list.value
        idx = data.features.feature['idx'].int64_list.value[0]
        lab = data.features.feature['label'].bytes_list.value[0].decode('utf-8')

        ## check pass or not
        if cnt.get(lab, 0) >= sample_size[lab]:
            continue
        df.append({'x': vector,
                   'y': idx}, ignore_index=True)
        cnt[lab] = cnt.get(lab, 0) + 1
        if cnt[lab] >= sample_size[lab]:
            done.add(lab)
            if len(done) == len(sample_size):
                break
        if DEBUG:
            print(f'{lab} {cnt[lab]}', end='\r')


def main():
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')
    
    dataset = get_data(FLAGS.input)
    if DEBUG:
        print(f'Dataset: {dataset}')
    idx2lab, lab2cnt = get_index(dataset)
    if DEBUG:
        print(f'lab2cnt: {lab2cnt}')
    weights = get_weight(FLAGS.weight, idx2lab)
    if DEBUG:
        print(f'weights: {weights}')
    datatick = get_datatick(lab2cnt, weights)
    if DEBUG:
        print(f'datatick: {datatick}')
    sample_size = get_sample_size(weights, datatick)
    if DEBUG:
        print(f'sample_size: {sample_size}')
    dataframe = get_dataframe(dataset, sample_size)
    dataframe.to_pickle(FLAGS.output)
    if DEBUG:
        print(f'Done pickling to {FLAGS.output}')


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='The present debug message')
    parser.add_argument('--input', type=str, required=True,
                        help='The path of tfrecords')
    parser.add_argument('--weight', type=str,
                        help='The application weights')
    parser.add_argument('--output', type=str, required=True,
                        help='The path of DataFrame pickle')
    parser.add_argument('--buffersize', type=int, default=1024*100,
                        help='The size of buffer used in shuffle')

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))
    DEBUG = FLAGS.debug
    
    main()
