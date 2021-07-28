import sys
sys.path.append('network')
from scapy.all import Ether, IP, sendp, get_if_hwaddr, AsyncSniffer
from utils import *
import time


def cflow_pkt(ipv4_dst, eth_dst, vals):
    """Generate a CREATE FLOW packet

    Args:
        ipv4_dst (string): the ipv4 address of the server
        eth_dst (string): the ether address of the server
        vals (list(int)): the values to be added to the flow

    Returns:
        bytes: CREATE FLOW packet
    """
    pkt = Ether(src=get_if_hwaddr('s1-eth0'), dst=eth_dst) 
    pkt /= IP(dst=ipv4_dst, proto=MED_PRTCL)
    pkt /= Median(op=MED_CREATE, nrvals=len(vals))
    for v in vals:
        pkt /= Value(val=v)

    return bytes(pkt)


@print_med
@print_vals
def process_flow_key(pkt):
    """Process the CREATE FLOW response

    Args:
        pkt (Packet): CREATE FLOW response
    """
    if pkt['Median'].errno == MED_SUCCESS:
        print(f"The flow key is {hex(pkt['Median'].key)}")


def create_flow(ipv4_dst, eth_dst, vals): 
    """Send a CREATE FLOW request and process the response

    Args:
        ipv4_dst (string): the ipv4 address of the server
        eth_dst (string): the ether address of the server
        vals (list(int)): the values to be added to the flow
    """
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))    
        
        skt.send(cflow_pkt(ipv4_dst, eth_dst, vals))
        process_flow_key(pkt=get_med(skt))


if __name__ == "__main__":
    vals = None if len(sys.argv) != 2 else [int(x) for x in sys.argv[1].split(',')]
    create_flow(IP_DPDK, ETH_DPDK, vals)