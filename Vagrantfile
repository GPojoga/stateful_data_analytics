
Vagrant.configure("2") do |config|

  # Box Settings
  config.vm.box = "debian/buster64"

  # Provider Settings
  config.vm.provider "virtualbox" do |vb|
    vb.name = 'sda_p4_dpdk'
    vb.memory = 8192
    vb.cpus = 4
  end

  # Network Settings
  config.vm.network :forwarded_port, guest: 22, host: 8822, id: 'ssh'

  # Folder Settings
  config.vm.synced_folder "sync", "/home/sync"

  # Provision Settings
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get --assume-yes -y -qq install docker.io build-essential automake libpcap-dev xauth ansible python-pip python3-pip
    pip3 install scapy

    source /home/sync/scripts/fix_xauth.sh    
  
    source /home/sync/scripts/install_containernet.sh

    docker pull ubuntu:trusty

    docker build -t basis /home/sync/docker_basis

    source /home/sync/scripts/install_p4c.sh
    
    source /home/sync/scripts/install_bmv2.sh

  SHELL

  config.vm.provision "shell", run:"always", inline: <<-SHELL
    source /home/sync/scripts/set_huge_pages.sh 
  SHELL
end
