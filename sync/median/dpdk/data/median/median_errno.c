#include "median_errno.h"

void success(medpkt_t *medpkt)
{
    medpkt->med->err_no = MED_SUCCESS;
}

void error_unknown_operation(medpkt_t *medpkt)
{
    medpkt->med->err_no = MED_UNKN_OP;
}

void error_unknown_key(medpkt_t *medpkt)
{
    medpkt->med->err_no = MED_UNKN_KEY;
}

void error_no_resources(medpkt_t *medpkt)
{
    medpkt->med->err_no = MED_NO_RES;
}

void error_unknown_value(medpkt_t *medpkt)
{
    medpkt->med->err_no = MED_UNKN_VAL;
}