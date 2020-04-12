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


def main():
    global CFG
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')
    
    

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
    
    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.temp = os.path.abspath(os.path.expanduser(FLAGS.temp))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))
    
    main()
