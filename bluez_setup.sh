#!/bin/bash
sudo apt-get autoremove -y bluez
sudo apt-get install -y build-essential libreadline-dev libical-dev libdbus-1-dev libudev-dev libglib2.0-dev python3-docutils
wget http://www.kernel.org/pub/linux/bluetooth/bluez-5.66.tar.xz
tar -xf bluez-*
rm -r bluez-*.tar.xz
cd bluez-*
./configure 
make 
sudo make install
sudo sed -i '/ExecStart=/ s/$/ --experimental/' /lib/systemd/system/bluetooth.service
sudo systemctl daemon-reload
sudo systemctl unmask bluetooth.service
sudo systemctl restart bluetooth
cd ..