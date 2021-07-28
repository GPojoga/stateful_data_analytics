import sys
sys.path.append('network')

from utils import *


def aval_pkt(ipv4_dst, eth_dst, flow_key, value):
    """Create a packet for an ADD VALUE request

    Args:
        ipv4_dst (string): the ipv4 address of the server
        eth_dst (string): the ether address of the server
        flow_key (int): the key of the flow
        value (int): the value to be added

    Returns:
        bytes: the ADD VALUE packet
    """
    pkt = Ether(src=get_if_hwaddr('s1-eth0'), dst=eth_dst) 
    pkt /= IP (dst=ipv4_dst, proto=MED_PRTCL) 
    pkt /= Median(op=MED_ADD, key=flow_key, val=value)
    return bytes(pkt)


@print_med
def get_response(pkt):
    """Process the ADD VALUE response

    Args:
        pkt (Packet): ADD VALUE response
    """
    pass


def add_value(ipv4_dst, eth_dst, flow_key, value): 
    """Send an ADD VALUE request and process the result

    Args:
        ipv4_dst (string): the ipv4 address of the server
        eth_dst (string): the ether address of the server
        flow_key (int): the key of the flow
        value (int): the value to be added
    """
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))    
        skt.send(aval_pkt(ipv4_dst, eth_dst, flow_key, value))
        get_response(pkt=get_med(skt))
        

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception("Required parameters : [flow key (in hex)] [value]")

    add_value(IP_DPDK, ETH_DPDK, int(sys.argv[1], 16), int(sys.argv[2]))
