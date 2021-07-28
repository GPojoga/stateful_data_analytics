#include "sliding_window_hdr.h"

/**
 * @brief operation completed successfully
 * 
 * @param swa SWA header
 */
void success(swa_t *swa);

/**
 * @brief the operation requested is unknown. 
 * return error to the client
 * 
 * @param swa SWA header
 */
void error_unknown_operation(swa_t *swa);

/**
 * @brief the specified key is inexistent.
 * 
 * @param swa SWA header
 */
void error_unknown_key(swa_t *swa);

/**
 * @brief the requested resources are unavailable.
 * 
 * @param swa SWA header
 */
void error_no_resources(swa_t *swa);