
#ifndef H_SLIDING_WINDOW_HDR
#define H_SLIDING_WINDOW_HDR

#include <rte_mbuf.h>

#define IP_TYPE_SWA 0x99

/**
 * @brief sliding window average header
 * 
 * @return typedef struct 
 */
typedef struct __attribute__((__packed__)) {
    unsigned int op : 4; // type of operation
    unsigned int err_no : 4; // error number
    uint32_t key; // key identifying the flow
    uint32_t value; // the value to be added 
    uint16_t window_size; // the size of the window
} swa_t;

/**
 * @brief extract the swa header from the packet
 * 
 * @param buf packet
 * @return swa_t* a pointer to the swa header
 */
swa_t *extract_swa(struct rte_mbuf *buf);

/**
 * @brief print an swa header
 * 
 * @param swa the header to be printed
 */
void print_swa(swa_t *swa);

/**
 * @brief check if the given packet has an swa header
 * 
 * @param pkt the packet o be checked 
 * @return int (1 if true else 0)
 */
int is_swa(struct rte_mbuf *pkt);

/**
 * @brief transform the representation of the header to little endian
 * A second application will transform it back to Big-endian (or vice-versa)
 * 
 * @param swa the header to be transformed
 */
void to_little_endian(swa_t *swa);

#endif