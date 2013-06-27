Summary: Deslicer client
Name: deslicer
Version: 0.0.1
Release: 1%{?dist}
Source0: http://konia.rit/%{version}/tarball/%{name}-%{version}.tar.gz
License: ASL 2.0
Group: Applications/System
URL: http://github.com/hacxman/deslicer
BuildArch: noarch
Requires: python
BuildRequires: python-setuptools

%description
jebem ti mater

%package server
Summary: JSON RPC server for running Slic3r as a remote service
Requires: python
Requires: python-daemon
Requires(post): chkconfig
Requires(preun): chkconfig
# This is for /sbin/service
Requires(preun): initscripts
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description server
Client for deslicer

%prep
%setup -q

%build
python setup.py build
python setup-server.py build

#mkdir ${buildroot}/conf
#cp -r conf/* ${buildroot}/conf/

%install

python setup.py install -O1 --root=%{buildroot} --skip-build
python setup-server.py install -O1 --root=%{buildroot} --skip-build

%{__install} -d %{buildroot}/%{_sysconfdir}/deslicer
%{__install} -d %{buildroot}/%{_localstatedir}/lib/deslicer
%{__install} -d %{buildroot}/%{_sysconfdir}/logrotate.d
%{__install} -d %{buildroot}/%{_unitdir}
%{__install} -d %{buildroot}/%{_sysconfdir}/sysconfig

%{__install} -m0600 conf/deslicer %{buildroot}/%{_sysconfdir}/logrotate.d/deslicer
%{__install} -m0600 conf/deslicer.service %{buildroot}/%{_unitdir}/deslicer.service
%{__install} -m0600 conf/sysconfig-deslicerd %{buildroot}/%{_sysconfdir}/sysconfig/deslicer

%post server
useradd deslicer
systemctl enable deslicer

%preun server
if [ $1 = 0 ] ; then
    systemctl stop deslicer >/dev/null 2>&1
    systemctl disable deslicer
fi

%files
%{_bindir}/deslicer
%{python_sitelib}/deslicer
%{python_sitelib}/deslicer-*.egg-info

%files server
#%config(noreplace) %{_sysconfdir}/deslicer.conf
%config(noreplace) %{_sysconfdir}/sysconfig/deslicer
%config(noreplace) %{_sysconfdir}/logrotate.d/deslicer
%{_unitdir}/deslicer.service
# %dir %attr(0755, deslicer, deslicer) %{_sysconfdir}/deslicer
%dir %attr(0755, deslicer, deslicer) %{_localstatedir}/lib/deslicer
%{python_sitelib}/deslicer_server/*.py[c,o]
%{python_sitelib}/deslicer_server/*.py
%{_bindir}/deslicerd
%{python_sitelib}/deslicer_server-*.egg-info

%changelog
* Wed Jun 26 2013 Maros Zatko <zavinac@www.wwwbodkask.sk> - 0.0.1-1
- Initial spec file.
