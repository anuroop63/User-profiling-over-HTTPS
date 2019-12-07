import dpkt
import struct

def parse_extensions(buf):
    extensions_length = struct.unpack('!H', buf[:2])[0]
    extensions = []
    pointer = 2
    while pointer < extensions_length:
        ext_type = struct.unpack('!H', buf[pointer:pointer + 2])[0]
        pointer += 2
        ext_data, parsed = dpkt.ssl.parse_variable_array(buf[pointer:], 2)
        extensions.append(SNIExtract(ext_type, ext_data))
        pointer += parsed
    return extensions

def main():
    encoding = 'utf-8'
    f = open('/Users/ratan/Desktop/Dumps/Shopping/4/20191201185133.pcap','rb')
    dpkt.ssl.parse_extensions = parse_extensions
    pcap = dpkt.pcap.Reader(f)
    for ts, buf in pcap:
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data
        tcp = ip.data
        if not isinstance(ip, dpkt.ip.IP):
            continue
        ip = eth.data
        if not isinstance(tcp, dpkt.tcp.TCP):
            continue

        if len(tcp.data) <= 0:
            continue
        try:
            tls = dpkt.ssl.TLS(tcp.data)
            if len(tls.records) < 1:
                continue
            handshake = dpkt.ssl.TLSHandshake(tls.records[0].data)
        except:
            # print("error")
            continue

        client_hello = handshake.data

        if isinstance(client_hello, dpkt.ssl.TLSClientHello):
            for ext in client_hello.extensions:
                if ext.value == 0:
                    server_name = (str(ext.data[5:], encoding))
                    print(server_name)

class SNIExtract(object):
    def __init__(self, ext_number, data):
        self.data = data
        self.value = ext_number

if __name__ == '__main__':
    main()
