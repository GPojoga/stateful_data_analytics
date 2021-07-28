
control IPv4(
    inout headers hdrs,
    inout metadata meta,
    inout standard_metadata_t std_meta
) {
    action drop() {
        mark_to_drop(std_meta);
    }

    action forward(bit<48> dstAddr, bit<9> port) {
        hdrs.ethernet.srcAddr = hdrs.ethernet.dstAddr;
        hdrs.ethernet.dstAddr = dstAddr;
        hdrs.ipv4.ttl = hdrs.ipv4.ttl - 1;
        std_meta.egress_spec = port;
    }

    table ipv4_route {
        key = {
            hdrs.ipv4.dstAddr : lpm;
        }
        actions = {
            drop;
            forward;
        }
        default_action = drop();
    }

    apply {
        ipv4_route.apply();
    }
}
