#!/bin/sh

RCol='\33[0m'    # Text Reset

# Regular            Bold                 Underline            High Intensity       BoldHigh Intens   
Bla='\33[0;30m';     BBla='\33[1;30m';    UBla='\33[4;30m';    IBla='\33[0;90m';    BIBla='\33[1;90m';
Red='\33[0;31m';     BRed='\33[1;31m';    URed='\33[4;31m';    IRed='\33[0;91m';    BIRed='\33[1;91m';
Gre='\33[0;32m';     BGre='\33[1;32m';    UGre='\33[4;32m';    IGre='\33[0;92m';    BIGre='\33[1;92m';
Yel='\33[0;33m';     BYel='\33[1;33m';    UYel='\33[4;33m';    IYel='\33[0;93m';    BIYel='\33[1;93m';
Blu='\33[0;34m';     BBlu='\33[1;34m';    UBlu='\33[4;34m';    IBlu='\33[0;94m';    BIBlu='\33[1;94m';
Pur='\33[0;35m';     BPur='\33[1;35m';    UPur='\33[4;35m';    IPur='\33[0;95m';    BIPur='\33[1;95m';
Cya='\33[0;36m';     BCya='\33[1;36m';    UCya='\33[4;36m';    ICya='\33[0;96m';    BICya='\33[1;96m';
Whi='\33[0;37m';     BWhi='\33[1;37m';    UWhi='\33[4;37m';    IWhi='\33[0;97m';    BIWhi='\33[1;97m';

CACHEDIR='/tmp/ISO/'

help(){
  cat <<EOF
Usage: 
	`basename $0` -i <input iso url> -I <inventory> \\
	  -T <template dir> -o <out iso> \\
	  [-t <tmp dir>] [-c cache dir]

Description:
	Build an iso with kickstart selection in syslinux (boot menu)

`basename $0` must be executed as root

Example:
	`basename $0` -i \\
	http://mirror-fr1.bbln.org/centos/7/isos/x86_64/CentOS-7.0-1406-x86_64-NetInstall.iso \\
	-I inventory/ -o ./test2.iso -T templates/

EOF
  exit 1
}

clean(){
    if ! [ -z "${tmpdir}" ]
    then
        info_msg "Cleaning working directory"
    	umount $tmpdir/iso/
    	rm -rf "${tmpdir}"
    fi
    if [ -f "$iso" ]
    then
	info_msg "Iso '${iso}' kept for futur generations"
    fi
}

clean_exit(){
    clean
    exit 1
}

error(){
    msg="$1"
    printf "${BRed}[ERROR]${Yel} ${msg}${RCol}\n"
    clean 
    exit 1
}

info_msg(){
    msg="$1"
    printf "${BBlu}[INFO] ${Gre}${msg}${RCol}\n"
}

trap clean_exit HUP INT TERM

while getopts ":hi:I:o:t:T:c:" opt; do
  case $opt in

    h) 
        help
        ;;
    i)
        IN="$OPTARG"
        ;;
    I)
        INV="$OPTARG"
        ;;
    o)
        OUT="$OPTARG"
        ;;
    T)
        TEMPLATEDIR="$OPTARG"
        ;;
    t)
        export TMPDIR="$OPTARG"
        ;;
    c)
        CACHEDIR="$OPTARG"
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        help
        exit 1
        ;;
    :)
        echo "Option -$OPTARG requires an argument." >&2
        help
        exit 1
        ;;
  esac
done

if which genisoimage >/dev/null
then
    MKISO='genisoimage'
elif which mkisofs >/dev/null
then
    MKISO='mkisofs'
fi

[ "`id -u`" -ne 0 ] && error "Must be root to run this script"

[ -z "${IN}" ] && error "missing arg -i <input iso url>"
[ -z "${OUT}" ] && error "missing arg -o <output iso>"
! [ -d "${INV}" ] && error "missing arg -I <inventory>"
! [ -d "${TEMPLATEDIR}" ] && error "missing arg -T <template directory>"

mkdir -p "${CACHEDIR}"
tmpdir=`mktemp -d`

iso="${CACHEDIR}/`basename $IN`"

if ! [ -f "$iso" ]
then
    cd "${CACHEDIR}"
    info_msg "Download '`basename ${IN}`' in '${CACHEDIR}'"
    curl --fail --compressed -O $IN || error "Unable to download iso '$IN'"
    cd -  >/dev/null 2>&1
else
    info_msg "Iso '`basename ${IN}`' already downloaded in '${CACHEDIR}'"
fi

mkdir -p $tmpdir/iso/ &&
mkdir -p $tmpdir/new_iso/ || error "Failed to create working directory"

info_msg "Mount iso '`basename ${IN}`' on '$tmpdir/iso/'"
mount "${iso}" $tmpdir/iso/ || error "Unable to mount ${iso}"

info_msg "Copy iso content in '${tmpdir}/new_iso/'"
rsync -pa $tmpdir/iso/ $tmpdir/new_iso/ || error "Failed to copy iso content"

info_msg "Create kickstart files"
koui-template -i ${INV} -t ${TEMPLATEDIR}/kickstart.py \
    -m 'byhost' -p '${host["hostname"]}.ks' -o $tmpdir/new_iso/ || error "Failed to generate kickstarts"

info_msg "Create syslinux menu"
koui-template -i inventory/ -t ${TEMPLATEDIR}/sysconfig.py \
    -m 'global' -p 'isolinux.cfg' -o $tmpdir/new_iso/isolinux/ || error "Failed to generate syslinux menu"

info_msg "Build the new iso '$OUT'"
$MKISO -r -T -J -V "Custom Centos Build" -b isolinux/isolinux.bin \
	-c isolinux/boot.cat -no-emul-boot -boot-load-size 4  \
	-input-charset 'utf-8' -boot-info-table -o "$OUT" \
	"$tmpdir/new_iso/" || error "Failed to build out iso ${OUT}"
clean
