#ifndef H_MEDIAN_ERRNO
#define H_MEDIAN_ERRNO

#include "median_hdr.h"

// error codes
#define MED_UNPROCESSED 0
#define MED_UNKN_OP 1
#define MED_UNKN_KEY 2
#define MED_NO_RES 3
#define MED_UNKN_VAL 4
#define MED_SUCCESS 0xf

/**
 * @brief operation completed successfully
 * 
 * @param medpkt the packet to be marked
 */
void success(medpkt_t *medpkt);

/**
 * @brief the requested operation is unknown
 * 
 * @param medpkt the packet to be marked
 */
void error_unknown_operation(medpkt_t *medpkt);

/**
 * @brief the provided key is unknown
 * 
 * @param medpkt the packet to be marked
 */
void error_unknown_key(medpkt_t *medpkt);

/**
 * @brief the requested resources are not avaialable
 * 
 * @param medpkt the packet to be marked
 */
void error_no_resources(medpkt_t *medpkt);

/**
 * @brief the provided value is unknown
 * 
 * @param medpkt the packet to be marked
 */
void error_unknown_value(medpkt_t *medpkt);

#endif
