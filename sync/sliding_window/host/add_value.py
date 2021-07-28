import sys
sys.path.append('network')

from utils import *


def aval_pkt(ipv4_dst, eth_dst, flow_key, value):
    """
        Build a packet for adding a new value to a window

    Args:
        ipv4_dst (string): address of the server hosting the window
        flow_key (int): key of the window 
        value (int): the value to be added to the window

    Returns:
        bytes : raw representation of the packet
    """
    pkt = Ether(src=get_if_hwaddr('s1-eth0'), dst=eth_dst) 
    pkt /= IP (dst=ipv4_dst, proto=SWA_PRTCL) 
    pkt /= SWinAvg(op=SWA_ADD, key=flow_key, val=value)
    return bytes(pkt)


@print_swa
def get_response(pkt):
    pass


def add_value(ipv4_dst, eth_dst, flow_key, value): 
    """Add a value to the flow identified by 
    the given key

    Args:
        ipv4_dst (string): the ip address of the server
        flow_key (int): the key of the flow
        value (int): the value to be added
    """
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))    
        skt.send(aval_pkt(ipv4_dst, eth_dst, flow_key, value))
        get_response(pkt=get_swa(skt))
        

if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise Exception("Required parameters : [flow key (in hex)] [value]")

    add_value(IP_DPDK, ETH_DPDK, int(sys.argv[1], 16), int(sys.argv[2]))
