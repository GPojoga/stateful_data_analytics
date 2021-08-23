# BSc. Stateful data analytics over programming models of networks

## Installation

---

Make sure that [virtualBox](https://www.virtualbox.org/wiki/Downloads) and [vagrant](https://www.vagrantup.com/downloads) are installed (on the host OS). For developing this project we have used virtualbox 6.1.26, vagrant 2.2.14 and, as a host OS, Debian bullseye. However, it is not required that exactly these versions, or host OS, to be used, since these tools are only used for the creation of a virtual machine where the application is executed. 

Install the vagrant plugin [vagrant-vbguest](https://github.com/dotless-de/vagrant-vbguest). You can do this by running
```
$ vagrant plugin install vagrant-vbguest
```

Now you can build the vagrant box. It will contain all the required dependecies for running the programs. It is a lengthy process. Expect it to take approximately an hour. To build the box run
```
$ vagrant up
```

Once the box is up, you can connect through ssh by running :

```
$ vagrant ssh
```

Once you are in the virtual OS proceed with the following section (Directory Overview).

In order to stop the virtual OS, you must interrupt the ssh connection and run
```
$ vagrant halt
```

## Directory Overview
---
The virtual OS contains a shared folder at `/home/sync`, it is connected to the folder `sync` on the host OS. This folder contains the following directories :
* `docker_basis` : It contains all the information necessary for creating a docker image that contains dpdk-16.11
* `scripts` : This folder contains all the scripts that are necessary for the initialization of the vagrant box
* `network` : This is a collection of python3 methods and classes that are used for the initialization and operation of a virtual network.
* `sliding_window` : This folder contains the dpdk and P4 implementations of the sliding window average. For more details check the section Sliding Window Average.
* `median` : This folder contains the dpdk and P4 implementations of the median. For more details check the section Median.

## Sliding Window Average
---
### Directory Overview

* `dpdk` : Here is located the dpdk implementation of the algorithm. The dockerfile defines the implementation of the docker image, and the `data` folder, which contains the files that implement the algorithm, is copied to the container.
* `host` : It contains the functions to be executed on the client hosts.
* `network` : This folder contains the configuration of the network topologies, the definition of the swa header and some other functions related to the processing of network packets
* `p4` : Here is located the P4 implementation of the algorithm. The P4 program is located in the folder `bmv2` and the table initialization in `init`. The controller is defined in `controller.py`

### Network

* **DPDK** : The dpdk network is described in `sync/sliding_window/network/topo_dpdk.json`. `d1` is a docker container running the dpdk implementation of the algorithm and `h1` is a Containernet host.
* **P4** : The P4 network is described in `sync/sliding_window/network/topo_p4.json`. `d1` and `h1` are Containernet hosts, `hc` acts as a controller, and is in the namespace as the switch. The switch `s1` is a bmv2 simple switch that executes the P4 program defined in 'sync/sliding_window/p4/bmv2'

### Usage

#### **Initialize DPDK**

To initialize the network run `$ make buran_dpdk`. 
Once the network is initialized the Containernet terminal will be waiting for input.
Now you can open a terminal that controls a client host, by running `> xterm h1` in the Containernet CLI.

#### **Initialize P4**
To initialize the network run `$ make buran_p4`. 
Once the network is initialized the Containernet terminal will be waiting for input.
Now you can open a terminal that controls a client host, by running `> xterm h1` in the Containernet CLI.

#### **Client Host operations :**
* **Create a flow** : `$ make create_flow winsize=<the size of the window>`. The response will contain a flow key, which can be used to perform the other operations on the flow.
* **Add a value** : `$ make add_value key=<flow key> val=<the value to be added>`
* **Get result** : `$ make get_result key=<flow key>`
* **Remove flow** : `$ make remove_flow key=<flow key>`

#### **Example**
Run :
```
$ make buran_dpdk
```
In the containernet CLI run :
```
> xterm h1
```
The following communication takes place in the h1 terminal

---

**Request** 
```
$ make create_flow winsize=5
```
**Response**
```
=== SUCCESS ===
OP : 0
ERRNO : 15
KEY : 0x972608fb
VAL : 0
WINSIZE : 5
==========

The flow key is 0x972608fb
```

---

**Request** 
```
$ make add_value key=972608fb val=3
```
**Response**
```
=== SUCCESS ===
OP : 1
ERRNO : 15
KEY : 0x972608fb
VAL : 2
WINSIZE : 0
==========
```

---

**Request** 
```
$ make get_result key=972608fb
```
**Response**
```
=== SUCCESS ===
OP : 2
ERRNO : 15
KEY : 0x972608fb
VAL : 3
WINSIZE : 5
==========

===0x972608fb===
sum : 3
winsize : 5
================
```

---

**Request** 
```
$ make remove_flow key=972608fb
```
**Response**
```
=== SUCCESS ===
OP : 3
ERRNO : 15
KEY : 0x972608fb
VAL : 0
WINSIZE : 0
==========
```

---

## Median
---
### Directory Overview
The file structure is similar to the sliding window average i.e.,
* `dpdk` : Here is located the dpdk implementation of the algorithm. The dockerfile defines the implementation of the docker image, and the `data` folder, which contains the files that implement the algorithm, is copied to the container.
* `host` : It contains the functions to be executed on the client hosts.
* `network` : This folder contains the configuration of the network topologies, the definition of the median header and some other functions related to the processing of network packets
* `p4` : Here is located the P4 implementation of the algorithm. The P4 program is located in the folder `bmv2` and the table initialization in `init`. The controller is defined in `controller.py`

### Usage

#### **Initialize DPDK**

To initialize the network run `$ make buran_dpdk`. 
Once the network is initialized the Containernet terminal will be waiting for input.
Now you can open a terminal that controls a client host, by running `> xterm h1` in the Containernet CLI.

#### **Initialize P4**
To initialize the network run `$ make buran_p4`. 
Once the network is initialized the Containernet terminal will be waiting for input.
Now you can open a terminal that controls a client host, by running `> xterm h1` in the Containernet CLI.

#### **Client Host operations :**
* **Create a flow** : `$ make create_flow vals=<list of values separated by comma>`. The response will contain a flow key, which can be used to perform the other operations on the flow.
* **Add a value** : `$ make add_value key=<flow key> val=<the value to be added>`
* **Get result** : `$ make get_result key=<flow key>`
* **Remove flow** : `$ make remove_flow key=<flow key>`

#### **Example**
Run :
```
$ make buran_p4
```
In the containernet CLI run :
```
> xterm h1
```
The following communication takes place in the h1 terminal

---

**Request** 
```
# make create_flow vals=1,3,4,7
```
**Response**
```
=== SUCCESS ===
OP : 0
ERRNO : 15
KEY : 0xfe5a6222
VAL : 0
WINSIZE : 4
==========
++++++++++
Val : 1
++++++++++
Val : 3
++++++++++
Val : 4
++++++++++
Val : 7
++++++++++
The flow key is 0xfe5a6222
```
---

**Request** 
```
# make add_value key=fe5a6222 val=3
```
**Response**
```
=== SUCCESS ===
OP : 1
ERRNO : 15
KEY : 0xfe5a6222
VAL : 3
WINSIZE : 0
==========
```
---

**Request** 
```
# make get_result key=fe5a6222
```
**Response**
```
=== SUCCESS ===
OP : 2
ERRNO : 15
KEY : 0xfe5a6222
VAL : 3
WINSIZE : 0
==========
The median is 3
```
---

**Request** 
```
# make remove_flow key=fe5a6222
```
**Response**
```
=== SUCCESS ===
OP : 3
ERRNO : 15
KEY : 0xfe5a6222
VAL : 0
WINSIZE : 0
==========
```
---