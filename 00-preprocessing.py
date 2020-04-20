# Load library
import os
import subprocess
import shlex
import shutil

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

    for label, path in read_pcap(FLAGS.input):
        dst = os.path.abspath(
                    os.path.expanduser(os.path.join(FLAGS.temp, label)))
        split_pcap(path, dst)


def pkt2vec(pkt, img_size):
    ip = pkt['IP']
    hexst = raw(ip).hex()
    arr = np.array([int(hexst[i:i+2], 16) for i in range(0, len(hexst), 2)])
    arr = arr[0:img_size*img_size]
    arr = np.pad(arr, (0, img_size*img_size-len(arr)), 'constant', constant_values=0)
    fv = np.reshape(arr, (-1, img_size))
    fv = np.uint8(fv)
    fv = np.stack((fv, fv, fv), axis=2)
    return fv


def pkt2img(base, label, cnt):
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
        if len(raw(ip[l4].payload)) < PAYLOAD_MIN:
            return
        fv = pkt2vec(pkt)
        num = cnt.get(label, 0)
        dst = os.path.join(base, f'{num:{FMT}}.png')
        cnt[label] = num + 1
        img = Image.fromarray(fv)
        img.save(dst)
        if num % 1000 == 1:
            print(f'{label}: {num} Processed')
    return process_pkt


def stop_filter(current):
    def process_pkt(pkt):
        global current
        if not pkt.haslayer('IP'):
            return False
        ip = pkt['IP']
        if not (ip.haslayer('TCP') or ip.haslayer('UDP')):
            return False
        if ip.haslayer('TCP'):
            l4 = 'TCP'
        elif ip.haslayer('UDP'):
            l4 = 'UDP'
        if len(raw(ip[l4].payload)) < PAYLOAD_MIN:
            return False
        current[0] += 1
        if current[0] > COUNT:
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
                        label = os.path.basename(os.path.dirname(entry.path)) # dirname is label
                        yield label, entry.path
                elif not entry.name.startswith('.') and entry.is_dir():
                    queue.append(entry.path)


def split_pcap(src, dst):
    os.makedirs(dst, exist_ok=True)
    cmd = f'PcapSplitter -f {src} -o {dst} -m connection'
    cmd = shlex.split(cmd)
    subprocess.run(cmd)


def main():
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')

    do_reset()

    cnt = dict()
    current = list()

    for label, path in read_pcap(splited_path):
        base = os.path.abspath(os.path.expanduser(os.path.join(IMG_DATA, label)))
        os.makedirs(base, exist_ok=True)
        current[0] = 0
        sniff(offline=path, prn=pkt2img(base, label, cnt), store=False, stop_filter=stop_filter(current))
        print()
    print(cnt)

    

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

    parser.add_argument('--img_size', type=int,
                        default=39,
                        help='Packet to vector image size')
    
    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.temp = os.path.abspath(os.path.expanduser(FLAGS.temp))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))
    
    main()