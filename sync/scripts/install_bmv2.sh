cd /home/vagrant

git clone https://github.com/p4lang/behavioral-model.git

cd behavioral-model

./install_deps.sh

./autogen.sh
./configure
make -j4
sudo make install
sudo ldconfig

cd /home/vagrant