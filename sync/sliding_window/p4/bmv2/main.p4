#include <core.p4>
#include <v1model.p4>

#include "headers.p4"
#include "checksum.p4"
#include "parser_deparser.p4"
#include "ipv4.p4"
#include "swind_avg.p4"

control IngressImpl(
    inout headers hdrs,
    inout metadata meta,
    inout standard_metadata_t std_meta
) {
    IPv4() ipv4;
    SWingAvg() swinavg;

    apply {
        if (hdrs.swinavg.isValid()){
            swinavg.apply(hdrs, meta, std_meta);
        }
        if (hdrs.ipv4.isValid()) {
            ipv4.apply(hdrs, meta, std_meta);
        }
    }
}

control EgressImpl(
    inout headers hdrs,
    inout metadata meta,
    inout standard_metadata_t std_meta
) {
    apply {

    }
}

V1Switch(
    ParserImpl(),
    VerifyChecksumImpl(),
    IngressImpl(),
    EgressImpl(),
    ComputeChecksumImpl(),
    DeparserImpl()
) main;