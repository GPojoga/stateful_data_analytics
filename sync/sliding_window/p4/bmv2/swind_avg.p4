
control SWingAvg(
    inout headers hdrs,
    inout metadata meta,
    inout standard_metadata_t std_meta
) { 
    register<bit<32>>(1024) window; // array of registers holding the windows
    register<bit<32>>(1024) results; // array of registers holding the results
    // array of registers holding the starting indexes of the windows
    register<bit<16>>(1024) idxes; 

    bit<32> val;
    bit<32> res;
    bit<48> temp;
    bit<16> offset;
    
    /*
        return the packet to its sender
    */
    action reverse() {
        temp = hdrs.ethernet.srcAddr;
        hdrs.ethernet.srcAddr = hdrs.ethernet.dstAddr;
        hdrs.ethernet.dstAddr = temp;

        val = (bit<32>)hdrs.ipv4.srcAddr;
        hdrs.ipv4.srcAddr = hdrs.ipv4.dstAddr;
        hdrs.ipv4.dstAddr = (bit<32>)val;
        hdrs.ipv4.ttl = 64;
    }

    /*
        report the unknown key to the sender
    */
    action no_key() {
        hdrs.swinavg.errno = SWA_UNKN_KEY;
        reverse();
    }

    /*
        retrieve the index of the window and its size
    */
    action process(bit<16> idx, bit<16> winsize) {
        meta.idx = idx;
        meta.winsize = winsize;
    }

    /*
        A table holding the indexes of the windows and their sizes,
        which are identified with the key generated during the 
        creation of the flow
    */
    table swinavg{
        key = {
            hdrs.swinavg.key : exact;
        }

        actions = {
            no_key;
            process;
        }

        default_action = no_key();
    }

    /*
        process the flow creation request. redirect it to the controller
    */
    action create_flow() {
        hdrs.ipv4.dstAddr = CONTROLLER_IP;
    }
    
    /*
        process the flow removal request. redirect it to the controller
    */
    action remove_flow() {
        hdrs.ipv4.dstAddr = CONTROLLER_IP;
        hdrs.swinavg.value = (bit<32>) meta.idx;
        hdrs.swinavg.window_size = meta.winsize;
    }

    /*
        add a value to the window.
    */
    action add_value() {
        
        // get the idx of the oldest value
        idxes.read(offset, (bit<32>)meta.idx); 
        // get the current window result
        results.read(res, (bit<32>)meta.idx);
        // get the oldest value in the window
        window.read(val, (bit<32>)(meta.idx + offset));
        
        res = res - val + hdrs.swinavg.value; // compute the new result

        // store the new result
        results.write((bit<32>)meta.idx, res);
        // store the new value
        window.write((bit<32>)(meta.idx + offset), hdrs.swinavg.value);
        
        offset = offset + 1; // identify the next oldest value

        // report success to the client
        hdrs.swinavg.errno = SWA_SUCCESS; 
        reverse();
    }

    /*
        return the result of the requested window
    */
    action get_result() {
        results.read(res, (bit<32>) meta.idx); // read the result 

        // store the result in the header
        hdrs.swinavg.value = res;
        hdrs.swinavg.window_size = meta.winsize;
        hdrs.swinavg.errno = SWA_SUCCESS;
        reverse(); // return the packet
    }

    action unkn_op() {
        hdrs.swinavg.errno = SWA_UNKN_OP;
        reverse();
    }

    apply {
        if (hdrs.swinavg.errno == 0) { // the packet was not processed yet
            // this is a supported operation except flow creation
            if (hdrs.swinavg.op == 1 || 
                hdrs.swinavg.op == 2 ||
                hdrs.swinavg.op == 3) {
                swinavg.apply();
            }
            switch (hdrs.swinavg.op) {
                0 : { 
                    create_flow(); 
                }
                1 : {  
                    if (hdrs.swinavg.errno != SWA_UNKN_KEY)
                    {
                        add_value();
                        if (offset >= meta.winsize){ // offset mod meta.winsize
                            offset = 0;
                        }
                        idxes.write((bit<32>)meta.idx, offset);
                    } 
                }
                2 : { 
                    if (hdrs.swinavg.errno != SWA_UNKN_KEY)
                    {
                        get_result(); 
                    }   
                }
                3 : { 
                    if (hdrs.swinavg.errno != SWA_UNKN_KEY)
                    {
                        remove_flow(); 
                    }
                } 
                default : { 
                    unkn_op(); 
                }
            }
        }
    }
}

