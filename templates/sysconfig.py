default vesamenu.c32
timout 600

##display boot.msg
##
### Clear the screen when exiting the menu, instead of leaving the menu displayed.
### For vesamenu, this means the graphical background is still displayed without
### the menu itself for as long as the screen remains in graphics mode.
##menu clear
##menu background splash.png
##menu title CentOS 7
##menu vshift 8
##menu rows 80
##menu margin 8
###menu hidden
##menu helpmsgrow 15
##menu tabmsgrow 13
##
### Border Area
##menu color border * #00000000 #00000000 none
##
### Selected item
##menu color sel 0 #ffffffff #00000000 none
##
### Title bar
##menu color title 0 #ff7ba3d0 #00000000 none
##
### Press [Tab] message
##menu color tabmsg 0 #ff3a6496 #00000000 none
##
### Unselected menu item
##menu color unsel 0 #84b8ffff #00000000 none
##
### Selected hotkey
##menu color hotsel 0 #84b8ffff #00000000 none
##
### Unselected hotkey
##menu color hotkey 0 #ffffffff #00000000 none
##
### Help text
##menu color help 0 #ffffffff #00000000 none
##
### A scrollbar of some type? Not sure.
##menu color scrollbar 0 #ffffffff #ff355594 none
##
### Timeout msg
##menu color timeout 0 #ffffffff #00000000 none
##menu color timeout_msg 0 #ffffffff #00000000 none
##
### Command prompt text
##menu color cmdmark 0 #84b8ffff #00000000 none
##menu color cmdline 0 #ffffffff #00000000 none
##
### Do not display the actual menu unless the user presses a key. All that is displayed is a timeout message.
##
menu tabmsg Press Tab for full configuration options on menu items.
##
##menu separator # insert an empty line
##menu separator # insert an empty line

%for host in hosts:
label ${hosts[host]['hostname']}
  menu label Install CentOS 7 with ${hosts[host]['hostname']}.ks
  kernel vmlinuz
  append initrd=initrd.img inst.stage2=hd:LABEL=CentOS\x207\x20x86_64 \
 nomodeset ks=ks=cdrom:/${hosts[host]['hostname']}.ks \
 repo=${general['mirror']}/centos/7/os/x86_64/ loglevel=debug debug=1

%endfor

##label linux
##  menu label ^Install CentOS 7
##  kernel vmlinuz
##  append initrd=initrd.img inst.stage2=hd:LABEL=CentOS\x207\x20x86_64 quiet
##
##label check
##  menu label Test this ^media & install CentOS 7
##  menu default
##  kernel vmlinuz
##  append initrd=initrd.img inst.stage2=hd:LABEL=CentOS\x207\x20x86_64 rd.live.check quiet
##
##label local
##  menu label Boot from ^local drive
##  localboot 0xffff

##menu end
