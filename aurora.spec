# This spec requires python 2.7. Currently, we're depending on a custom
# python27 rpm that installs to /usr/python2.7. Change the spec accordingly
# for your environment. You'll also need the mesos python egg (tested against
# version 0.18.0).
#
# To build:
#
# This spec is intended for use with tito/mock, but can be adapted for the
# typical rpm build process. Instructions are for tito/mock, with the
# assumption you are building on a machine with tito and mock installed.
#
# 1) Create your repo for tito, copying the contents of incubator-aurora repo
# to SOURCES/aurora. Be sure to use or track the correct branch you want to
# deploy.
#
# 2) Copy this spec file into the SOURCES/aurora folder.
#
# 3) Ensure that the mesos python egg (tested against 0.18.0) is available
# from your local pypi and setting the appropriate variable in pants.ini
# OR do a horrible hack by copying the egg into the repo as follows:
#
#    cp mesos-0.18.0-py2.7-linux-x86_64.egg SOURCES/aurora/.pants.d/python/eggs/
#
# 4) Push to remote.
#
# 5) Clone the repo onto the machine that has tito/mock and cd SOURCES/aurora
#
# 6) run 'tito tag'
#
# 7) mkdir ~/tmp/tito; tito build --srpm -o ~/tmp/tito
#    Check the output to find the correct src.rpm to use in the next step.
#
# 8) mock -vr centos6 ~/tmp/tito/aurora-0.5.0-1.el6.rc0.src.rpm
#    Use an architecture of your choosing. Tested on SL and Centos.

%define install_base /opt

Name:      aurora
Version:   0.5.0
Release:   1%{?dist}.rc0
Summary:   A framework for scheduling long-running services against Apache Mesos
License:   ASL 2.0
URL:       http://%{name}.incubator.apache.org/
Source0:   aurora-0.5.0.tar.gz
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-%(%{__id_u} -n)
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: java-1.7.0-openjdk
BuildRequires: java-1.7.0-openjdk-devel
BuildRequires: mesos
BuildRequires: python27-devel
BuildRequires: python27-setuptools
BuildRequires: tar
BuildRequires: unzip
BuildRequires: which
BuildRequires: zip

%description
Apache Aurora is a service scheduler that runs on top of Mesos, enabling you
to schedule long-running services that take advantage of Mesos\' scalability,
fault-tolerance, and resource isolation.

%package client
Summary: Client tools for interacting with the scheduler.
Group: Development/Tools

%description client
Provides aurora_admin and aurora_client binaries.

%package scheduler
Summary: The master scheduler portion of Aurora.
Group: Applications/System
Requires: java-1.7.0-openjdk
Requires: java-1.7.0-openjdk-devel
Requires: mesos
Requires: mesos-python
Requires: python27

%description scheduler
Apache Aurora is a service scheduler that runs on top of Mesos, enabling you
to schedule long-running services that take advantage of Mesos\' scalability,
fault-tolerance, and resource isolation.

%package thermos
Summary: A simple Pythonic process management framework for Mesos chroots
Group: Applications/System
Requires: mesos
Requires: mesos-python
Requires: python27

%description thermos
Thermos a simple process management framework used for orchestrating
dependent processes within a single Mesos chroot.

%prep
%setup -q

%build
# Add custom python2.7 to path.
export PATH=/usr/python2.7/bin:$PATH
export JAVA_HOME=/usr

# The main aurora distribution.
./gradlew distZip

# Client binaries.
./pants build -i 'CPython>=2.7.0' src/main/python/apache/aurora/client/bin:aurora_admin
./pants build -i 'CPython>=2.7.0' src/main/python/apache/aurora/client/bin:aurora_client

# Executors/observers.
./pants build -i 'CPython>=2.7.0' src/main/python/apache/aurora/executor/bin:gc_executor
./pants build -i 'CPython>=2.7.0' src/main/python/apache/aurora/executor/bin:thermos_executor
./pants build -i 'CPython>=2.7.0' src/main/python/apache/aurora/executor/bin:thermos_runner
./pants build -i 'CPython>=2.7.0' src/main/python/apache/thermos/observer/bin:thermos_observer

# Package thermos runner within the observer.
python <<EOF
import contextlib
import zipfile
with contextlib.closing(zipfile.ZipFile('dist/thermos_executor.pex', 'a')) as zf:
  zf.writestr('apache/aurora/executor/resources/__init__.py', '')
  zf.write('dist/thermos_runner.pex', 'apache/aurora/executor/resources/thermos_runner.pex')
EOF

%install
rm -rf %{buildroot}
%define _prefix %{install_base}/aurora

install -d -m 755 %{buildroot}%{_prefix}

unzip dist/distributions/aurora-scheduler-*.zip -d .
mv    aurora-scheduler-*/bin %{buildroot}%{_prefix}/
mv    aurora-scheduler-*/lib %{buildroot}%{_prefix}/

install    -m 755 dist/aurora_admin.pex  %{buildroot}%{_bindir}/aurora_admin
install    -m 755 dist/aurora_client.pex %{buildroot}%{_bindir}/aurora_client

%define _prefix %{install_base}/thermos
install -d -m 755 %{buildroot}%{_bindir}
install    -m 755 dist/gc_executor.pex       %{buildroot}%{_bindir}/gc_executor
install    -m 755 dist/thermos_executor.pex  %{buildroot}%{_bindir}/thermos_executor
install    -m 755 dist/thermos_runner.pex    %{buildroot}%{_bindir}/thermos_runner
install    -m 755 dist/thermos_observer.pex  %{buildroot}%{_bindir}/thermos_observer

%clean
rm -rf %{buildroot}

%files client
%defattr(-,root,root,-)
%define _prefix %{install_base}/aurora
%{_bindir}/aurora_admin
%{_bindir}/aurora_client

%files scheduler
%defattr(-,root,root,-)
%define _prefix %{install_base}/aurora
%{_bindir}/aurora-scheduler
%{_bindir}/aurora-scheduler.bat
%{_prefix}/lib/*

%files thermos
%defattr(-,root,root,-)
%define _prefix %{install_base}/thermos
%{_bindir}/gc_executor
%{_bindir}/thermos_executor
%{_bindir}/thermos_runner
%{_bindir}/thermos_observer
