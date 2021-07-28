import sys 
sys.path.append('../network')
from simple_switch_api import SSApi

print("Initializing IngressImpl.med.storage.processor.mask")
with SSApi() as ssapi:
    v = 2 ** 32 - 1
    ssapi.table_add_bulk(
        tname='IngressImpl.med.storage.processor.mask',
        amp=[
            (
                'IngressImpl.med.storage.processor.process_mask',
                (i, ),
                (v & (v << i + 1), )
            ) for i in range(0, 32)
        ]
    )
