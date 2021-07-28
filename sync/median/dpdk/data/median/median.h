#ifndef H_MEDIAN
#define H_MEDIAN

#include <rte_hash.h>

#include "median_hdr.h"

/**
 * @brief A value in the flow
 * and additional data that describe it
 */
typedef struct {
    uint16_t index;     // index in the frame
    uint32_t val;       // the value at that index
    uint32_t left_dst;  // distance to the left neighbour
    uint32_t right_dst; // distance to the right neighbour
    uint32_t nr_vals;   // 2 * the number of packets received with this value 
} felem;

/**
 * @brief Median table entry
 * It contains all the necessary information about a flow.
 */
typedef struct {
    felem *frame; // the list of values (and additional data) of the flow
    uint32_t bitmap; // a bit map of the present/absent values in the flow
    uint32_t rev_bitmap; // reversed bitmap
    uint16_t idx; // current index of the median
    uint16_t frame_size; // the number of values in flow
    struct rte_hash_parameters params; // val_idx table params
    struct rte_hash *val_idx; // map value to its index
} mte_t;

/**
 * @brief process a median request
 *
 * @param medpkt median header and additional values
 */
void process_medpkt(medpkt_t *medpkt);

/**
 * @brief initialize the data structures necessary for the algorithm
 * , such as hash tables. To be called once, before processing starts.
 */
void init_processing(void);

/**
 * @brief Initialize a median table entry from a Median create request
 * 
 * @param medpkt median header and additional values
 * @return mte_t* dinamically allocated median table entry
 */
mte_t *init_mte(medpkt_t *medpkt);

/**
 * @brief Initialize a frame of the flow
 * a frame is a value of the flow, and additional data that describe it
 * @param medpkt 
 * @return felem* 
 */
felem *init_frame(medpkt_t *medpkt);

/**
 * @brief Compare two frames
 * Needed for sorting a list of frames
 * @param a the first frame
 * @param b the second frame
 * @return int | a == b => 0 | a < b => -1 | a > b => 1 |
 */
int compare_frames(const void *a, const void *b);

/**
 * @brief Release the resources allocated for
 * a median table entry
 * @param mte the entry to be deallocated
 */
void clean_mte(mte_t *mte);

/**
 * @brief print a median table entry
 * 
 * @param mte 
 */
void print_mte(mte_t *mte);

/**
 * @brief print a list of frames
 * 
 * @param frame the frames to be printed
 * @param size the size of the list
 */
void print_frame(felem *frame, uint16_t size);

/**
 * @brief Process a Create request
 * 
 * @param medpkt the request
 */
void create_flow(medpkt_t *medpkt);

/**
 * @brief Process an Add request
 * 
 * @param medpkt the request
 */
void add_value(medpkt_t *medpkt);

/**
 * @brief Process a Get request
 * 
 * @param medpkt the request
 */
void get_result(medpkt_t *medpkt);

/**
 * @brief Process a remove request
 * 
 * @param medpkt the request
 */
void remove_flow(medpkt_t *medpkt);                 

/**
 * @brief Update the bitmaps and the value counter 
 * when a new value is added
 * @param mte the median table entry to be updated
 * @param index the index of the value in flow
 */
void update_new_value(mte_t *mte, uint16_t index);

/**
 * @brief move the index of the median to the 
 * next smallest value
 * @param mte median table entry to be updated
 */
void move_right(mte_t *mte);

/**
 * @brief move the index of the median to the
 * previous greatest value
 * @param mte median table entry to be updated
 */
void move_left(mte_t *mte);

#endif