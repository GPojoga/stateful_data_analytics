import json

from mininet.net import Containernet
from node import ConfHost, ConfDocker
from mininet.cli import CLI 
from mininet.log import info, setLogLevel
from topo import build_topo

import sys

class Network:
    """Create containernet network from a given
    json file.
    """
    def __init__(self, topo_path):
        """Create the network

        Args:
            topo_path (string): path to the json file
        """
        self.net = Containernet()
        build_topo(topo_path, self.net)

    def start(self):
        """start the network
        """
        self.net.start()
        CLI(self.net)
        self.net.stop()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("Required argument : [network conf. file path]")
    Network(sys.argv[1]).start()
    
