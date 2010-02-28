d:\python26\python.exe setup.py bdist_egg
copy dist\*.* "C:\Documents and Settings\nly96021\Application Data\Editra\plugins"

set JALLIB_PYTHON=D:\Python26\Python.exe
set JALUINO_ROOT=D:\pic\jaluino
set JALLIB_ROOT=%JALUINO_ROOT%\3rdparty\jallib_svn
set JALLIB_REPOS=%JALUINO_ROOT%\lib;%JALLIB_ROOT%\include
set JALLIB_SAMPLEDIR=%JALUINO_ROOT%\samples

set PATH=D:\pic\jaluino\bin;%PATH%

%JALLIB_PYTHON% D:\pic\Editra\launcher.py
