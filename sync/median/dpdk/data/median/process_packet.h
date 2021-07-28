
#ifndef H_PROCESS_PACKET
#define H_PROCESS_PACKET

#include <rte_ether.h>
#include <rte_ip.h>

/**
 * @brief Process all the incomming packets
 * 
 */
void lcore_work(void);

/**
 * @brief return the packet to its sender
 * 
 * @param pkt the packet to be returned
 */
void reverse_packet(struct rte_mbuf* pkt);

/**
 * @brief extract the ethernet header from the given packet
 * 
 * @param pkt the packet containing the header
 * @return struct ether_hdr* the extracted header
 */
struct ether_hdr *extract_eth(struct rte_mbuf *pkt);

/**
 * @brief extract the ipv4 header from the given packet
 * 
 * @param pkt the packet containing the header
 * @return struct ipv4_hdr* the extracted header
 */
struct ipv4_hdr *extract_ipv4(struct rte_mbuf *pkt);


#endif
