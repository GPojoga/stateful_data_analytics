from scapy.all import Packet, BitField

# Operations
MED_CREATE = 0
MED_ADD = 1
MED_GET = 2
MED_REMOVE = 3

# Error codes
MED_UNPROCESSED = 0 # request not processed
MED_UNKN_OP = 1 # unknown operation
MED_UNKN_KEY = 2 # unknown key
MED_NO_RES = 3 # no available resources
MED_UNKN_VAL = 4 # unknown value
MED_SUCCESS = 0xf # success


class Median(Packet):
    """Median header
    """
    name = "median"
    fields_desc = [
        BitField('op', 0, 4),
        BitField('errno', 0, 4),
        BitField('key', 0, 32),
        BitField('val', 0, 32),
        BitField('nrvals', 0, 16)
    ]


class Value(Packet):
    """ Value header
        used during flow creation
    """
    name = "value"
    fields_desc = [
        BitField('val', 0, 32)
    ]