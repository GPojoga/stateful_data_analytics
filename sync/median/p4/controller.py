import sys
sys.path.extend(["network", "../network"])

import random 
from simple_switch_api import SSApi
from utils import *


bitmap = [0] * 1024
flow = {} # store flow keys and their values
flow_key_idx = {} # store the flow keys and their indexes


def reverse_packet(pkt):
    """return the packet to its sender

    Args:
        pkt (Packet): a network packet with IP and ETH headers
    """
    pkt['Ether'].src, pkt['Ether'].dst = pkt['Ether'].dst, pkt['Ether'].src 
    pkt['IP'].src, pkt['IP'].dst = pkt['IP'].dst, pkt['IP'].src
    pkt['IP'].ttl = 64


def find_window(length):
    """Find an available window of the requested size

    Args:
        length (int): size of the window to be searched for

    Returns:
        int: the starting index of the available window
        None : if a window of the requested size was not found
    """
    i = 0
    while i < len(bitmap):
        free_space = 0
        idx = i
        while i < len(bitmap) and bitmap[i] == 0:
            free_space += 1
            if free_space == length:
                bitmap[idx:idx + free_space] = [1] * free_space
                return idx
            i += 1
        i += 1


def create_flow(pkt):
    """Process a CREATE FLOW request

    Args:
        pkt (Packet): a packet containing a Median CREATE FLOW request
    """
    frame_idx = find_window(pkt['Median'].nrvals)
    if frame_idx is None:
        pkt['Median'].errno = MED_NO_RES
        return

    values = sorted([pkt['Value'][i].val for i in range(pkt['Median'].nrvals)])
    pkt['Median'].key = random.randint(0, 2**32 - 1)

    flow[pkt['Median'].key] = values
    flow_key_idx[pkt['Median'].key] = frame_idx

    with SSApi() as ssapi:
        ssapi.table_add(
            tname='IngressImpl.med.median',
            action='IngressImpl.med.process',
            match=(pkt['Median'].key, ),   
            params=(frame_idx, pkt['Median'].nrvals)
        )   
        ssapi.register_write(
            'IngressImpl.med.storage.idxs',
            frame_idx,
            frame_idx
        )
        for i in range(pkt['Median'].nrvals):
            ssapi.table_add(
                tname='IngressImpl.med.storage.val_idx',
                action='IngressImpl.med.storage.process',
                match=(pkt['Median'].key, values[i]),
                params=(i, )
            )
            ssapi.register_write(
                rname='IngressImpl.med.storage.vals',
                idx=frame_idx + i,
                val=values[i]
            )
    
    pkt['Median'].errno = MED_SUCCESS


def clean_val_idx(ssapi, pkt):
    """Remove all the entries from the value to index hash table

    Args:
        ssapi (SSApi): simple switch api
        pkt (Packet): packet containing a Median header
    """
    values = flow[pkt['Median'].key]
    for i in range(len(values)):
        ssapi.table_delete(
            tname='IngressImpl.med.storage.val_idx',
            keys=(pkt['Median'].key, values[i])
        )


def clean_registers(ssapi, pkt):
    """Clean the registers allocated for the flow

    Args:
        ssapi (SSApi): simple switch api
        pkt (Packet): packet containing a Median header
    """
    values = flow[pkt['Median'].key]
    frame_idx = flow_key_idx[pkt['Median'].key]
    for i in range(frame_idx, frame_idx + len(values)):
        ssapi.register_write(rname='IngressImpl.med.storage.idxs', idx=i, val=0)
        ssapi.register_write(rname='IngressImpl.med.storage.vals', idx=i, val=0)
        ssapi.register_write(rname='IngressImpl.med.storage.counters', idx=i, val=0)
        ssapi.register_write(rname='IngressImpl.med.storage.left_dists', idx=i, val=0)
        ssapi.register_write(rname='IngressImpl.med.storage.right_dists', idx=i, val=0)


def clean_bitmaps(ssapi, pkt):
    """Clean the bitmap and reversed bitmap

    Args:
        ssapi (SSApi): simple switch api
        pkt (Packet): packet containing a Median header
    """
    frame_idx = flow_key_idx[pkt['Median'].key]
    nrvals = len(flow[pkt['Median'].key])

    bmap = ssapi.register_read('IngressImpl.med.storage.bitmap', 0)
    rbmap = ssapi.register_read('IngressImpl.med.storage.rev_bitmap', 0)
        
    mask = (2 ** 32 - 1) - ((2 ** nrvals - 1) << frame_idx)
    bmap &= mask
    revmask = int(bin(mask)[2:][::-1], 2)
    rbmap &= revmask
    
    ssapi.register_write('IngressImpl.med.storage.bitmap', 0, bmap)
    ssapi.register_write('IngressImpl.med.storage.rev_bitmap', 0, rbmap)


def clear_controller_data(pkt):
    """Clear the flow data stored in the controller

    Args:
        pkt (Packet): packet containing a Median header
    """
    frame_idx = flow_key_idx[pkt['Median'].key]
    nrvals = len(flow[pkt['Median'].key])
    bitmap[frame_idx:frame_idx + nrvals] = [0] * nrvals
    del flow_key_idx[pkt['Median'].key]
    del flow[pkt['Median'].key]


def remove_flow(pkt):
    """Process a remove flow request

    Args:
        pkt (Packet): packet containing a REMOVE FLOW request
    """
    with SSApi() as ssapi:
        ssapi.table_delete(
            tname='IngressImpl.med.median',
            keys=(pkt['Median'].key, )
        )
        clean_val_idx(ssapi, pkt)
        clean_registers(ssapi, pkt)
        clean_bitmaps(ssapi, pkt)
        clear_controller_data(pkt)

    pkt['Median'].errno = MED_SUCCESS


def process_request(pkt):
    """Process incomming median packet

    Args:
        pkt (Packet): packet containing a median header
    """
    if pkt['Median'].op == MED_CREATE:
        create_flow(pkt)
    elif pkt['Median'].op == MED_REMOVE:
        remove_flow(pkt)


def main():
    with socket(AF_PACKET, SOCK_RAW, htons(ETH_P_IPv4)) as skt:
        skt.bind(('s1-eth0', 0))
        while True:
            pkt = get_med(skt)
            process_request(pkt)
            reverse_packet(pkt)
            skt.send(bytes(pkt))


if __name__ == "__main__":
    main()