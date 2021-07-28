#ifndef H_SLIDING_WINDOW
#define H_SLIDING_WINDOW

#include "sliding_window_hdr.h"

/**
 * @brief SWA flow table entry 
 * 
 */
typedef struct {
    uint32_t *window; 
    uint16_t window_size;
    uint16_t idx;
    uint32_t window_sum;
} swa_table_entry;

/**
 * @brief initialize all the required data
 * should be called only once. before processing starts
 */
void init_processing(void);

/**
 * @brief initialize an SWA table entry
 * 
 * @param swa must contain the requested window size
 * @return swa_table_entry* a dynamically allocated table entry
 */
swa_table_entry *init_table_entry(swa_t *swa);

/**
 * @brief free the resources of the table entry
 * 
 * @param ste the table entry to be cleaned
 */
void clear_table_entry(swa_table_entry *ste);

/**
 * @brief print a table entry
 * 
 * @param ste the entry to be printed
 */
void print_table_entry(swa_table_entry *ste);

/**
 * @brief Process an SWA application packet
 * 
 * @param swa the swa header
 */
void process_swa(swa_t *swa);

/**
 * @brief Create a new flow 
 * 
 * @param swa 
 */
void create_flow(swa_t *swa);

/**
 * @brief add a value to the given flow
 * 
 * @param swa 
 */
void add_value(swa_t *swa);

/**
 * @brief Get the current result for a given flow
 * 
 * @param swa 
 */
void get_result(swa_t *swa);

/**
 * @brief remove the specified flow
 * 
 * @param swa 
 */
void remove_flow(swa_t *swa);

#endif