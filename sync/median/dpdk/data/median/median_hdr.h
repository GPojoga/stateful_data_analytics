
#ifndef H_MEDIAN_HDR
#define H_MEDIAN_HDR

#include <rte_mbuf.h>

#define IP_TYPE_MED 0x98

// operations
#define MED_CREATE 0
#define MED_ADD 1
#define MED_GET 2
#define MED_REMOVE 3

/**
 * @brief median header
 */
typedef struct __attribute__((__packed__)) {
    unsigned int op : 4; // type of operation
    unsigned int err_no : 4; // error number
    uint32_t key; // key identifying the flow
    uint32_t value; // the value to be added / the result
    uint16_t nrvals; // the size of the frame
} med_t;

/**
 * @brief median header together with the 
 * additional values
 */
typedef struct {
    med_t *med; // median header
    uint32_t *vals; // the values passed together with the header
} medpkt_t;

/**
 * @brief extract the median packet from the receive buffer
 * i.e., median header and additional values
 * @param pkt the receive buffer
 * @return medpkt_t* the extracted median packet
 */
medpkt_t *extract_medpkt(struct rte_mbuf *pkt);

/**
 * @brief extract the median header from the receive buffer
 * 
 * @param pkt the receive buffer
 * @return med_t* the extracted median header
 */
med_t *extract_med(struct rte_mbuf *pkt);

/**
 * @brief print median header
 * 
 * @param med the header to be printed
 */
void print_med(med_t *med);

/**
 * @brief print additional values of a median packet
 * 
 * @param vals an array of values
 * @param size the size of the array
 */
void print_vals(uint32_t *vals, uint16_t size);

/**
 * @brief print median packet
 * i.e., median header and additional values
 * @param medpkt median packet
 */
void print_medpkt(medpkt_t *medpkt);

/**
 * @brief check if the received packet has the median header
 * 
 * @param pkt receive buffer
 * @return int 1 if true else 0
 */
int is_med(struct rte_mbuf *pkt);

/**
 * @brief transform the representation of the header to little endian
 * A second application will transform it back to Big-endian (or vice-versa)
 * 
 * @param medpkt the header to be transformed (median ad additional values)
 */
void to_little_endian(medpkt_t *medpkt);

/**
 * @brief release the resources allocated for the median packet
 * 
 * @param medpkt the packet to be freed
 */
void clean_medpkt(medpkt_t *medpkt);

#endif
