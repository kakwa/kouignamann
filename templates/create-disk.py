<%
import os
imgdir = os.getenv("IMGDIR", "/var/lib/kvm")

def getSize(devs):
    size = 4096
    for dev in devs:
        size = size + dev['size']
    return str(size)

%>\
#!/bin/sh

echo "Start creation of disks for VM '${host['hostname']}'"

## disks declaration
<%counter=0
id=str(counter)
%>\
%for vg in host['partitioning']['volume-groups']:
<%sizeDisk=getSize(vg['parts'])%>
echo "Creating disk '${imgdir}/${host['hostname']}_${id}.img'"
qemu-img create -f qcow2 -o preallocation=metadata ${imgdir}/${host['hostname']}_${id}.img ${sizeDisk}M || exit 1
<%counter= counter + 1
id=str(counter)
%>\
%endfor

