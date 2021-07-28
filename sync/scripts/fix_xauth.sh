sudo touch /root/.Xauthority

echo '
var=$DISPLAY
tmp=${var##*:}
id=${tmp%%.*}
sudo xauth add $(xauth list | grep "buster/unix:$id")
' >> /home/vagrant/.bashrc