
from scapy.all import Packet, BitField

# Operations
SWA_CREATE = 0
SWA_ADD = 1
SWA_GET = 2
SWA_REMOVE = 3

# Error codes
SWA_SUCCESS = 0xf
SWA_UNKN_OP = 1
SWA_UNKN_KEY = 2
SWA_NO_RES = 3

class SWinAvg(Packet):
    """
        Sliding window average header
    """
    name = "swinavg"
    fields_desc = [
        BitField("op", 0, 4),
        BitField("errno", 0, 4),
        BitField("key", 0, 32),
        BitField("val", 0, 32),
        BitField("winsize", 0, 16)
    ]
    