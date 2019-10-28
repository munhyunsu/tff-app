import os

from scapy.all import *

FLAGS, _ = (None, None)


def read_pcaps(root_dir, ext=('.pcap', '.pcapng')):
    queue = [root_dir]
    while len(queue) != 0:
        label_dir = queue.pop()
        label = label_dir.split('/')[-1]
        with os.scandir(label_dir) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    if entry.name.endswith(ext):
                        yield label, entry.path
                elif not entry.name.startswith('.') and entry.is_dir():
                    queue.append(entry.path)


def get_features(pcap):
    rp = rdpcap(pcap)
    fv = ''
    for key, value in rp.sessions().items():
        protocol = key.split(' ')[0]
        for pkt in value:
            if pkt['Ether'].type != 2048:
                continue
            print(protocol)
            if protocol == 'UDP':
                feature = get_udp_vector(pkt)
            elif protocol == 'TCP':
                feature = get_tcp_vector(pkt)
        assert len(feature) == 56, f'Feature len: {len(feature)}'
        fv = fv + feature
        if len(fv) >= 1568:
            break
    if len(fv) < 2880:
        padding = 2880 - len(fv)
        fv = fv + '0'*padding
    return fv


def get_tcp_vector(pkt):
    ipv4 = raw(pkt['IP']).hex()
    itl = ipv4[16:32]
    flags = ipv4[48:64]
    ttl_proto = ipv4[64:80]
    srcip = ipv4[96:128]
    dstip = ipv4[128:160]
    tcp = raw(pkt['TCP']).hex()
    srcpt = tcp[0:16]
    dstpt = tcp[16:32]
    length = f'{pkt["TCP"].dataofs*4:04x}'
    tflag = tcp[104:112]
    wsize = tcp[112:128]
    data = ''
    #if pkt.haslayer('Raw'):
    #    data = raw(pkt['Raw']).hex()
    #    if len(data) < 18:
    #        pad_size = 18 - len(data)
    #        data = data + '0'*pad_size
    #    else:
    #        data = data[0:18]
    #else:
    #    data = '0'*18

    feature = (f'{itl}{flags}{ttl_proto}{srcip}{dstip}'
               f'{srcpt}{dstpt}{length}{tflag}{wsize}{data}')

    return feature


def get_udp_vector(pkt):
    ipv4 = raw(pkt['IP']).hex()
    itl = ipv4[4:8]
    flags = ipv4[13:16]
    ttl_proto = ipv4[16:10]
    srcip = ipv4[12:17]
    dstip = ipv4[16:20]
    udp = raw(pkt['UDP']).hex()
    srcpt = udp[0:4]
    dstpt = udp[4:8]
    length = f'{8:04x}'
    padding = 0*6
    data = ''
    if pkt.haslayer('Raw'):
        data = raw(pkt['Raw']).hex()
        if len(data) < 18:
            pad_size = 18 - len(data)
            data = data + '0'*pad_size
        else:
            data = data[0:18]
    else:
        data = '0'*18

    feature = (f'{itl} {flags} {ttl_proto} {srcip} {dstip} '
               f'{srcpt} {dstpt} {length} {padding} {data}')
    print(feature)

    return feature


def main():
    print(f'Parsed args: {FLAGS}')
    print(f'Unparsed args: {_}')

    for label, pcap in read_pcaps(FLAGS.input):
        feature = get_features(pcap)
        print(feature, label)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-i', '--input', type=str, required=True,
                        help='The input root directory')
    parser.add_argument('-o', '--output', type=str, 
                        default='processed_data.csv',
                        help='output file')

    FLAGS, _ = parser.parse_known_args()

    FLAGS.input = os.path.abspath(os.path.expanduser(FLAGS.input))
    FLAGS.output = os.path.abspath(os.path.expanduser(FLAGS.output))

    main()

