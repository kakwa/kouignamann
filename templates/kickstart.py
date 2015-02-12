# Kickstart file for ${host["hostname"]}
<%!
def ipv4_cidr_to_netmask(bits):
    """ Convert CIDR bits to netmask """
    netmask = ''
    for i in range(4):
        if i:
            netmask += '.'
        if bits >= 8:
            netmask += '%d' % (2**8-1)
            bits -= 8
        else:
            netmask += '%d' % (256-2**(8-bits))
            bits = 0
    return netmask

def ipv4_netmask_to_cidr(netmask):
    """ convert netmask to CIDR """
    return map(lambda x: ipv4_cidr_to_netmask(x), range(0,33)).index(netmask)
%>\
text
reboot --eject
skipx
install

# network configuration
%for interface in host['network']['interfaces']:
network --device=${interface['device']} --activate \
--onboot=yes --bootproto=static \
--ip=${interface['ip']} --netmask=${interface['mask']} \
--gateway=${host['network']['default-gateway']} \
--nameserver=${general['dnsip']} \
--hostname=${host['hostname']}.${general['domain']}

%for altdevice in interface['device-alt-names']:
network --device=${altdevice} --activate \
--onboot=yes --bootproto=static \
--ip=${interface['ip']} --netmask=${interface['mask']} \
--gateway=${host['network']['default-gateway']} \
--nameserver=${general['dnsip']} \
--hostname=${host['hostname']}.${general['domain']}

%endfor
%endfor

repo --name=base --baseurl="${general["mirror"]}/centos/7/os/x86_64/"
repo --name=Epel --baseurl="${general["mirror"]}/epel/7/x86_64"
url 		     --url="${general["mirror"]}/centos/7/os/x86_64/"

selinux --disabled
firewall --disabled
eula --agreed

reboot

# UEFI/GPT or bios
%if host['hardware']['bootloader'] == 'mbr': 
bootloader --location=mbr
%elif host['hardware']['bootloader'] == 'uefi': 
part biosboot --fstype=biosboot --size=1
%endif

lang en_US.UTF-8
keyboard us

# need separated /boot/ (not in lvm)
partition /boot --fstype "ext4" --size=512
##part pv.01 --size 1 --grow
##logvol swap	--fstype swap --name=lvSwap		--vgname=OS_VOL --size=2048 #2Go swap
# partitions
<% counter=0%>\
%for vg in host['partitioning']['volume-groups']:
<% counter = counter + 1
index=str(counter)
%>\
part pv.${index} --size 1 --grow --ondisk=${vg['device']}
volgroup ${vg['name']} pv.${index}
%for part in vg['parts']:
logvol ${part['mount-point']} --fstype=ext4 --name=${part['name']} --vgname=${vg['name']} --size=${part['size']} \
%if 'grow' in part and part['grow']:
--grow #partition ${part['mount-point']}
%else:
#partition ${part['mount-point']}
%endif
%endfor
%endfor

##bootloader --location mbr --driveorder sda 
timezone Europe/Paris
authconfig --enableshadow
selinux --disabled
firewall --disabled 

rootpw ${general['rootpwd']}

%%packages --nobase --excludedocs --ignoremissing
coreutils
yum
rpm
e2fsprogs
lvm2
grub
openssh-server
openssh-clients
authconfig
ed
vim
iptables
file
man
wget
%if 'puppetserver' in general:
puppet
%endif

# Useless Packages
-alsa-firmware
-alsa-lib
-alsa-tools-firmware
-audit
-avahi
-avahi-autoipd
-avahi-libs
-atmel-firmware
-b43-openfwwf
-dnsmasq
-glib-networking
-gsettings-desktop-schemas
-ipw2100-firmware
-ipw2200-firmware
-ivtv-firmware
-iwl1000-firmware
-iwl3945-firmware
-iwl4965-firmware
-iwl5000-firmware
-iwl5150-firmware
-iwl6000-firmware
-iwl6050-firmware
-iwl100-firmware
-iwl6000g2a-firmware
-iwl6000g2b-firmware
-iwl*-firmware
-jansson
-ql2100-firmware
-ql2200-firmware
-ql23xx-firmware
-ql2400-firmware
-ql2500-firmware
-libertas-usb8388-firmware
-libsoup
-NetworkManager
-NetworkManager-tui
-NetworkManager-glib
-xorg-x11-drv-ati-firmware
-aic94xx-firmware
-zd1211-firmware
-bfa-firmware
-rt73usb-firmware
-rt61pci-firmware
-teamd
-mariadb-libs
-postfix
-ModemManager-glib
-mozjs17
-polkit
-polkit-pkla-compat
-nettle
-gnutls
-newt
-authconfig
-newt-python
-plymouth
-plymouth-core-libs
-plymouth-scripts
-ppp
-wpa_supplicant
-mysql-libs
-sysstat
-yum-utils
-info
-compiz
-emacs-leim
-emacspeak
-ethereal
-ethereal-gnome
-gnome-games
-isdn4k-utils
-nmap
-octave
-oprofile
-rcs
-tcpdump
-valgrind
-zsh
-avahi
-dhclient
-sendmail
-iptables-ipv6
-subscription-manager
-tuned
%%end

%%pre

# suppress lvm volumes
vgscan |sed -n 's/.*"\(.*\)"/\1/' |while read v; do vgremove -f "$v";done

# gpt or mbr label
%for vg in host['partitioning']['volume-groups']:
<%
if host['hardware']['bootloader'] == 'uefi':
    mode='gpt'
else:
    mode='msdos'
%>\
dd if=/dev/zero of=${vg['device']} bs=512 count=1000
/usr/sbin/parted -s ${vg['device']} mklabel ${mode}
%endfor

#echo 68719476736 >/proc/sys/kernel/shmmax
#echo 4096  >/proc/sys/kernel/shmmni
#echo 4294967296 /proc/sys/kernel/shmall

%%end

%%post --nochroot

mkdir /mnt/sysimage/tmp/ks-tree-copy
if [ -d /oldtmp/ks-tree-shadow ]; then
    cp -fa /oldtmp/ks-tree-shadow/* /mnt/sysimage/tmp/ks-tree-copy
elif [ -d /tmp/ks-tree-shadow ]; then
    cp -fa /tmp/ks-tree-shadow/* /mnt/sysimage/tmp/ks-tree-copy
fi

cp /etc/resolv.conf /mnt/sysimage/etc/resolv.conf
%%end

%%post
(

echo "# disable useless services"
for s in `echo "irda lm_sensors portmap rawdevices rpcidmapd rpcsvcgssd \
 sendmail xinetd ip6tables netfs kudzu rhnsd rhsmcertd netconsole abrtd \
 acpid atd avahi-daemon autofs bluetooth irqbalance kdump mdmonitor \
 nfslock portreserve postfix psacct rdisc restorecond rpcbind rpcgssd \
 sysstat auditd tuned"`
do
/sbin/chkconfig $s off
/usr/bin/systemctl disable $s
done

echo "# Disable ZEROCONF"
echo "NOZEROCONF=yes" >>/etc/sysconfig/network

echo "# Set Default Gateway"
echo "GATEWAY='${host['network']['default-gateway']}'" >>/etc/sysconfig/network 


echo "# Set static routes"
%if 'routes' in host['network']:
%for route in host['network']['routes']:
<% mask=ipv4_netmask_to_cidr(route['mask']) %>\
echo "${route['network']}/${mask} via ${route['gateway']}" >>/etc/sysconfig/static-routes
%endfor
%endif

# clean default rpm repos configuration
find /etc/yum.repos.d/ -type f |while read line; do echo > "$line";done

# configure rpm repos (CentOS and Epel
cat >/etc/yum.repos.d/CentOS.repo <<EOF
[base]
name=CentOS-\$releasever - Base
baseurl=${general["mirror"]}/centos/\$releasever/os/\$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-\$releasever
[updates]
name=CentOS-\$releasever - Updates
baseurl=${general["mirror"]}/centos/\$releasever/updates/\$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-\$releasever
EOF

cat >/etc/yum.repos.d/Epel.repo <<EOF
[Epel]
name=Extra Packages for Enterprise Linux \$releasever - \$basearch
baseurl=${general["mirror"]}/epel/\$releasever/\$basearch
gpgcheck=0
EOF

%if 'puppetserver' in general:

echo "# Puppet Client Configuration"
# configure puppet client
cat >/etc/puppet/puppet.conf <<EOF
[main]
logdir=/var/log/puppet
vardir=/var/lib/puppet
ssldir=/var/lib/puppet/ssl
rundir=/var/run/puppet
factpath=$vardir/lib/facter

[agent]
server      = ${general['puppetserver']}
certname    = ${host['hostname']}.${general['domain']}
environment = ${host['environment']}
pluginsync  = true
runinterval = 600
EOF


# enable puppet
chkconfig puppet on
/usr/bin/systemctl enable puppet
%endif
) >/root/post.log 2>&1

%%end
