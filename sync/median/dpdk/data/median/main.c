
#include <stdio.h>

#include <rte_eal.h>
#include <rte_debug.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>
#include <rte_malloc.h>

#include "process_packet.h"

#define RX_RING_SIZE 32
#define TX_RING_SIZE 32

#define NUM_MBUFS 1023
#define MBUF_CACHE_SIZE 120

/**
 * @brief initialize the ethernet device with 1 rx and 1 tx queues
 * 
 * @param port the port of the ethernet device
 * @param mbuf_pool memory pool of the rx queue
 * @return int 
 */
static inline int port_init(uint8_t port, struct rte_mempool *mbuf_pool) {
	
	struct rte_eth_conf port_conf;

	if (rte_eth_dev_configure(port, 1, 1, &port_conf))
		rte_exit(EXIT_FAILURE, "Could not configure the ethernet device\n");

	if (rte_eth_rx_queue_setup(	port, 0, RX_RING_SIZE,
								rte_eth_dev_socket_id(port), NULL, mbuf_pool) < 0)
		rte_exit(EXIT_FAILURE, "Could not configure the rx queue\n");

	if (rte_eth_tx_queue_setup( port, 0, TX_RING_SIZE,
								rte_eth_dev_socket_id(port), NULL) < 0)
		rte_exit(EXIT_FAILURE, "Could not configure the tx queue\n");

	if (rte_eth_dev_start(port) < 0)
		rte_exit(EXIT_FAILURE, "Could not start the ethernet device\n");

	rte_eth_promiscuous_enable(port);
	return 0;
}

int main(int argc, char **argv)
{	
	struct rte_mempool *mbuf_pool;

	if (rte_eal_init(argc, argv) < 0) // process a rguments
		rte_panic("Cannot init EAL\n");

	// init memory pool
	mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
		MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, rte_socket_id());

	if (mbuf_pool == NULL)
		rte_exit(EXIT_FAILURE, "Could not allocate the memory pool\n");

	if (port_init(0, mbuf_pool)) // initialize eth device
		rte_exit(EXIT_FAILURE, "Could not initialize the port");

    lcore_work(); // process incomming packets

    return 0;
}
