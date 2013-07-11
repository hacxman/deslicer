#!/usr/bin/bash
V=$(cat VERSION)
if [ $# -eq 1 ] ; then
  echo Changing version from $V to $1
  sed -i "s/^Version:\ *\([A-Za-z0-9\.-]*\)\ *$/Version: $1/" src/deslicer.spec
  rm deslicer-$V
  V=$1
  echo $1 > VERSION
  ln -s src deslicer-$V
fi
tar czhvf deslicer-$V.tar.gz deslicer-$V
cp deslicer-$V.tar.gz ~/rpmbuild/SOURCES/deslicer-$V.tar.gz
pushd src
rpmbuild -bs deslicer.spec
popd
mock -r fedora-19-x86_64 --rebuild ~/rpmbuild/SRPMS/deslicer-$V-1.fc19.src.rpm
cp /var/lib/mock/fedora-19-x86_64/result/*.rpm rpm/
