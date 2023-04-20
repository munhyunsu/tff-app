import os
import pickle
import matplotlib.pylab as plt


def main():
    # Print Parameters
    print(f'Parsed: {FLAGS}')
    print(f'Unparsed: {_}')

    # [round_num, loss, accuracy, val_loss, val_accuracy]
    with open(FLAGS.input, 'rb') as f:
        data = pickle.load(f)
    loss = data[1]
    accuracy = data[2]
    val_loss = data[3]
    val_accuracy = data[4]

    fig1 = plt.figure(figsize=(8, 8))
    ax1 = fig1.add_subplot(2, 1, 1)
    ax1.plot(accuracy, label='Training Accuracy')
    ax1.plot(val_accuracy, label='Validation Accuracy')
    ax1.legend(loc='lower right')
    ax1.set_ylabel('Accuracy')
    ax1.set_ylim([0, 1])
    ax1.set_title('Training and Validation Accuracy')

    ax2 = fig1.add_subplot(2, 1, 2)
    ax2.plot(loss, label='Training Loss')
    ax2.plot(val_loss, label='Validation Loss')
    ax2.legend(loc='upper right')
    ax2.set_ylabel('Cross Entropy')
    ax2.set_ylim([0,max(ax2.get_ylim())])
    ax2.set_title('Training and Validation Loss')
    ax2.set_xlabel('epoch')
    fig1.savefig(FLAGS.output)


if __name__ == '__main__':
    root_path = os.path.abspath(__file__)
    root_dir = os.path.dirname(root_path)
    os.chdir(root_dir)

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, required=True,
                        help='Metric pickle')
    parser.add_argument('--output', type=str,
                        default='metric.png',
                        help='Output chart file name')

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()
