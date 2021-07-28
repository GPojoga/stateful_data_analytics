import sys
sys.path.extend(["network","../network"])
from utils import *
from simple_switch_api import SSApi
import random 
import time

MAX_WIN_SIZE = 1024 # the size of the SWA table in the switch

bitmap = [0 for _ in range(MAX_WIN_SIZE)] # a bitmap of the available space


def reverse_packet(pkt):
    """return the packet to its sender

    Args:
        pkt (Packet): a network packet with IP and ETH headers
    """
    pkt['Ether'].src, pkt['Ether'].dst = pkt['Ether'].dst, pkt['Ether'].src 
    pkt['IP'].src, pkt['IP'].dst = pkt['IP'].dst, pkt['IP'].src
    pkt['IP'].ttl = 64


def allocate_window(pkt, idx):
    """allocate the resources on the P4 switch

    Args:
        pkt (Packet): SWA packet
        idx (int): index of the first available segment that can accomodate the window
    """
    winsize = pkt["SWinAvg"].winsize
    bitmap[idx:idx + winsize] = [1] * winsize # mark the segment as occupied
    with SSApi() as ssapi:        
        key = random.randint(0, 2 ** 32 - 1) # generate the key
        ssapi.table_add(
            'IngressImpl.swinavg.swinavg',
            'IngressImpl.swinavg.process',
            (key,),
            (idx, winsize)
        )
    
    pkt['SWinAvg'].key = key
    pkt['SWinAvg'].errno = SWA_SUCCESS
    
    reverse_packet(pkt)


def create_flow(pkt):
    """search for free space that can accomodate a window
    of the requested size, and allocate resources.

    Args:
        pkt (Packet): an SWA packet
    """
    i = 0
    while i < len(bitmap):
        free_space, current_idx = 0, i
        while i < len(bitmap) and bitmap[i] == 0:
            free_space += 1
            i += 1
            if free_space == pkt["SWinAvg"].winsize: # found free space
                allocate_window(pkt, current_idx)
                return
        i += 1

    # free space not found
    pkt['SWinAvg'].errno = SWA_NO_RES
    reverse_packet(pkt)


def remove_flow(pkt):
    """remove the requested flow and deallocate its resources

    Args:
        pkt (Packet): an SWA packet
    """
    winsize = pkt["SWinAvg"].winsize
    idx = pkt["SWinAvg"].val
    key = pkt["SWinAvg"].key

    bitmap[idx:idx + winsize] = [0] * winsize # mark the segment as empty
    
    with SSApi() as ssapi:
        for i in range(idx, idx + winsize):
            ssapi.register_write('IngressImpl.swinavg.window', i, 0)

        ssapi.register_write('IngressImpl.swinavg.results', idx, 0)    
        ssapi.register_write('IngressImpl.swinavg.idxes', idx, 0)

        ssapi.table_delete('IngressImpl.swinavg.swinavg', keys=(key,))
    
    #report success
    pkt["SWinAvg"].errno = SWA_SUCCESS
    pkt["SWinAvg"].val = pkt["SWinAvg"].winsize = 0
    reverse_packet(pkt)


def process_request(pkt):
    """process the incomming request from a simple switch

    Args:
        pkt (Packet): an SWA packet
    """
    if pkt['SWinAvg'].op == SWA_CREATE :
        create_flow(pkt)
    elif pkt['SWinAvg'].op == SWA_REMOVE :
        remove_flow(pkt)


def main():
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))
        while True:
            pkt = get_swa(skt)
            process_request(pkt)
            skt.send(bytes(pkt))


if __name__ == "__main__":
    main()