@ echo off
rem  Title: jallib executable for windows system
rem  Author: Sebastien Lelong, Copyright (c) 2008, all rights reserved.
rem  Adapted-by: Joep Suijs
rem  Compiler:
rem
rem  This file is part of jallib (http://jallib.googlecode.com)
rem  Released under the BSD license (http://www.opensource.org/licenses/bsd-license.php)
rem
rem  Sources:
rem
rem  Description: the aim of this script is to ease user's life !
rem  If *you* are a user, edit this script by specfiying the following
rem  environment variables. These variables will save you some typing
rem  while using the jallib wrapper script. Adapt it to your own need !
rem  Once done, you can put this script in your path.
rem  Rem: usually, setting JALLIB_ROOT as an absolute path is enough.


rem ########################
rem ENVIRONMENT VARIABLES #
rem ######################


rem call from something above, or directly called ?
set RUNFROM=%CD%\..
if defined JALUINO_ROOT set RUNFROM=%JALUINO_ROOT%

set JALUINO_ROOT=%RUNFROM%
rem Path to the jallib root's repository (containing "tools,"compiler","include" dirs)
set JALLIB_ROOT=%RUNFROM%
rem if running from SVN, adjust
if exist %JALUINO_ROOT%\.svn set JALLIB_ROOT=%RUNFROM%\3rdparty\jallib_svn
rem path to jallib root's samples.
set JALLIB_SAMPLEDIR=%JALUINO_ROOT%\samples
rem path to jallib root's libraries.
if not defined JALLIB_REPOS set JALLIB_REPOS=%JALUINO_ROOT%\lib;%JALLIB_ROOT%\include
rem path to "jalv2" executable. If not in your PATH, set an absolute path to the exec
rem Arguments can be added if they're needed as default (Ex: "jalv2 -long-start")
if not defined JALLIB_JALV2 set JALLIB_JALV2=%JALLIB_ROOT%\compiler\jalv2.exe


rem get python from default/standard location, but honor PYTHON_EXEC

if not defined JALLIB_PYTHON set JALLIB_PYTHON=C:\Python25\Python.exe

if defined PYTHON_EXEC set JALLIB_PYTHON=%PYTHON_EXEC%
%JALLIB_PYTHON% "%JALLIB_ROOT%\tools\jallib.py" %1 %2 %3 %4 %5 %6 %7 %8 %9

