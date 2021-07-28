import sys
sys.path.append("network")

from utils import *



def rflow_pkt(ipv4_dst, eth_dst, flow_key):
    """Build a packet for removing an SWA flow

    Args:
        ipv4_dst (string): address of the server hosting the window
        flow_key (int): the flow key

    Returns:
        bytes : raw representation of the packet
    """
    pkt = Ether(src=get_if_hwaddr('s1-eth0'), dst=eth_dst) 
    pkt /= IP (dst=ipv4_dst, proto=SWA_PRTCL) 
    pkt /= SWinAvg(op=SWA_REMOVE, key=flow_key)
    return bytes(pkt)


@print_swa
def get_result(pkt):
    pass


def remove_flow(ipv4_dst, eth_dst, flow_key): 
    """Remove the flow identified by the given key

    Args:
        ipv4_dst (string): the ip address of the server
        flow_key (int): the flow key
    """
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))    
        skt.send(rflow_pkt(ipv4_dst, eth_dst, flow_key))
        get_result(pkt=get_swa(skt))
        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Required parameters : [flow key (in hex)]")

    remove_flow(IP_DPDK, ETH_DPDK, int(sys.argv[1], 16))
    