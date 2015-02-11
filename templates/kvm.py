<%
import uuid
import os
import random
imgdir = os.getenv("IMGDIR", "/var/lib/kvm")
slot=1

global diskLetter
diskLetter='a'

# increment disk letter
def nextDiskLetter():
    global diskLetter
    diskLetter = chr(ord(diskLetter) + 1)

# init mac calculation 
# Fixed OUI
# random NIC specific first 2 bytes (but common to all interfaces)
# random last byte, incremented for each interface
# this methods limits the number of interfaces to 128
def randomMacInit():
    global lastMac
    global baseMac
    lastMac=random.randint(0x00, 0xef)
    baseMac = [ 0x52, 0x54, 0x00,
            random.randint(0x00, 0x7f),
            random.randint(0x00, 0xff) ]

# get a semi-random mac address
def getMac():
    global lastMac
    global baseMac
    mac = list(baseMac)
    mac.append(lastMac)
    lastMac = lastMac + 1
    return ':'.join(map(lambda x: "%02x" % x, mac))

randomMacInit()

%>\
<domain type='kvm'>
  <name>${host['hostname']}</name>
  <% uuid=uuid.uuid1() %>\
  <uuid>${uuid}</uuid>
  <% memory=str(host['hardware']['ram'] * 1024) %>\
  <memory unit='KiB'>${memory}</memory>
  <currentMemory unit='KiB'>${memory}</currentMemory>
  <% cpus=str(host['hardware']['cpus']) %>\
  <vcpu placement='static'>${cpus}</vcpu>
  <os>
    <type arch='x86_64' machine='pc-i440fx-rhel7.0.0'>hvm</type>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
    <pae/>
  </features>
  <clock offset='utc'/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>restart</on_crash>
  <devices>
    <emulator>/usr/libexec/qemu-kvm</emulator>

## disks declaration
<%counter=0
id=str(counter)
%>\
%for vg in host['partitioning']['volume-groups']:
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2' cache='none'/>
      <source file='${imgdir}/${host['hostname']}_${id}.img'/>
      <target dev='sd${diskLetter}' bus='scsi'/>
      <address type='drive' controller='0' bus='${id}' target='0' unit='0'/>
    </disk>
<%counter= counter + 1
id=str(counter)
nextDiskLetter()
%>\
%endfor

    <disk type='block' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <target dev='hd${diskLetter}' bus='ide'/>
      <readonly/>
      <address type='drive' controller='0' bus='${id}' target='0' unit='0'/>
    </disk>
    <controller type='scsi' index='0' model='virtio-scsi'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x06' function='0x0'/>
    </controller>
    <controller type='usb' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x2'/>
    </controller>
    <controller type='pci' index='0' model='pci-root'/>
    <controller type='ide' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
    </controller>
    <controller type='virtio-serial' index='0'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x07' function='0x0'/>
    </controller>

## Interface declaration
<% counter=0 %>
%for interface in host['network']['interfaces']:
<% mac=getMac()
slot="%02x" % counter
counter = counter + 1%>\
    <interface type='network'>
      <mac address='${mac}'/>
      <source network='${interface['type']}'/>
      <model type='e1000'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x${slot}' function='0x3'/>
    </interface>
%endfor

    <serial type='pty'>
      <target port='0'/>
    </serial>
    <console type='pty'>
      <target type='serial' port='0'/>
    </console>
    <channel type='spicevmc'>
      <target type='virtio' name='com.redhat.spice.0'/>
      <address type='virtio-serial' controller='0' bus='0' port='1'/>
    </channel>
    <input type='mouse' bus='ps2'/>
    <graphics type='spice' autoport='yes'/>
    <video>
      <model type='qxl' ram='65536' vram='65536' heads='1'/>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
    </video>
    <memballoon model='virtio'>
      <address type='pci' domain='0x0000' bus='0x00' slot='0x08' function='0x0'/>
    </memballoon>
  </devices>
</domain>

