default vesamenu.c32
menu clear
menu background splash.png
menu title CentOS 7 Auto Installation
menu rows 18
# Border Area
menu color border * #00000000 #00000000 none
# Selected item
menu color sel 0 #ffffffff #00000000 none
# Title bar
menu color title 0 #ff7ba3d0 #00000000 none
# Press [Tab] message
menu color tabmsg 0 #ff3a6496 #00000000 none
# Unselected menu item
menu color unsel 0 #84b8ffff #00000000 none
# Selected hotkey
menu color hotsel 0 #84b8ffff #00000000 none
# Unselected hotkey
menu color hotkey 0 #ffffffff #00000000 none
# Help text
menu color help 0 #ffffffff #00000000 none
# A scrollbar of some type? Not sure.
menu color scrollbar 0 #ffffffff #ff355594 none
menu tabmsg Press Tab for full configuration options on menu items.

%for host in sorted(hosts):
label ${hosts[host]['hostname']}
  menu label Install CentOS 7 with ${hosts[host]['hostname']}.ks
  kernel vmlinuz
  append initrd=initrd.img inst.ks=cdrom:/${hosts[host]['hostname']}.ks \
 inst.repo=${general['mirror']}/centos/7/os/x86_64/ loglevel=debug debug=1

%endfor

label local
  menu label Boot from ^local drive
  localboot 0xffff

