%global _hardened_build 1

Name:    bluez
Summary: Bluetooth utilities
Version: 5.39
Release: 1%{?dist}
License: GPLv2+
Group: Applications/System
URL: http://www.bluez.org/

Source0: http://www.kernel.org/pub/linux/bluetooth/bluez-%{version}.tar.gz

BuildRequires: dbus-devel >= 1.6
BuildRequires: glib2-devel
BuildRequires: libical-devel
BuildRequires: readline-devel
BuildRequires: libtool
# For cable pairing
BuildRequires: systemd-devel
# For cups
BuildRequires: cups-devel

Requires: dbus >= 1.6

Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

# Dropped in Fedora 20:
Obsoletes: bluez-alsa < 5.0
Obsoletes: bluez-compat < 5.0
Obsoletes: bluez-gstreamer < 5.0

# Other bluetooth-releated packages that haven't gotten ported to BlueZ 5
Obsoletes: blueman < 1.23-9
Obsoletes: blueman-nautilus < 1.23-9
Obsoletes: obex-data-server < 1:0.4.6-8

%description
Utilities for use in Bluetooth applications:
	- hcitool
	- hciattach
	- hciconfig
	- bluetoothd
	- l2ping
	- rfcomm
	- sdptool
	- bccmd
	- bluetoothctl
	- btmon
	- hcidump
	- l2test
	- rctest
	- gatttool
	- start scripts (Red Hat)
	- pcmcia configuration files

The BLUETOOTH trademarks are owned by Bluetooth SIG, Inc., U.S.A.

%package libs
Summary: Libraries for use in Bluetooth applications
Group: System Environment/Libraries

%package libs-devel
Summary: Development libraries for Bluetooth applications
Group: Development/Libraries
Requires: bluez-libs%{?_isa} = %{version}-%{release}

%package cups
Summary: CUPS printer backend for Bluetooth printers
Group: System Environment/Daemons
Requires: bluez%{?_isa} = %{version}-%{release}
Requires: cups

%package hid2hci
Summary: Put HID proxying bluetooth HCI's into HCI mode
Group: System Environment/Daemons
Requires: bluez%{?_isa} = %{version}-%{release}

%description cups
This package contains the CUPS backend

%description libs
Libraries for use in Bluetooth applications.

%description libs-devel
bluez-libs-devel contains development libraries and headers for
use in Bluetooth applications.

%description hid2hci
Most allinone PC's and bluetooth keyboard / mouse sets which include a
bluetooth dongle, ship with a so called HID proxying bluetooth HCI.
The HID proxying makes the keyboard / mouse show up as regular USB HID
devices (after connecting using the connect button on the device + keyboard),
which makes them work without requiring any manual configuration.

The bluez-hid2hci package contains the hid2hci utility and udev rules to
automatically switch supported Bluetooth devices into regular HCI mode.

Install this package if you want to use the bluetooth function of the HCI
with other bluetooth devices like for example a mobile phone.

Note that after installing this package you will first need to pair your
bluetooth keyboard and mouse with the bluetooth adapter before you can use
them again. Since you cannot use your bluetooth keyboard and mouse until
they are paired, this will require the use of a regular (wired) USB keyboard
and mouse.

%prep
%setup -q

%build
./bootstrap
%configure --enable-cups --enable-tools --enable-library \
           --enable-sixaxis \
           --with-systemdsystemunitdir=%{_unitdir} \
           --with-systemduserunitdir=%{_userunitdir} \
           --enable-experimental

make %{?_smp_mflags} V=1

%install
make install DESTDIR=$RPM_BUILD_ROOT

# "make install" fails to install gatttool, necessary for Bluetooth Low Energy
# Red Hat Bugzilla bug #1141909
# Debian bug #720486
install -m0755 attrib/gatttool $RPM_BUILD_ROOT%{_bindir}

# Remove autocrap and libtool droppings
find $RPM_BUILD_ROOT -name '*.la' -delete

# Remove the cups backend from libdir, and install it in /usr/lib whatever the install
if test -d ${RPM_BUILD_ROOT}/usr/lib64/cups ; then
	install -D -m0755 ${RPM_BUILD_ROOT}/usr/lib64/cups/backend/bluetooth ${RPM_BUILD_ROOT}%_cups_serverbin/backend/bluetooth
	rm -rf ${RPM_BUILD_ROOT}%{_libdir}/cups
fi

rm -f ${RPM_BUILD_ROOT}/%{_sysconfdir}/udev/*.rules ${RPM_BUILD_ROOT}/usr/lib/udev/rules.d/*.rules
install -D -p -m0644 tools/hid2hci.rules ${RPM_BUILD_ROOT}/lib/udev/rules.d/97-hid2hci.rules

install -d -m0755 $RPM_BUILD_ROOT/%{_localstatedir}/lib/bluetooth

mkdir -p $RPM_BUILD_ROOT/%{_libdir}/bluetooth/

rm -rf ${RPM_BUILD_ROOT}/.git
rm -f ${RPM_BUILD_ROOT}/.gitignore

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%post
%systemd_post bluetooth.service

%preun
%systemd_preun bluetooth.service

%postun
%systemd_postun_with_restart bluetooth.service

%post hid2hci
/sbin/udevadm trigger --subsystem-match=usb

%files
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc AUTHORS ChangeLog
%{_bindir}/ciptool
%{_bindir}/hcitool
%{_bindir}/l2ping
%{_bindir}/rfcomm
%{_bindir}/sdptool
%{_bindir}/bccmd
%{_bindir}/bluetoothctl
%{_bindir}/bluemoon
%{_bindir}/btmon
%{_bindir}/hciattach
%{_bindir}/hciconfig
%{_bindir}/hcidump
%{_bindir}/l2test
%{_bindir}/hex2hcd
%{_bindir}/mpris-proxy
%{_bindir}/gatttool
%{_bindir}/rctest
%exclude %{_bindir}/btattach
%{_mandir}/man1/ciptool.1.gz
%{_mandir}/man1/hcitool.1.gz
%{_mandir}/man1/rfcomm.1.gz
%{_mandir}/man1/sdptool.1.gz
%{_mandir}/man1/bccmd.1.*
%{_mandir}/man1/hciattach.1.*
%{_mandir}/man1/hciconfig.1.*
%{_mandir}/man1/hcidump.1.*
%{_mandir}/man1/l2ping.1.*
%{_mandir}/man1/rctest.1.*
%{_mandir}/man8/*
%{_libexecdir}/bluetooth/bluetoothd
%{_libexecdir}/bluetooth/obexd
%exclude %{_mandir}/man1/hid2hci.1*
%exclude %{_mandir}/man1/btattach.1.gz
%config %{_sysconfdir}/dbus-1/system.d/bluetooth.conf
%{_libdir}/bluetooth/
%{_localstatedir}/lib/bluetooth
%{_datadir}/dbus-1/system-services/org.bluez.service
%{_datadir}/dbus-1/services/org.bluez.obex.service
%{_unitdir}/bluetooth.service
%{_userunitdir}/obex.service

%files libs
%{!?_licensedir:%global license %%doc}
%license COPYING
%{_libdir}/libbluetooth.so.*

%files libs-devel
%{_libdir}/libbluetooth.so
%dir %{_includedir}/bluetooth
%{_includedir}/bluetooth/*
%{_libdir}/pkgconfig/bluez.pc

%files cups
%_cups_serverbin/backend/bluetooth

%files hid2hci
/usr/lib/udev/hid2hci
%{_mandir}/man1/hid2hci.1*
/lib/udev/rules.d/97-hid2hci.rules
