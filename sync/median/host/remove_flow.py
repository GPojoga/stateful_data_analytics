import sys
sys.path.append("network")

from utils import *


def rflow_pkt(ipv4_dst, eth_dst, flow_key):
    """Generate a REMOVE FLOW packet

    Args:
        ipv4_dst (string): the ipv4 address of the server
        eth_dst (string): the ether address of the server
        flow_key (int): the key of the flow

    Returns:
        bytes: the REMOVE FLOW packet
    """
    pkt = Ether(src=get_if_hwaddr('s1-eth0'), dst=eth_dst) 
    pkt /= IP (dst=ipv4_dst, proto=MED_PRTCL) 
    pkt /= Median(op=MED_REMOVE, key=flow_key)
    return bytes(pkt)


@print_med
def get_result(pkt):
    """Process the REMOVE FLOW response

    Args:
        pkt (Packet): REMOVE FLOW response
    """
    pass


def remove_flow(ipv4_dst, eth_dst, flow_key): 
    """Send a REMOVE FLOW request and process the response

    Args:
        ipv4_dst (string): the ipv4 address of the server
        eth_dst (string): the ehter address of the server
        flow_key ([type]): [description]
    """
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))    
        skt.send(rflow_pkt(ipv4_dst, eth_dst, flow_key))
        get_result(pkt=get_med(skt))
        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Required parameters : [flow key (in hex)]")

    remove_flow(IP_DPDK, ETH_DPDK, int(sys.argv[1], 16))
    