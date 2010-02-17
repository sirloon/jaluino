c:\Python25\python.exe pyinstaller-1.3\Configure.py
c:\Python25\python.exe pyinstaller-1.3\Makespec.py ..\jaluinoide_svn
c:\Python25\python.exe pyinstaller-1.3\Build.py jaluinoide_svn.spec
copy distjaluinoide_svn\jaluinoide_svn.exe ..\jaluinoide_svn.exe
rmdir /S /Q distjaluinoide_svn
rmdir /S /Q buildjaluinoide_svn
