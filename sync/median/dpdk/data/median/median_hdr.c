#include <rte_ether.h>
#include <rte_ip.h>
#include <rte_byteorder.h>
#include <rte_malloc.h>

#include "median_hdr.h"
#include "process_packet.h"

med_t *extract_med(struct rte_mbuf *pkt)
{
    return rte_pktmbuf_mtod_offset(
                pkt, 
                med_t *, 
                sizeof(struct ether_hdr) + sizeof(struct ipv4_hdr)
            );
}

medpkt_t *extract_medpkt(struct rte_mbuf *pkt)
{   
    medpkt_t *medpkt = rte_malloc(NULL, sizeof(medpkt_t), 0);
    medpkt->med = extract_med(pkt);
    if (medpkt->med->nrvals == 0)
        medpkt->vals = NULL;
    else
    {
        medpkt->vals = rte_malloc(NULL, medpkt->med->nrvals * sizeof(uint32_t), 0);
        int i;
        for (i = 0; i < medpkt->med->nrvals; ++i)
            medpkt->vals[i] = *rte_pktmbuf_mtod_offset(
                                pkt, 
                                uint32_t *, 
                                sizeof(struct ether_hdr) + sizeof(struct ipv4_hdr) + 
                                sizeof(med_t) + i * sizeof(uint32_t)
                            );
    }
    return medpkt;
}

void print_med(med_t *med)
{
    printf("==== Median ====\n");
    printf("op : %x\n", med->op);
    printf("error no : %x\n", med->err_no);
    printf("key : %x\n", med->key);
    printf("value : %u\n", med->value);
    printf("nr vals : %u\n", med->nrvals);
    printf("================\n");
}

void print_vals(uint32_t *vals, uint16_t size)
{   
    printf("+++++++++++++\n");
    int i;
    for (i = 0; i < size; ++i)
    {
        printf("val : %u\n", vals[i]);
        printf("+++++++++++++\n");
    }
}

void print_medpkt(medpkt_t *medpkt)
{
    printf("--------------\n");
    print_med(medpkt->med);
    print_vals(medpkt->vals, medpkt->med->nrvals);
    printf("--------------\n");
}

int is_med(struct rte_mbuf *pkt)
{
    struct ether_hdr *eth = extract_eth(pkt);
    if (rte_bswap16(eth->ether_type) == ETHER_TYPE_IPv4) // has ipv4 header
        return extract_ipv4(pkt)->next_proto_id == IP_TYPE_MED; // has MED header
    return 0;
}

void to_little_endian(medpkt_t *medpkt)
{
    uint8_t temp = medpkt->med->op;
    medpkt->med->op = medpkt->med->err_no;
    medpkt->med->err_no = temp;
    medpkt->med->key = rte_bswap32(medpkt->med->key);
    medpkt->med->value = rte_bswap32(medpkt->med->value);
    medpkt->med->nrvals = rte_bswap16(medpkt->med->nrvals);

    int i;
    for (i = 0; i < medpkt->med->nrvals; ++i)
        medpkt->vals[i] = rte_bswap32(medpkt->vals[i]);
}

void clean_medpkt(medpkt_t *medpkt)
{
    if (medpkt->vals != NULL)
        rte_free(medpkt->vals);
    rte_free(medpkt);
}
