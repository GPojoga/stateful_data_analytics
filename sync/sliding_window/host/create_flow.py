import sys
sys.path.append('network')

from utils import *


def cflow_pkt(ipv4_dst, eth_dst, win_size):
    """ 
        Create a packet that is used to request 
        the creation of a new flow    

    Args:
        ipv4_dst (string): the ip address of the server
        win_size ([type]): the size of the window to be created

    Returns:
        bytes : raw representation of the packet
    """
    pkt = Ether(src=get_if_hwaddr('s1-eth0'), dst=eth_dst) 
    pkt /= IP(dst=ipv4_dst, proto=SWA_PRTCL)
    pkt /= SWinAvg(op=SWA_CREATE, winsize=win_size)
    return bytes(pkt)


@print_swa
def process_flow_key(pkt):
    """
        Print the key stored in an SWA header.

    Args:
        pkt (Packet): a packet containing IP and SWA headers
    """
    print(f'The flow key is {hex(pkt["SWinAvg"].key)}')


def create_flow(ipv4_dst, eth_dst, win_size): 
    """
        Create a new flow
    Args:
        ipv4_dst (string): the ip address of the server
        win_size (int): the size of the window to be created
    """
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))    
        
        skt.send(cflow_pkt(ipv4_dst, eth_dst, win_size))
        process_flow_key(pkt=get_swa(skt))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Required argument : [window size]")
    
    create_flow(IP_DPDK, ETH_DPDK, int(sys.argv[1]))
    