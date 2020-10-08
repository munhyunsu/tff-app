import os
import pickle

import pandas as pd


def load_dataset(path_root):
    dpath = os.path.join(path_root, 'sampled_dataset.pickle')
    dataset = pd.read_pickle(dpath)

    ipath = os.path.join(path_root, 'get_index.pickle')
    with open(ipath, 'rb') as f:
        idx2lab, lab2cnt = pickle.load(f)
    
    return dataset, idx2lab, lab2cnt