import json
import os
from simple_switch_api import SSApi

def init_table(path):
    """initialize a simple switch table from a json file

    Args:
        path (string): path to the configuration file
    """
    with open(path) as f:
        data = json.load(f)

    table = f"{data['control']}.{data['table_name']}"

    print(f'Initializing {table}')

    with SSApi() as ssapi:
        ssapi.table_add_bulk(table, [
            (
                f"{data['control']}.{e['action']}",
                e['match'],
                e['params']
            ) for e in data['entries']
        ])

