#!/usr/bin/bash
sudo rpm -e deslicer deslicer-server deslicer-server-selinux
sudo rpm -i /var/lib/mock/fedora-18-x86_64/result/deslicer-0.0.1-1.fc18.noarch.rpm
sudo rpm -i /var/lib/mock/fedora-18-x86_64/result/deslicer-server-0.0.1-1.fc18.noarch.rpm
sudo rpm -i /var/lib/mock/fedora-18-x86_64/result/deslicer-server-selinux-0.0.1-1.fc18.noarch.rpm
