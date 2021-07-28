import sys
sys.path.append('network')

from utils import *


def gres_pkt(ipv4_dst, eth_dst, flow_key):
    """Build a packet for requesting the result

    Args:
        ipv4_dst (string): address fo the server hosting the window
        flow_key (int): the flow key

    Returns:
        bytes : raw representation of the packet
    """
    pkt = Ether(src=get_if_hwaddr('s1-eth0'), dst=eth_dst) 
    pkt /= IP (dst=ipv4_dst, proto=SWA_PRTCL) 
    pkt /= SWinAvg(op=SWA_GET, key=flow_key)
    return bytes(pkt)


@print_swa
def print_flow_result(pkt):
    """Print the sum and the window size of 
    and SWA header

    Args:
        pkt (Packet): a packet with IP and SWA headers
    """
    print(f"{'=' * 3}{hex(pkt['SWinAvg'].key)}{'='* 3}")
    print(f"sum : {pkt['SWinAvg'].val}")
    print(f"winsize : {pkt['SWinAvg'].winsize}")
    print('=' * 16)


def get_result(ipv4_dst, eth_dst, flow_key):
    """Get the current result from a flow
    identified with the given key

    Args:
        ipv4_dst (string): the ip address of the server
        flow_key (int): the flow key
    """
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))    
        
        skt.send(gres_pkt(ipv4_dst, eth_dst, flow_key))
        print_flow_result(pkt=get_swa(skt))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Required parameters : [flow key] ")
    get_result(IP_DPDK, ETH_DPDK, int(sys.argv[1], 16))
    