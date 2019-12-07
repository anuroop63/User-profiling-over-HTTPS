import dpkt, socket, os , sys, glob, numpy, itertools
from itertools import islice
import ntpath

from random import random
class Packets:
    def __init__(self, timestamp, data):
        self.size = len(data)
        self.Ethernet = data[0:14]
        self.IP = data[14:34]
        self.TCP = data[34:self.size]
        self.ts = timestamp

        self.ttl = self.IP[8]
        self.protocol = self.IP[9]
        self.sourceIP = self.IP[12:16]
        self.destIP = self.IP[16:20]

        self.sourcePort = self.TCP[0:2]
        self.destPort = self.TCP[2:4]
        self.sequence_no = self.TCP[4:8]
        self.ack_no = self.TCP[8:12]
        self.flags = self.TCP[12:14]
        self.window = self.TCP[14:16]
        self.checksum = self.TCP[16:18]


#process filename and url mappings
filename_url_map = {}

filenam_url_file = open('/Users/ratan/PycharmProjects/ebay_info/ebay_file_url.txt')
for line in filenam_url_file:
    line=line.strip('\n')

    filename_url_map[str(line.split(",")[0])] = line.split(",")[1]



label_url_map = {}

lable_url_file = open('/Users/ratan/PycharmProjects/ebay_info/ebay_url_label_map')

for line in lable_url_file:
    line = line.strip('\n')
    x = line.split("-$$-")[1]
    try:
        label_url_map[x] = line.split("-$$-")[0]
    except :
        print("Exception")

print("label_url_map",list(islice(label_url_map.items(), 10)))
print("filename_url_map",list(islice(filename_url_map.items(), 10)))

print("length of filename-url map" , len(filename_url_map))
print("length of label-url map", len(label_url_map))

path = '/Users/ratan/Desktop/new_final/'

fdout = open('/Users/ratan/PycharmProjects/ebay_info/feature_ebay_test_all', 'w')

root_dir = path
label=0
rec= 0
# print(path)
for filename in glob.glob(root_dir+"*.pcap" ):
    # print(filename)
    if os.path.isfile(filename):
        # print(filename)
        pfile = open(filename, 'rb')
        pcap = dpkt.pcap.Reader(pfile)
        total_packets = 0
        pkt_size = 0
        insize = 0
        outsize = 0
        out_pkts = []
        in_pkts = []
        cumulative_insize=[]
        features=[]

        for tstamp, pktdata in pcap:
            eth = dpkt.ethernet.Ethernet(pktdata)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                continue
            ip = eth.data
            if ip.p != dpkt.ip.IP_PROTO_TCP:
                continue

            total_packets += 1
            packets = Packets(tstamp, pktdata)
            src_ip = socket.inet_ntoa(packets.sourceIP)
            des_ip = socket.inet_ntoa(packets.destIP)
            pkt_size += packets.size

            if src_ip == '10.0.2.15':
                out_pkts.append((tstamp, pktdata))
                outsize += len(pktdata)
            else:
                in_pkts.append((tstamp, pktdata))
                insize += len(pktdata)
                cumulative_insize.append(insize)

        filenamet = ntpath.basename(filename).split(".")[0].strip('\n')

        url=""
        try:
            url = filename_url_map[filenamet]
        except:
            print("file mapping error", filename)

        try:
            label = label_url_map[str(url)]
        except:
            print("lable mapping error", filename, url)

        features.append(label)
        features.append( len(in_pkts))
        features.append(len(out_pkts))
        features.append(outsize)
        features.append(insize)
        featureCount = 100
        cumFeatures = numpy.interp(numpy.linspace(cumulative_insize[0], cumulative_insize[-1], featureCount + 1), cumulative_insize, cumulative_insize)

        for el in itertools.islice(cumFeatures, 1, None):
            features.append(el)

        rec = rec+1
        fdout.write(str(features[0]) + ' ' + ' '.join(['%d:%.2f' % (i + 1, el) for i, el in enumerate(features[1:])]) + ' # ' + str('dummy') + '\n')

print("Total recs written: ",rec)
fdout.close();
