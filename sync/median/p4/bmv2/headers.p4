#define TYPE_IPV4 0x0800
#define TYPE_MEDIAN 0x98  
#define CONTROLLER_IP 0x0a010101

// operations 
#define MED_CREATE 0 // Create Flow request
#define MED_ADD 1    // Add Value request
#define MED_GET 2    // Get Result request
#define MED_REMOVE 3 // Remove Flow request

// error codes
#define MED_UNPROCESSED 0 // Request not processed
#define MED_UNKN_OP 1     // Unknown operation
#define MED_UNKN_KEY 2    // Unknown key
#define MED_NO_RES 3      // No available resources
#define MED_UNKN_VAL 4    // Unknown value
#define MED_SUCCESS 0xf   // Success

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

header median_t {
    bit<4> op;
    bit<4> errno;
    bit<32> key;
    bit<32> val;
    bit<16> nrvals;
}

struct headers {
    ethernet_t ethernet;
    ipv4_t ipv4;
    median_t median;
}

struct flow_t {
    bit<16> median_idx; // the absolute index of the median
    bit<32> median;     // the value of the median
    bit<32> nr_vals;    // 2 * number of packets received with a given number
    bit<32> left_dst;   // the ditance to the left neighbour
    bit<32> right_dst;  // the distance to the right neighbour 
    bit<32> bitmap;     // the bitmap of all the values from all the flows
    bit<32> rev_bitmap; // the reversed bitmap
} 

struct metadata {
    flow_t flow;       // flow data
    bit<16> val_idx;   // the absolute index of the value to be added
    bit<16> flow_idx;  // the absolute starting index of the flow
    bit<16> flow_size; // the size of the flow
}
