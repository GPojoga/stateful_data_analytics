const bit<32> CONTROLLER_IP = 0x0a010101;
const bit<8> TYPE_SWINAVG = 0x99;
const bit<16> TYPE_IPV4 = 0x0800;

const bit<4> SWA_SUCCESS = 0xf;
const bit<4> SWA_UNKN_OP = 1;
const bit<4> SWA_UNKN_KEY = 2;

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    bit<32>   srcAddr;
    bit<32>   dstAddr;
}

header swinavg_t {
    bit<4> op;
    bit<4> errno;
    bit<32> key;
    bit<32> value; 
    bit<16> window_size; 
}

struct headers {
    ethernet_t ethernet;
    ipv4_t ipv4;
    swinavg_t swinavg;
}

struct metadata {
    bit<16> idx;
    bit<16> winsize;
}

