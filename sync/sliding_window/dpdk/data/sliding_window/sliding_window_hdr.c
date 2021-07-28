#include <stdio.h>

#include <rte_ether.h>
#include <rte_ip.h>
#include <rte_byteorder.h>

#include <endian.h>

#include "sliding_window_hdr.h"
#include "process_packet.h"


swa_t *extract_swa(struct rte_mbuf *pkt)
{   
    swa_t *swa = rte_pktmbuf_mtod_offset(
                    pkt, 
                    swa_t *, 
                    sizeof(struct ether_hdr) + sizeof(struct ipv4_hdr)
            );
            
    return swa;
}

void print_swa(swa_t *swa)
{   
    printf("===== SWA =====\n");
    printf("op : %x\n", swa->op);
    printf("error no : %x\n", swa->err_no);
    printf("key : %u\n", swa->key);
    printf("value : %u\n", swa->value);
    printf("window size : %u\n", swa->window_size);
    printf("===============\n");
}

int is_swa(struct rte_mbuf *pkt)
{
    struct ether_hdr *eth = extract_eth(pkt);
    if (rte_bswap16(eth->ether_type) == ETHER_TYPE_IPv4) // has ipv4 header
        return extract_ipv4(pkt)->next_proto_id == IP_TYPE_SWA; // has SWA header
    return 0;
}

void to_little_endian(swa_t *swa)
{
    uint8_t temp = swa->op;
    swa->op = swa->err_no;
    swa->err_no = temp;
    swa->key = rte_bswap32(swa->key);
    swa->value = rte_bswap32(swa->value);
    swa->window_size = rte_bswap16(swa->window_size);
}
