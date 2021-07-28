from node import ConfHost, ConfDocker, P4SSwitch

import json

def build_topo(topo_path, net):
    """build a topology defined by the given 
    configuration file

    Args:
        topo_path (string): path to the configuration file
        net (Containernet): virtual network based on Containernet
    """
    with open(topo_path) as jtopo:
        topo = json.load(jtopo)
    
    for h in topo['hosts']:
        net.addHost( 
            cls=ConfDocker if h['type'] == 'docker' else ConfHost,
            **h
        )
    
    if topo['controller']:
        net.addController('ctrlr')

    for s in topo['switches']:
        net.addSwitch(
            **s, 
            cls=P4SSwitch if s['type'] == 'p4_simple_switch' else None
        )
    
    for l in topo["links"]:
        net.addLink(**l)