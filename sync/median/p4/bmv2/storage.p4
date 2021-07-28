#include "processor.p4"

control Storage(
    inout headers hdrs,
    inout metadata meta,
    inout standard_metadata_t std_meta
) {
    register<bit<16>>(32) idxs; // idxs[frameidx] contains the index of the median
    register<bit<32>>(32) vals; // values
    register<bit<32>>(32) counters; // packet counters per value
    register<bit<32>>(32) left_dists; // distance to the left value
    register<bit<32>>(32) right_dists; // distance to the right value
    register<bit<32>>(1) bitmap; // bitmap of the received values
    register<bit<32>>(1) rev_bitmap; // reversed bitmap

    bit<16> old_median_idx; // used to determine if move left/right is required

    /**
    *   @brief update the flow based on the new value
    *   1. update the bitmap
    *   2. update the reversed bitmap
    *   3. update the value counter
    */
    action update_new_val(bit<32> bitmask, bit<32> rev_bitmask) {
        meta.flow.bitmap = meta.flow.bitmap | bitmask;
        meta.flow.rev_bitmap = meta.flow.rev_bitmap | rev_bitmask;
        meta.flow.nr_vals = meta.flow.nr_vals + 2;

        counters.write((bit<32>)meta.val_idx, meta.flow.nr_vals);
    }

    /**
    *   @brief extract all the flow data from the registers
    */
    action extract_data() {
        idxs.read(meta.flow.median_idx, (bit<32>)meta.flow_idx);
        old_median_idx = meta.flow.median_idx;
        vals.read(meta.flow.median, (bit<32>)meta.flow.median_idx);
        left_dists.read(meta.flow.left_dst, (bit<32>)meta.flow.median_idx);
        right_dists.read(meta.flow.right_dst, (bit<32>)meta.flow.median_idx);
        bitmap.read(meta.flow.bitmap, 0);
        rev_bitmap.read(meta.flow.rev_bitmap, 0);
        counters.read(meta.flow.nr_vals, (bit<32>)meta.val_idx);
    }

    /**
    *   @brief store the updated data to the registers
    */
    action store_data() {
        idxs.write((bit<32>)meta.flow_idx, meta.flow.median_idx);
        left_dists.write((bit<32>)meta.flow.median_idx, meta.flow.left_dst);
        right_dists.write((bit<32>)meta.flow.median_idx, meta.flow.right_dst);
        bitmap.write(0, meta.flow.bitmap);
        rev_bitmap.write(0, meta.flow.rev_bitmap);
        counters.write((bit<32>)meta.val_idx, meta.flow.nr_vals);
    }

    /**
    *   @brief update the distances of the new median
    *   when a move to the previous greatest number occurred
    */
    action move_left() {
        counters.read(meta.flow.nr_vals, (bit<32>)meta.flow.median_idx);
        meta.flow.left_dst = meta.flow.nr_vals;
        meta.flow.right_dst = 0;
    }

    /**
    *   @brief update the distances of the new median
    *   when a move to the next smallest number occurred
    */
    action move_right() {
        counters.read(meta.flow.nr_vals, (bit<32>)meta.flow.median_idx);
        meta.flow.left_dst = 1;
        meta.flow.right_dst = meta.flow.nr_vals - 1;
    }

    /**
    *   @brief extract the absolute index of the received value
    */
    action process(bit<16> val_idx) {
        meta.val_idx = meta.flow_idx + val_idx;
    }

    /**
    *   @brief the specified value is not part of the flow
    */
    action no_val() {
        hdrs.median.errno = MED_UNKN_VAL;
    }

    /**
    *   @brief map the value index to its bitmap and reversed bitmap
    *   e.g., 3 => ...00001000, 0001000...
    */
    table update_val { 
        key = {
            meta.val_idx : exact;
        }

        actions = {
            update_new_val;
        }
    }

    /**
    *   @brief map a value to its relative index in the flow
    */
    table val_idx { 
        key = {
            hdrs.median.key : exact;
            hdrs.median.val : exact;
        }

        actions = {
            no_val;
            process;
        }

        default_action = no_val();
    }

    Processor() processor;

    // meta.flow_idx and meta.flow_size are set in median.py
    apply {
        switch(hdrs.median.op) {
            MED_ADD : {
                val_idx.apply();
                if (hdrs.median.errno != MED_UNKN_VAL) {
                    
                    // process first value in the flow
                    bitmap.read(meta.flow.bitmap, 0);
                    if (meta.flow.bitmap == 0) {
                        meta.flow.median_idx = meta.val_idx;
                        idxs.write((bit<32>)meta.flow_idx, meta.flow.median_idx);
                    }
                    // ===============================

                    extract_data();

                    update_val.apply();

                    processor.apply(hdrs, meta, std_meta);
                    
                    if (meta.flow.median_idx < old_median_idx) { // move left
                        move_left();
                    } 
                    if (meta.flow.median_idx > old_median_idx) { // move right
                        move_right();
                    }
                    store_data();
                    hdrs.median.errno = MED_SUCCESS;
                }
            }
            MED_GET : {
                idxs.read(meta.flow.median_idx, (bit<32>)meta.flow_idx);
                vals.read(hdrs.median.val, (bit<32>)meta.flow.median_idx);
                hdrs.median.errno = MED_SUCCESS;
            }
            default : {
                NoAction();
            }
        }
    }
}
