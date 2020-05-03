import os
import pprint

FLAGS = None
_ = None


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
                        yield label, entry.path
                elif not entry.name.startswith('.') and entry.is_dir():
                    queue.append(entry.path)


def main():
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')

    count = dict()
    for label, path in get_files(FLAGS.input):
        count[label] = count.get(label, 0) + 1

    pprint.pprint(count)


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True,
                        help=('Target directory which has pcap files '
                              'in subdirectory'))

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))

    main()
