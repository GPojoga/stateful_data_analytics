from socket import socket, AF_PACKET, SOCK_RAW, htons
from scapy.all import Ether, IP, get_if_hwaddr
from median import *

ETH_P_IPv4 = 0x800 # ether type IPv4

MED_PRTCL = 0x98 # median protocol

IP_DPDK = '10.0.0.1' # ip address of the dpdk server
ETH_DPDK = "0:0:0:0:0:1" # mac address of the dpdk server

errnos = { # swa error numbers
    MED_UNPROCESSED : 'REQUEST NOT PROCESSED',
    MED_SUCCESS : 'SUCCESS',
    MED_UNKN_OP : 'UNKNOWN OPERATION',
    MED_UNKN_KEY : 'UNKNOWN KEY',
    MED_NO_RES : 'RESOURCES UNAVAILABLE',
    MED_UNKN_VAL : 'UNKNOWN VALUE'
}


def get_med(skt):
    """Get a median packet

    Args:
        skt (Socket): the open socker where the packet is expected

    Returns:
        Packet: a packet containing the median header
    """
    pkt = Ether(skt.recv(4096))
    while pkt['IP'].proto != MED_PRTCL:
        pkt = Ether(skt.recv(4096))
    pkt['IP'].decode_payload_as(Median)

    if pkt['Median'].nrvals > 0:
        pkt['Median'].decode_payload_as(Value)
    for i in range(1, pkt['Median'].nrvals):
        pkt['Value'][i - 1].decode_payload_as(Value)
    
    return pkt


def print_med_hdr(pkt):
    """Print a median header

    Args:
        pkt (Packet): packet containing a median header
    """
    print(f"{'=' * 3} {errnos[pkt['Median'].errno]} {'=' * 3}")
    print(f"OP : {pkt['Median'].op}")
    print(f"ERRNO : {pkt['Median'].errno}")
    print(f"KEY : {hex(pkt['Median'].key)}")
    print(f"VAL : {pkt['Median'].val}")
    print(f"NR_VALS : {pkt['Median'].nrvals}")
    print(f"{'=' * 10}")


def print_val_hdrs(pkt):
    """Print the values attached to a median packet

    Args:
        pkt (Packet): a packet containing a median header
    """
    print("+" * 10)
    for i in range(pkt['Median'].nrvals):
        print(f"Val : {pkt['Value'][i].val}")
        print("+" * 10)

def print_med(funct, *args, **kwargs):
    """Print median header decorator

    Args:
        funct (Function): the function to be decorated, must have a pkt argument
    """
    def wrapper(pkt, *args, **kwargs):
        print_med_hdr(pkt)
        funct(pkt, *args, **kwargs)

    return wrapper

def print_vals(funct, *args, **kwargs):
    """Print the values attached to a median packet decorator

    Args:
        funct (Function): the function to be decorated, must have a pkt argument
    """
    def wrapper(pkt, *args, **kwargs):
        print_val_hdrs(pkt)
        funct(pkt, *args, **kwargs)

    return wrapper