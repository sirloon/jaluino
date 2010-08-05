#!/bin/bash

LIBUSB=libusb-win32-filter-bin-1.1.14.3.exe
EDITRA=editra.win32.0.5.72.exe 
PYUSB=pyusb-0.4.3.win32-py2.6.exe
PYSER=pyserial-2.5.win32.exe
PYEXE=python-2.6.msi 

for file in $LIBUSB $EDITRA $PYUSB $PYSER $PYEXE
do
    echo Downloading $file
    wget http://jaluino.googlecode.com/files/$file -O ../../3rdparty/$file

done

echo
echo
echo "OK, now go to your win box and compile NSIS installer :)"
echo
echo
