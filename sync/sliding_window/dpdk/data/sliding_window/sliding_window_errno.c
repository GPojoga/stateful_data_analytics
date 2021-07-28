
#include "sliding_window_errno.h"

void success(swa_t *swa)
{
    swa->err_no = 0xf;
}

void error_unknown_operation(swa_t *swa)
{
    swa->err_no = 1;
}

void error_unknown_key(swa_t *swa)
{
    swa->err_no = 2;
}

void error_no_resources(swa_t *swa)
{
    swa->err_no = 3;
}