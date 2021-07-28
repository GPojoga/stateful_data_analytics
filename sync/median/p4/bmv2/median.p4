#include "storage.p4"

control Median(
    inout headers hdrs,
    inout metadata meta,
    inout standard_metadata_t std_meta
) { 
    Storage() storage;

    bit<48> mac_temp;
    bit<32> ip_temp;

    /**
    *   @brief Return the packet to its sender
    */
    action reverse() {
        mac_temp = hdrs.ethernet.srcAddr;
        hdrs.ethernet.srcAddr = hdrs.ethernet.dstAddr;
        hdrs.ethernet.dstAddr = mac_temp;

        ip_temp = hdrs.ipv4.srcAddr;
        hdrs.ipv4.srcAddr = hdrs.ipv4.dstAddr;
        hdrs.ipv4.dstAddr = ip_temp;
        hdrs.ipv4.ttl = 64;
    }

    /**
    *   @brief The specified flow key is unknown
    */
    action no_key() {
        hdrs.median.errno = MED_UNKN_KEY;
    }

    /**
    *   @brief Retrieve the flow id and the flow size, 
    *   based on the flow key from the packet
    *
    *   @param flow_idx absolute index of the flow
    *   @param flow_size the number of values in the flow
    */
    action process(bit<16> flow_idx, bit<16> flow_size) {
        meta.flow_idx = flow_idx;
        meta.flow_size = flow_size;
    }

    /**
    *   @brief the requested operation is unknown
    */
    action unkn_op() {
        hdrs.median.errno = MED_UNKN_OP;
    }

    /**
    *   @brief redirect the packet to the controller
    */
    action redirect_to_controller() {
        hdrs.ipv4.dstAddr = CONTROLLER_IP; 
    }

    /**
    *   @brief map flow keys => flow index, flow size
    */
    table median {
        key = {
            hdrs.median.key : exact;
        }

        actions = {
            no_key;
            process;
        }

        default_action = no_key();
    }

    apply {
        if (hdrs.median.errno == MED_UNPROCESSED) { // the pkt was not processed
            if (hdrs.median.op == MED_ADD || 
                hdrs.median.op == MED_GET ||
                hdrs.median.op == MED_REMOVE) { 
                median.apply();
            }
            if (hdrs.median.errno != MED_UNKN_KEY) { // flow key is known
                switch (hdrs.median.op) {
                    MED_CREATE : {
                        redirect_to_controller();
                    }
                    MED_ADD :
                    MED_GET : {
                        storage.apply(hdrs, meta, std_meta);
                        reverse();
                    }
                    MED_REMOVE : {
                        redirect_to_controller();
                    }
                    default : {
                        unkn_op();
                        reverse();
                    }
                }
            } else {
                reverse();
            }
        }
    }
}