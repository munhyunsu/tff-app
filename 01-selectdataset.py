# Load library
import os
import shutil
import random

FLAGS = None
_ = None


def do_reset():
    global FLAGS
    if os.path.exists(FLAGS.output):
        shutil.rmtree(FLAGS.output)


def get_files(root_dir, ext=('.jpg', '.png')):
    queue = [root_dir]
    while len(queue) != 0:
        nest_dir = queue.pop()
        label = None
        files = list()
        with os.scandir(nest_dir) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    if entry.name.endswith(ext):
                        label = os.path.basename(
                                  os.path.dirname(entry.path))
                        files.append(entry.path)
                elif not entry.name.startswith('.') and entry.is_dir():
                    queue.append(entry.path)
            if label is not None:
                yield label, files


def main():
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')

    do_reset()

    for label, files in get_files(FLAGS.input):
        random.shuffle(files)
        nfile = len(files) if FLAGS.count == 0 else FLAGS.count
        dst = os.path.join(FLAGS.output, label)
        os.makedirs(dst, exist_ok=True)
        for path in files[:nfile]:
            shutil.copy(path, dst)


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True,
                        help=('Target directory which has pcap files '
                              'in subdirectory'))
    parser.add_argument('--output', type=str,
                        default='./selected_data',
                        help='Output directory')
    parser.add_argument('--count', type=int,
                        default=0,
                        help='File count per class')

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()
