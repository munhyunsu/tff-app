import os
import sys

from scapy.all import *

FLAGS = None
_ = None
GLOBAL = dict()

class PacketSniffer(object):
    def __init__(iface=None):
        pass

def gopath():
    global FLAGS
    return os.path.abspath(os.path.expanduser(FLAGS.output))

def pkt_handler():
    global FLAGS
    writer = PcapWriter(gopath())
    def handler(pkt):
        writer.write(pkt)

    return handler



def main():
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')

    try:
        sniff(prn=pkt_handler(), store=False, 
              filter='ip')
    except KeyboardInterrupt:
        print(f'Keyboard Interrupted. Shutting down program.')


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--output', type=str,
                        default='output.pcap',
                        help='The output pcap path')

    FLAGS, _ = parser.parse_known_args()

    # preprocessing for some arguments
    FLAGS.config = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()

