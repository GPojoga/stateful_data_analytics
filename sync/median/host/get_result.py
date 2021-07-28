import sys
sys.path.append('network')

from utils import *


def gres_pkt(ipv4_dst, eth_dst, flow_key):
    """Generate a GET RESULT packet

    Args:
        ipv4_dst (string): the ipv4 address of the server
        eth_dst (string): the ether address of the server
        flow_key (int): the key of the flow

    Returns:
        bytes: the GET RESULT packet
    """
    pkt = Ether(src=get_if_hwaddr('s1-eth0'), dst=eth_dst) 
    pkt /= IP (dst=ipv4_dst, proto=MED_PRTCL) 
    pkt /= Median(op=MED_GET, key=flow_key)
    return bytes(pkt)


@print_med
def print_flow_result(pkt):
    """Process the GET RESULT response

    Args:
        pkt (Packet): GET RESULT response
    """
    if pkt['Median'].errno == MED_SUCCESS:
        print(f"The median is {pkt['Median'].val}")


def get_result(ipv4_dst, eth_dst, flow_key):
    """Send a GET RESULT request and process the response

    Args:
        ipv4_dst (string): the ipv4 address of the server
        eth_dst (string): the ether address of the server
        flow_key (int): the key of the flow
    """
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))    
        
        skt.send(gres_pkt(ipv4_dst, eth_dst, flow_key))
        print_flow_result(pkt=get_med(skt))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Required parameters : [flow key] ")
    get_result(IP_DPDK, ETH_DPDK, int(sys.argv[1], 16))
    