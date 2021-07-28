cd /home/vagrant

git clone --recursive https://github.com/p4lang/p4c.git

# install dependencies
sudo apt install --assume-yes cmake g++ git automake libtool libgc-dev bison flex \
libfl-dev libgmp-dev libboost-dev libboost-iostreams-dev \
libboost-graph-dev llvm pkg-config python python-scapy python-ipaddr python-ply python3-pip \
tcpdump protobuf-compiler

pip3 install scapy ply

cd p4c

mkdir build
cd build

cmake .. 
make -j4

sudo make install

cd /home/vagrant