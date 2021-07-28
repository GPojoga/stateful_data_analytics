control Processor(
    inout headers hdrs,
    inout metadata meta,
    inout standard_metadata_t std_meta
) { 

    bit<32> bitmask = 0;
    bit<32> bmap = 0;
    bit<3> movement = 0; // 0 - no move; 1 - move left; 2 - move right

    /**
    *   @brief Store the request mask
    *   See the description of table mask
    */
    action process_mask(bit<32> bmask) {
        bitmask = bmask;
    }

    /**
    *   Given a number n return a mask (32 bit) which 
    *   only preserves the bits that are more 
    *   significant than the one from index n.
    *   e.g., n = 4 => ...1111100000
    */
    table mask {
        key = {
            meta.flow.median_idx : exact;
        }

        actions = {
            process_mask;
        }
    }

    /**
    *   @brief Extract the logarithm from a number
    *   and store it as the median index
    */
    action process_log2(bit<16> id) {
        meta.flow.median_idx = id;
    }

    /**
    *   @brief take log2 from a number of the form 2^n
    */
    table log2 {
        key = {
            bitmask : exact;
        }
        
        actions = {
            process_log2;
        }
    }

    apply {
        if (hdrs.median.val == meta.flow.median) { // received value == median
            meta.flow.left_dst = meta.flow.left_dst + 1;
            meta.flow.right_dst = meta.flow.right_dst + 1;
        } else if (hdrs.median.val < meta.flow.median) { 
            if (meta.flow.left_dst == 1) { // move left
                movement = 1;
                bmap = meta.flow.rev_bitmap;
            } else {
                meta.flow.left_dst = meta.flow.left_dst - 1;
                meta.flow.right_dst = meta.flow.right_dst + 1;
            }
        } else if (hdrs.median.val > meta.flow.median) {
            if (meta.flow.right_dst == 0) { // move right
                movement = 2;   
                bmap = meta.flow.bitmap; 
            } else {
                meta.flow.left_dst = meta.flow.left_dst + 1;
                meta.flow.right_dst = meta.flow.right_dst - 1;
            }
        }

        if (movement == 1) { // move left
            meta.flow.median_idx = 31 - meta.flow.median_idx;
        }
        if (movement != 0) { // move left or right
            mask.apply();
            bitmask = bmap & bitmask;
            bitmask = bitmask & ~(bitmask - 1);
            log2.apply();    
        }
        if (movement == 1) { // move left
            meta.flow.median_idx = 31 - meta.flow.median_idx;
        }
    }
}