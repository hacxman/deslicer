#!/usr/bin/bash
tar czhvf deslicer-0.0.1.tar.gz deslicer-0.0.1
cp deslicer-0.0.1.tar.gz ~/rpmbuild/SOURCES/deslicer-0.0.1.tar.gz
pushd src
rpmbuild -bs deslicer.spec
popd
mock -r fedora-18-x86_64 --rebuild ~/rpmbuild/SRPMS/deslicer-0.0.1-1.fc18.src.rpm
