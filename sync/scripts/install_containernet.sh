cd /home/vagrant

git clone https://github.com/containernet/containernet.git

cd containernet/ansible

sed -i 's/ubuntu/debian/g' install.yml

sudo ansible-playbook -i "localhost," -c local install.yml

cd ..

sudo make install