
#include <stdlib.h>
#include <rte_hash.h>
#include <rte_jhash.h>
#include <rte_malloc.h>

#include "sliding_window.h"
#include "sliding_window_errno.h"

static struct rte_hash *flow_table;

struct rte_hash_parameters flow_table_params =  {
    "Flow-table",   // hash table name
    1024,           // number of entries
    0,              // unused field
    32,             // length of the hash key
    rte_jhash,      // hash function
    0,              // initial value of the hash function
    0,              // NUMA Socket ID
    0               // indicate if additional parameters are present
};

static uint32_t key;

void init_processing(void)
{
    srand(time(NULL));
    flow_table = rte_hash_create(&flow_table_params);
    if (flow_table == NULL)
        rte_exit(EXIT_FAILURE, "Could not initialize the flow_table\n");
}

void process_swa(swa_t *swa)
{
    switch(swa->op)
    {
        case 0:
            create_flow(swa);
            break;
        case 1:
            add_value(swa);
            break;
        case 2:
            get_result(swa);
            break;
        case 3:
            remove_flow(swa);
            break;
        default:
            error_unknown_operation(swa);
    }
}

swa_table_entry *init_table_entry(swa_t *swa)
{
    swa_table_entry *ste = rte_zmalloc(NULL, sizeof(swa_table_entry), 0);
    if (ste == NULL)
        error_no_resources(swa);
    else
    {
        ste->window_size = swa->window_size;
        ste->window = rte_zmalloc(NULL, ste->window_size * sizeof(uint32_t), 0);
        if (ste->window == NULL)
        {
            rte_free(ste);
            ste = NULL;
            error_no_resources(swa);
        }
    }
    return ste;
}

void clear_table_entry(swa_table_entry *ste)
{
    rte_free(ste->window);
    rte_free(ste);
}

void print_table_entry(swa_table_entry *ste)
{
    printf("===== SWA TE =====\n");
    printf("Sum : %u\n", ste->window_sum);
    printf("Idx : %u\n", ste->idx);
    printf("Size : %u\n", ste->window_size);
    printf("---- Elements ----\n");
    uint16_t i;
    for (i = 0; i < ste->window_size; ++i)
        printf("  elem [%u] : %u\n", i, ste->window[i]);
    printf("===================\n");
}

void create_flow(swa_t *swa)
{   
    key = (rand() % 0xffff << 16) | (rand() % 0xffff);
    swa->key = key;
    
    swa_table_entry *ste = init_table_entry(swa);
    if (ste == NULL)
        return;
    
    if (rte_hash_add_key_data(flow_table, &key, ste) < 0)
    {
        clear_table_entry(ste);
        error_no_resources(swa);
        return;
    }
    
    success(swa);
}   

void add_value(swa_t *swa)
{   
    key = swa->key;
    swa_table_entry *ste;
    if (rte_hash_lookup_data(flow_table, &key, (void **)&ste) < 0)
    {
        error_unknown_key(swa);
        return;
    }

    ste->window_sum -= ste->window[ste->idx];
    ste->window_sum += swa->value;
    ste->window[ste->idx] = swa->value;
    ste->idx = (ste->idx + 1) % ste->window_size;
    success(swa);
}

void get_result(swa_t *swa)
{
    key = swa->key;
    swa_table_entry *ste;
    if (rte_hash_lookup_data(flow_table, &key, (void **)&ste) < 0)
    {
        error_unknown_key(swa);
        return;
    }

    swa->value = ste->window_sum;
    swa->window_size = ste->window_size;
    success(swa);
}

void remove_flow(swa_t *swa)
{   
    key = swa->key;
    
    swa_table_entry *ste;
    if (rte_hash_lookup_data(flow_table, &key, (void **)&ste) < 0)
    {
        error_unknown_key(swa);
        return;
    }

    clear_table_entry(ste);
    rte_hash_del_key(flow_table, &key);
    success(swa);
}
