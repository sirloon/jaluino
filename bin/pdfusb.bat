@ echo off

rem Wrapper script to run Albert Fabert's PDFUSB bootloader

rem call from something above, or directly called ?
set RUNFROM=%CD%\..
if defined JALUINO_ROOT set RUNFROM=%JALUINO_ROOT%

set JALUINO_ROOT=%RUNFROM%

rem get python from default/standard location, but honor PYTHON_EXEC
set JALLIB_PYTHON=C:\Python25\Python.exe
if defined PYTHON_EXEC set JALLIB_PYTHON=%PYTHON_EXEC%

echo Press reset button...
%JALLIB_PYTHON% "%JALUINO_ROOT%\bootloaders\pdfusb\hostapp\UsbBootLoader.py" %1 %2 %3 %4 %5 %6 %7 %8 %9

