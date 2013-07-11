#!/usr/bin/bash
#sudo rpm -e deslicer deslicer-server deslicer-server-selinux
V=$(cat VERSION)
sudo rpm -U --force rpm/deslicer-$V-1.fc19.noarch.rpm
sudo rpm -U --force rpm/deslicer-server-$V-1.fc19.noarch.rpm
sudo rpm -U --force rpm/deslicer-server-selinux-$V-1.fc19.noarch.rpm
sudo rpm -U --force rpm/deslicer-utils-$V-1.fc19.noarch.rpm
