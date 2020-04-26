# Load library
import os
import subprocess
import shlex
import shutil
import multiprocessing

from scapy.all import *
from PIL import Image
import numpy as np

FLAGS = None
_ = None


def do_reset():
    global FLAGS
    if os.path.exists(FLAGS.output):
        shutil.rmtree(FLAGS.output)
    if FLAGS.reset and os.path.exists(FLAGS.temp):
        shutil.rmtree(FLAGS.temp)
    if FLAGS.reset:
        for label, path in read_pcap(FLAGS.input):
            dst = os.path.abspath(
                    os.path.expanduser(os.path.join(FLAGS.temp, label)))
            split_pcap(path, dst)


def pkt2vec(pkt):
    ip = pkt['IP']
    hexst = raw(ip).hex()
    arr = np.array([int(hexst[i:i+2], 16) for i in range(0, len(hexst), 2)])
    arr = arr[0:4*375]
    arr = np.pad(arr, (0, 4*375-len(arr)), 'constant', constant_values=0)
    fv = np.reshape(arr, (-1, 4))
    fv = np.uint8(fv)
    return fv


def pkt2img(base, prefix, cnt):
    global FLAGS
    def process_pkt(pkt):
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
        fv = pkt2vec(pkt)
        dst = os.path.join(base, f'{prefix}-{cnt[0]:08d}.png')
        cnt[0] = cnt[0] + 1
        img = Image.fromarray(fv)
        img.save(dst)
    return process_pkt


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
                        yield label, entry.path
                elif not entry.name.startswith('.') and entry.is_dir():
                    queue.append(entry.path)


def split_pcap(src, dst):
    os.makedirs(dst, exist_ok=True)
    cmd = f'PcapSplitter -f {src} -o {dst} -m connection'
    cmd = shlex.split(cmd)
    subprocess.run(cmd)


def process_pcap(args):
    label = args[0]
    path = args[1]
    base = os.path.abspath(
             os.path.expanduser(os.path.join(FLAGS.output, label)))
    os.makedirs(base, exist_ok=True)
    prefix = os.path.basename(path)
    cnt = [0]
    current = [0]
    sniff(offline=path, prn=pkt2img(base, prefix, cnt), 
          store=False, stop_filter=stop_filter(current))
    return label, current[0]


def main():
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')

    do_reset()

    cnt = dict()
    current = [0]
    with multiprocessing.Pool(FLAGS.process) as p:
        joined_result = p.imap_unordered(process_pcap, read_pcap(FLAGS.temp))
        for result in joined_result:
            print(f'{result[0]}: {result[1]}')


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
                        default='./img_data',
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
