#!/bin/sh

CACHEDIR='/tmp/ISO/'

help(){
  cat <<EOF
usage: `basename $0` <args>

<description>

arguments:
  <options>
EOF
  exit 1
}

while getopts ":hi:I:o:t:T:" opt; do
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
    t)
        export TMPDIR="$OPTARG"
        ;;
    T)
        TEMPLATEDIR="$OPTARG"
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

clean(){
    umount $tmpdir/iso/
    rm -rf "${tmpdir}"
}

mkdir -p "${CACHEDIR}"
tmpdir=`mktemp -d`

iso="${CACHEDIR}/`basename $IN`"

if ! [ -f "$iso" ]
then
    cd "${CACHEDIR}"
    curl -O $IN
    cd -  >/dev/null 2>&1
fi

mkdir -p $tmpdir/iso/
mkdir -p $tmpdir/new_iso/
mount "${iso}" $tmpdir/iso/
rsync -pa $tmpdir/iso/ $tmpdir/new_iso/
koui-template -i ${INV} -t ${TEMPLATEDIR}/kickstart.py \
    -m 'byhost' -p '${host["hostname"]}.ks' -o $tmpdir/new_iso/
koui-template -i inventory/ -t ${TEMPLATEDIR}/sysconfig.py \
    -m 'global' -p 'isolinux.cfg' -o $tmpdir/new_iso/isolinux/

$MKISO -r -T -J -V "Custom Centos Build" -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4  -boot-info-table -o "$OUT" "$tmpdir/new_iso/"

clean
