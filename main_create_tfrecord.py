# Load library
import os
import subprocess
import shlex
import shutil
import multiprocessing

from scapy.all import *
from PIL import Image
import numpy as np

import tensorflow as tf

FLAGS = None
_ = None


def do_reset():
    global FLAGS
    if os.path.exists(FLAGS.output):
        shutil.rmtree(FLAGS.output)
    os.makedirs(FLAGS.output, exist_ok=True)
    
    if FLAGS.reset and os.path.exists(FLAGS.temp):
        shutil.rmtree(FLAGS.temp)
        
    if FLAGS.reset:
        for path, label in read_pcap(FLAGS.input):
            dst = os.path.abspath(
                    os.path.expanduser(os.path.join(FLAGS.temp, label)))
            split_pcap(path, dst)


def pkt2tfrecord(writers, label, idx):
    global FLAGS
    label_ = [label.encode('utf-8')]
    idx_ = [idx]
    def as_tfrecord(pkt):
        if not pkt.haslayer('IP'):
            return
        ip = pkt['IP']
        if not (ip.haslayer('TCP') or ip.haslayer('UDP')):
            return
        if ip.haslayer('TCP'):
            l4 = 'TCP'
        elif ip.haslayer('UDP'):
            l4 = 'UDP'
        if len(raw(ip[l4].payload)) < FLAGS.payload:
            return
        
        vector_ = pkt2vec(pkt).tolist()

        tf_example = tf.train.Example(features=tf.train.Features(feature={
            'vector': tf.train.Feature(int64_list=tf.train.Int64List(value=vector_)),
            'label': tf.train.Feature(bytes_list=tf.train.BytesList(value=label_)),
            'idx': tf.train.Feature(int64_list=tf.train.Int64List(value=idx_)),
        }))

        writers[label].write(tf_example.SerializeToString())
    
    return as_tfrecord 


def pkt2vec(pkt):
    ip = pkt['IP']
    hexst = raw(ip).hex()
    arr = np.array([int(hexst[i:i+2], 16) for i in range(0, len(hexst), 2)])
    arr = arr[0:4*375]
    arr = np.pad(arr, (0, 4*375-len(arr)), 'constant', constant_values=0)
    fv = np.uint8(arr)
    fv = fv.flatten()
    return fv


def stop_filter(current):
    global FLAGS
    def process_pkt(pkt):
        if not pkt.haslayer('IP'):
            return False
        ip = pkt['IP']
        if not (ip.haslayer('TCP') or ip.haslayer('UDP')):
            return False
        if ip.haslayer('TCP'):
            l4 = 'TCP'
        elif ip.haslayer('UDP'):
            l4 = 'UDP'
        if len(raw(ip[l4].payload)) < FLAGS.payload:
            return False
        current[0] = current[0] + 1
        if current[0] > FLAGS.limit:
            return True
        return False
    return process_pkt


def read_pcap(root_dir, ext=('.pcap', '.pcapng')):
    queue = [root_dir]
    while len(queue) != 0:
        nest_dir = queue.pop()
        with os.scandir(nest_dir) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    if entry.name.endswith(ext):
                        label = os.path.basename(os.path.dirname(entry.path))
                        yield entry.path, label
                elif not entry.name.startswith('.') and entry.is_dir():
                    queue.append(entry.path)

                    
def get_labels(root_dir):
    labels = list()
    with os.scandir(root_dir) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_dir():
                label = os.path.basename(entry.path)
                labels.append(label)
    labels.sort()
    return labels

                    
def split_pcap(src, dst):
    os.makedirs(dst, exist_ok=True)
    cmd = f'PcapSplitter -f {src} -o {dst} -m connection'
    cmd = shlex.split(cmd)
    subprocess.run(cmd)


def set_writers(labels):
    global FLAGS
    writers = dict()
    for label in labels:
        wpath = os.path.join(FLAGS.output, f'{label}.tfrecord')
        writer = tf.io.TFRecordWriter(wpath)
        writers[label] = writer
    return writers


def main():
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')

    do_reset()
    labels = get_labels(FLAGS.input)
    writers = set_writers(labels)

    current = [0] # for a stop_filter
    for path, label in read_pcap(FLAGS.temp):
        print(f'Processing {path} {label}')
        idx = labels.index(label)
        sniff(offline=path, prn=pkt2tfrecord(writers, label, idx),
              store=False, stop_filter=stop_filter(current))

    for writer in writers.values():
        writer.close()


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument
    parser.add_argument('--input', type=str, required=True,
                        help=('Target directory which has pcap files '
                              'in subdirectory'))
    parser.add_argument('--temp', type=str,
                        default='./splited_data',
                        help='Temporarory directory')
    parser.add_argument('--reset', action='store_true',
                        help='Clear temporary files')
    parser.add_argument('--output', type=str, required=True,
                        help='Output directory')
    parser.add_argument('--payload', type=int,
                        default=1,
                        help='Payload size of IP packets')
    parser.add_argument('--limit', type=int,
                        default=float('inf'),
                        help='Limit count per target pcap')

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.temp = os.path.abspath(os.path.expanduser(FLAGS.temp))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()
