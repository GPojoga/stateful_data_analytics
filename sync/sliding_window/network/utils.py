from socket import socket, AF_PACKET, SOCK_RAW, htons
from scapy.all import Ether, IP, get_if_hwaddr
from swinavg import *


ETH_P_IPv4 = 0x800 # ether type IPv4

SWA_PRTCL = 0x99 # ip type swa

IP_DPDK = '10.0.0.1' # ip address of the dpdk server
ETH_DPDK = "0:0:0:0:0:1" # mac address of the dpdk server

errnos = { # swa error numbers
    SWA_SUCCESS : 'SUCCESS',
    SWA_UNKN_OP : 'UNKNOWN OPERATION',
    SWA_UNKN_KEY : 'UNKNOWN KEY',
    SWA_NO_RES : 'RESOURCES UNAVAILABLE'
}


def print_swa_hdr(pkt):
    print(f"{'=' * 3} {errnos[pkt['SWinAvg'].errno]} {'=' * 3}")
    print(f"OP : {pkt['SWinAvg'].op}")
    print(f"ERRNO : {pkt['SWinAvg'].errno}")
    print(f"KEY : {hex(pkt['SWinAvg'].key)}")
    print(f"VAL : {pkt['SWinAvg'].val}")
    print(f"WINSIZE : {pkt['SWinAvg'].winsize}")
    print(f"{'=' * 10}", end='\n\n')


def print_swa(funct, *args, **kwargs):
    """Print an swa header, decorator.

    Args:
        funct (function): function to be decorated
    """
    def wrapper(pkt, *args, **kwargs):
        print_swa_hdr(pkt)
        funct(pkt, *args, **kwargs)

    return wrapper


def get_swa(skt):
    """Get an SWA packet.
    Listen until an SWA packet is received

    Args:
        skt (socket): an open socket

    Returns:
        Packet : swa packet
    """
    pkt = Ether(skt.recv(4096))
    while pkt['IP'].proto != SWA_PRTCL:
        pkt = Ether(skt.recv(4096))
    pkt['IP'].decode_payload_as(SWinAvg)
    return pkt
