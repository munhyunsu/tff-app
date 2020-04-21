# Load library
import os
import pickle

from scapy.all import *

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


def main():
    root_path = os.path.abspath(os.path.expanduser(input('Root path: ').strip()))
    print(f'Root Path: {root_path}')

    session_length = dict()
    mid_print = dict()
    cnt = 0
    for label, path in read_pcap(root_path):
        pcap = rdpcap(path)
        label_dict = session_length.get(label, dict())
        slen = len(pcap)
        label_dict[slen] = label_dict.get(slen, 0) + 1
        session_length[label] = label_dict
        cnt = cnt + 1
        mid_print[label] = mid_print.get(label, 0) + 1
        if cnt%10000 == 0:
            print(f'{cnt}: {mid_print}')
    print(f'{cnt}: {mid_print}')

    with open('session_length.pickle', 'wb') as f:
        pickle.dump(session_length, f)


if __name__ == '__main__':
    main()
