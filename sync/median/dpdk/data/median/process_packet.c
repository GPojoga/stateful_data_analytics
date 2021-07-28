
#include <rte_mbuf.h>
#include <rte_ethdev.h>

#include "process_packet.h"
#include "median.h"

void lcore_work(void)
{   
    
    init_processing();

    while (1) 
    {
        struct rte_mbuf *pkt;
		const uint16_t nb_rx = rte_eth_rx_burst(0, 0, &pkt, 1);

        if (nb_rx && is_med(pkt)) // a med packet was received
        {   
            medpkt_t *medpkt = extract_medpkt(pkt);
            #if BYTE_ORDER == LITTLE_ENDIAN
                to_little_endian(medpkt);
            #endif

            process_medpkt(medpkt);
            
            reverse_packet(pkt);

            #if BYTE_ORDER == LITTLE_ENDIAN
                to_little_endian(medpkt);
            #endif
            clean_medpkt(medpkt);
            rte_eth_tx_burst(0, 0, &pkt, 1);
        }
    }
}

void reverse_packet(struct rte_mbuf* pkt)
{   
    struct ether_hdr *eth = extract_eth(pkt);
    struct ipv4_hdr *ip = extract_ipv4(pkt);

    struct ether_addr temp_ether = eth->s_addr;
	eth->s_addr = eth->d_addr;
	eth->d_addr = temp_ether;

	uint32_t temp_ip = ip->src_addr;
	ip->src_addr = ip->dst_addr;
	ip->dst_addr = temp_ip;
	ip->time_to_live = 64;
}

struct ether_hdr *extract_eth(struct rte_mbuf *pkt)
{
    return rte_pktmbuf_mtod(pkt, struct ether_hdr *);
}

struct ipv4_hdr *extract_ipv4(struct rte_mbuf *pkt)
{
    return rte_pktmbuf_mtod_offset(pkt, struct ipv4_hdr *, sizeof(struct ether_hdr));
}
