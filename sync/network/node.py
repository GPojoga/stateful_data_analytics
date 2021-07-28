
from mininet.node import Host, Docker, Switch
from init_table import init_table

import os
import time 

class ConfHost(Host):
    """A containernet Host that is configured
    using the commands from the specification file

    """
    def config(self, exe, **params):
        Host.config(self, **params)
        self.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        self.cmd(f"{exe}&")

class ConfDocker(Docker):
    """Similar to ConfHost, however, used by Docker hosts

    """
    def config(self, exe, **params):
        Docker.config(self, **params)
        self.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        self.cmd(f"{exe}&")
    
class P4SSwitch(Switch):
    """A mininet switch that runs a 
    P4 simple switch implementation

    """
    def __init__(self, name, sw_path, thrift_port, device_id, init_path=None, **kwargs):
        """initialize the P4 simple switch

        Args:
            name (string): name of the switch
            sw_path (string): path to the compiled p4 program
            thrift_port (int): thrift port used by bmv2 runtime api
            device_id (int): used by bmv2 runtime api
            init_path (string, optional): path to a directory that
            contains json and python3 files used for initialization
            of the tables. Defaults to None.
        """
        self.sw_path = sw_path
        self.thrift_port = thrift_port
        self.device_id = device_id
        self.init_path = init_path
        Switch.__init__(self, name, **kwargs)

    def start(self, controllers):
        """start the P4SSwitch. Should not be called directly.

        Args:
            controllers (Controler): Mininet controllers
        """
        print(f"*** Setting up P4 simple switch {self.name} on"
              f" thrift port {self.thrift_port} ***")
        ss_ifaces = [f"-i {self.ports[p]}@{p.name}" for p in self.ports if p.name != "lo"]
        self.cmd(
            'simple_switch '
            f'--device-id {self.device_id} '
            f'--thrift-port {self.thrift_port} '
            f'{" ".join(ss_ifaces)}'
            f' {self.sw_path} &'
        )
        if self.init_path:
            time.sleep(1)
            self.init_tables()

    def init_tables(self):
        """execute the scripts from the initialization directory

        Raises:
            Exception: the table specified in the json file is unavailable
        """
        for f in os.listdir(self.init_path):
            file = f.split('.')
            if len(file) != 2:
                raise Exception(f"Table init : unknown extension of file {f}")
            if file[1] == 'json':
                init_table(f'{self.init_path}/{f}')
            elif file[1] == 'py':
                os.system(f'python3 {self.init_path}/{f}')
        