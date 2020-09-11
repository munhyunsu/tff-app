import os
import csv

import tensorflow as tf

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