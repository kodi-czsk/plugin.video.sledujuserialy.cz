#/bin/sh
# do NOT use this script from XBMC addons directory, it is intented for development only
DESTDIR=~/.kodi/addons/plugin.video.sledujuserialy.cz

rm -rf ${DESTDIR}
mkdir -p ${DESTDIR}
cp -a * ${DESTDIR}
