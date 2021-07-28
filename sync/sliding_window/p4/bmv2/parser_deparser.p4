parser ParserImpl(
    packet_in packet,
    out headers hdrs,
    inout metadata meta,
    inout standard_metadata_t std_meta
) {
    state start {
        transition ethernet;
    }

    state ethernet {
        packet.extract(hdrs.ethernet);
        transition select(hdrs.ethernet.etherType) {
            TYPE_IPV4 : ipv4;
            default : accept;
        }
    }

    state ipv4 {
        packet.extract(hdrs.ipv4);
        transition select(hdrs.ipv4.protocol) {
            TYPE_SWINAVG: swinavg;
            default : accept;
        }
    }

    state swinavg {
        packet.extract(hdrs.swinavg);
        transition accept;
    }
}

control DeparserImpl(
    packet_out packet,
    in headers hdrs    
) {
    apply {
        packet.emit(hdrs.ethernet);
        packet.emit(hdrs.ipv4);
        packet.emit(hdrs.swinavg);
    }
}
