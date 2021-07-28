#include <stdlib.h>
#include <math.h>

#include <rte_hash.h>
#include <rte_jhash.h>
#include <rte_malloc.h>

#include "median.h"
#include "median_errno.h"

// a hash table storing all the pairs flow key <-> median table entry
static struct rte_hash *flow_table;

struct rte_hash_parameters flow_table_params =  {
    .entries=1024,           // number of entries
    .reserved=0,              // unused field
    .key_len=32,             // length of the hash key
    .hash_func=rte_jhash,      // hash function
    .hash_func_init_val=0,              // initial value of the hash function
    .socket_id=0,              // NUMA Socket ID
    .extra_flag=0               // indicate if additional parameters are present
};

// skeleton used for the creation of value index mapping hash table
struct rte_hash_parameters mte_table_params =  {
    "",             // hash table name
    32,             // number of entries
    0,              // unused field
    32,             // length of the hash key
    rte_jhash,      // hash function
    0,              // initial value of the hash function
    0,              // NUMA Socket ID
    0               // indicate if additional parameters are present
};

static uint32_t key; // used for adding/retrieving values from hash tables

void init_processing(void)
{
    srand(time(NULL));
    flow_table = rte_hash_create(&flow_table_params);
    if (flow_table == NULL)
        rte_exit(EXIT_FAILURE, "Could not initialize the flow_table\n");
}

mte_t *init_mte(medpkt_t *medpkt)
{   
    mte_t *mte = rte_zmalloc(NULL, sizeof(mte_t), 0);
    if (mte == NULL)
        return NULL;
    mte->frame_size = medpkt->med->nrvals;
    mte->params = mte_table_params;
    mte->params.name = rte_malloc(NULL, 32, 0);

    #pragma GCC diagnostic ignored "-Wcast-qual"
    sprintf((char *)mte->params.name, "%u", (rand() % 0xffff << 16) | (rand() % 0xffff));

    mte->val_idx = rte_hash_create(&mte->params);
    
    if (mte->val_idx == NULL)
    {
        rte_free(mte);
        return NULL;
    }
    mte->frame = init_frame(medpkt);
    if (mte->frame == NULL)
    {   
        rte_hash_free(mte->val_idx);
        rte_free(mte);
        return NULL;
    }
    int i;
    for (i = 0; i < mte->frame_size; ++i)
    {   
        mte->frame[i].index = i;
        key = mte->frame[i].val;
        if (rte_hash_add_key_data(mte->val_idx, &key, &mte->frame[i].index) < 0)
        {
            clean_mte(mte);
            error_no_resources(medpkt);
            return NULL;
        }
    }

    return mte;
}

int compare_frames(const void *a, const void *b)
{
     const felem *fa = (const felem *)a;
     const felem *fb = (const felem *)b;

     if ( fa->val == fb->val ) return 0;
     else if ( fa->val < fb->val ) return -1;
     else return 1;
}

felem *init_frame(medpkt_t *medpkt)
{   
    felem *frame = rte_zmalloc(NULL, medpkt->med->nrvals * sizeof(felem), 0);
    if (frame == NULL)
        return NULL;

    int i;
    for (i = 0; i < medpkt->med->nrvals; ++i)
        frame[i].val = medpkt->vals[i];
    
    qsort(frame, medpkt->med->nrvals, sizeof(felem), compare_frames);

    return frame;
}

void clean_mte(mte_t *mte)
{   
    #pragma GCC diagnostic ignored "-Wcast-qual"
    rte_free((char *)mte->params.name);
    rte_free(mte->frame);
    rte_hash_free(mte->val_idx);
    rte_free(mte);
}

void print_frame(felem *frame, uint16_t size)
{   
    printf("++++++++++++\n");
    int i;
    for (i = 0; i < size; ++i)
    {
        printf("Val : %u\n", frame[i].val);
        printf("Left dst : %u\n", frame[i].left_dst);
        printf("Right dst : %u\n", frame[i].right_dst);
        printf("Nr vals : %u\n", frame[i].nr_vals);
        printf("++++++++++++\n");
    }
}

void print_mte(mte_t *mte)
{
    printf("=== MTE ===\n");
    printf("Bitmap : %x\n", mte->bitmap);
    printf("Reversed Bitmap : %x\n", mte->rev_bitmap);
    printf("Idx : %u\n", mte->idx);
    printf("Frame size : %u\n", mte->frame_size);
    print_frame(mte->frame, mte->frame_size);
    printf("===========\n");
}

void process_medpkt(medpkt_t *medpkt)
{
    switch(medpkt->med->op)
    {
        case MED_CREATE:
            create_flow(medpkt);
            break;
        case MED_ADD:
            add_value(medpkt);
            break;
        case MED_GET:
            get_result(medpkt);
            break;
        case MED_REMOVE:
            remove_flow(medpkt);
            break;
        default:
            error_unknown_operation(medpkt);
    }
}

void create_flow(medpkt_t *medpkt)
{   
    mte_t *mte = init_mte(medpkt);
    if (mte == NULL)
    {
        error_no_resources(medpkt);
        return;
    }

    key = (rand() % 0xffff << 16) | (rand() % 0xffff);
    medpkt->med->key = key;

    if (rte_hash_add_key_data(flow_table, &key, mte) < 0)
    {
        clean_mte(mte);
        error_no_resources(medpkt);
        return;
    }
    success(medpkt);
}

void add_value(medpkt_t *medpkt)
{
    key = medpkt->med->key;
    mte_t *mte;

    if (rte_hash_lookup_data(flow_table, &key, (void **)&mte) < 0)
    {
        error_unknown_key(medpkt);
        return;
    }
    key = medpkt->med->value;
    uint16_t *index;
    if (rte_hash_lookup_data(mte->val_idx, &key, (void **)&index) < 0)
    {
        error_unknown_value(medpkt);
        return;
    }

    if (mte->bitmap == 0) // first value received
        mte->idx = *index;

    uint32_t val = medpkt->med->value;
    felem *median = &mte->frame[mte->idx];

    update_new_value(mte, *index);

    if (val == median->val)
    {
        median->left_dst += 1;
        median->right_dst += 1;
    } 
    else if (val < median->val)
    {   
        if (median->left_dst == 1)
        {
            move_left(mte);
        }
        else
        {
            median->left_dst -= 1;
            median->right_dst += 1;
        }
    }
    else if (val > median->val)
    {   
        if (median->right_dst == 0)
        {
            move_right(mte);
        }
        else
        {
            median->left_dst += 1;
            median->right_dst -= 1;
        }
    }

    success(medpkt);
}

void get_result(medpkt_t *medpkt)
{
    key = medpkt->med->key;
    mte_t *mte;

    if (rte_hash_lookup_data(flow_table, &key, (void **)&mte) < 0)
    {
        error_unknown_key(medpkt);
        return;
    }

    medpkt->med->value = mte->frame[mte->idx].val;

    success(medpkt);
}

void remove_flow(medpkt_t *medpkt)
{
    key = medpkt->med->key;
    mte_t *mte;

    if (rte_hash_lookup_data(flow_table, &key, (void **)&mte) < 0)
    {
        error_unknown_key(medpkt);
        return;
    }

    clean_mte(mte);
    rte_hash_del_key(flow_table, &key);
    success(medpkt);
}

void update_new_value(mte_t *mte, uint16_t index)
{
    mte->frame[index].nr_vals += 2;
    mte->bitmap |= 1 << index;
    mte->rev_bitmap |= 1 << (mte->frame_size - 1 - index);
}

void move_right(mte_t *mte)
{   
    uint16_t cidx = mte->idx;
    uint32_t bitmap = mte->bitmap;
    bitmap = (bitmap >> (cidx + 1)) << (cidx + 1); // clear the bits to the left
    mte->idx = (uint16_t)log2(bitmap & ~(bitmap - 1));
    felem *median = &mte->frame[mte->idx];
    median->left_dst = 1;
    median->right_dst = median->nr_vals - 1;
}

void move_left(mte_t *mte)
{
    uint16_t rev_cidx = mte->frame_size - 1 - mte->idx;
    uint32_t rev_bitmap = mte->rev_bitmap;
    rev_bitmap = (rev_bitmap >> (rev_cidx + 1)) << (rev_cidx + 1);
    mte->idx = mte->frame_size - 1 - (uint16_t)log2(rev_bitmap & ~(rev_bitmap - 1));
    felem *median = &mte->frame[mte->idx];
    median->left_dst = median->nr_vals;
    median->right_dst = 0;
}
