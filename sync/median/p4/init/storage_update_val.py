import sys 
sys.path.append("../network")
from simple_switch_api import SSApi

print('Initializing IngressImpl.med.storage.update_val')
with SSApi() as ssapi:
    ssapi.table_add_bulk(
        tname='IngressImpl.med.storage.update_val',
        amp=[
            (
                'IngressImpl.med.storage.update_new_val',
                (i, ),
                (2 ** i, 2 ** (31 - i))    
            ) for i in range(32)
        ]
    )