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


def packet_counter(counter):
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
        counter[0] = counter[0] + 1
    return process_pkt


def main():
    root_path = os.path.abspath(os.path.expanduser(input('Root path: ').strip()))
    print(f'Root Path: {root_path}')

    session_length = dict()
    cnt = 0
    for label, path in read_pcap(root_path):
        counter = [0]
        sniff(offline=path, prn=packet_counter(counter), store=False)
        label_dict = session_length.get(label, dict())
        label_dict[counter[0]] = label_dict.get(counter[0], 0) + 1
        session_length[label] = label_dict
        cnt = cnt + 1
        if cnt%1000 == 0:
            print(f'{cnt}: {session_length.keys()}')
    print()

    print(session_length)
    with open('session_length.pickle', 'wb') as f:
        pickle.dump(session_length, f)


if __name__ == '__main__':
    main()
