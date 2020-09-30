# Load library
import os
import csv
import pickle

import numpy as np
import pandas as pd
import tensorflow as tf

from dataset_util import get_data, get_index, get_weight, get_datatick, get_sample_size

FLAGS = None
DEBUG = None
_ = None


def get_dataframe(dataset, sample_size):
    global FLAGS
    global DEBUG
    df = pd.DataFrame(columns=['x', 'y'])
    cnt = dict()
    done = set()
    
    for raw_record in dataset.shuffle(FLAGS.buffersize):
        ## parse data
        data = tf.train.Example.FromString(raw_record.numpy())
        vector = list(data.features.feature['vector'].int64_list.value)
        idx = data.features.feature['idx'].int64_list.value[0]
        lab = data.features.feature['label'].bytes_list.value[0].decode('utf-8')

        ## check pass or not
        if cnt.get(lab, 0) >= sample_size[lab]:
            continue
        df = df.append({'vector': vector,
                        'idx': idx,
                        'lab': lab}, ignore_index=True)
        cnt[lab] = cnt.get(lab, 0) + 1
        if cnt[lab] >= sample_size[lab]:
            done.add(lab)
            if DEBUG:
                print(f'Done {lab} {cnt[lab]}')
            if len(done) == len(sample_size):
                break
        if DEBUG:
            print(f'{lab} {cnt[lab]}', end='\r')
    return df


def main():
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')
    
    dataset = get_data(FLAGS.input)
    if DEBUG:
        print(f'Dataset: {dataset}')

    tpath = os.path.join(FLAGS.output, 'get_index.pickle')
    if os.path.exists(tpath):
        with open(tpath, 'rb') as f:
            idx2lab, lab2cnt = pickle.load(f)
    else:
        idx2lab, lab2cnt = get_index(dataset)
        with open(tpath, 'wb') as f:
            pickle.dump((idx2lab, lab2cnt), f)
    if DEBUG:
        print(f'lab2cnt: {lab2cnt}')

    tpath = os.path.join(FLAGS.output, 'get_weight.pickle')
    if os.path.exists(tpath):
        with open(tpath, 'rb') as f:
            weights = pickle.load(f)
    else:
        weights = get_weight(FLAGS.weight, idx2lab)
        with open(tpath, 'wb') as f:
            pickle.dump(weights, f)
    if DEBUG:
        print(f'weights: {weights}')
    
    tpath = os.path.join(FLAGS.output, 'get_datatick.pickle')
    if os.path.exists(tpath):
        with open(tpath, 'rb') as f:
            datatick = pickle.load(f)
    else:
        datatick = get_datatick(lab2cnt, weights)
        with open(tpath, 'wb') as f:
            pickle.dump(datatick, f)
    if DEBUG:
        print(f'datatick: {datatick}')

    tpath = os.path.join(FLAGS.output, 'get_sample_size.pickle')
    if os.path.exists(tpath):
        with open(tpath, 'rb') as f:
            sample_size = pickle.load(f)
    else:
        sample_size = get_sample_size(weights, datatick)
        with open(tpath, 'wb') as f:
            pickle.dump(sample_size, f) 
    if DEBUG:
        print(f'sample_size: {sample_size}')

    if FLAGS.buffersize == -1:
        FLAGS.buffersize = sum(lab2cnt.values())
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
    parser.add_argument('--buffersize', type=int, default=1024*1024,
                        help='The size of buffer used in shuffle')

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))
    DEBUG = FLAGS.debug
    
    main()
