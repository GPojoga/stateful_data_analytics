import sys 
sys.path.append('../network')
from simple_switch_api import SSApi

print('Initializing IngressImpl.med.storage.processor.log2')
with SSApi() as ssapi:
    ssapi.table_add_bulk(
        tname='IngressImpl.med.storage.processor.log2',
        amp=[
            (
                'IngressImpl.med.storage.processor.process_log2',
                (2 ** i, ),
                (i, ) 
            ) for i in range(32)
        ]
    )
