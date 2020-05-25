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
        for path, labels, idx in read_pcap(FLAGS.input):
            dst = os.path.abspath(
                    os.path.expanduser(os.path.join(FLAGS.temp, labels[idx])))
            split_pcap(path, dst)


def pkt2tfrecord(writer, label, idx):
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

        writer.write(tf_example.SerializeToString())
    
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
    labels = get_labels(root_dir)
    queue = [root_dir]
    while len(queue) != 0:
        nest_dir = queue.pop()
        with os.scandir(nest_dir) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    if entry.name.endswith(ext):
                        label = os.path.basename(os.path.dirname(entry.path))
                        yield entry.path, labels, labels.index(label)
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


def process_pcap(args):
    global tfwriter
    writer = tfwriter
    path = args[0]
    labels = args[1]
    idx = args[2]
    label = labels[idx]

    current = [0]
    sniff(offline=path, prn=pkt2tfrecord(writer, label, idx), 
            store=False, stop_filter=stop_filter(current))
    return label, current[0]

tfwriter = None

def main():
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')
    global tfwriter

    do_reset()

    tf_record_path = os.path.join(FLAGS.output, f'dataset_{FLAGS.payload}.tfrecord')
    with tf.io.TFRecordWriter(tf_record_path) as writer:
        tfwriter = writer
        with multiprocessing.Pool(FLAGS.process) as p:
            results = p.imap_unordered(process_pcap, read_pcap(FLAGS.temp))
            for result in results:
                continue


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True,
                        help=('Target directory which has pcap files '
                              'in subdirectory'))
    parser.add_argument('--temp', type=str,
                        default='./splited_data',
                        help='Temporarory directory')
    parser.add_argument('--reset', type=bool,
                        default=False,
                        help='Clear temporary files')
    parser.add_argument('--output', type=str,
                        default='./tfrecord',
                        help='Output directory')
    parser.add_argument('--payload', type=int,
                        default=1,
                        help='Payload size of IP packets')
    parser.add_argument('--limit', type=int,
                        default=float('inf'),
                        help='Limit count per target pcap')
    parser.add_argument('--process', type=int,
                        default=multiprocessing.cpu_count(),
                        help='The number of process pool')

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.temp = os.path.abspath(os.path.expanduser(FLAGS.temp))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()
