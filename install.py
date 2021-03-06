#!/usr/bin/env python

# This script is aimed to automacally install Jaluino IDE
# plugins and configuration files. Can be used either when 
# Jaluino comes from SVN sources, or from a release package.
#
# It tries to guess some environment configuration
# and generate a default configuration file used by Editra
# and Jaluino IDE plugin to determine a default environment.
# It also installs all Jaluino IDE related configuration and
# plugins files, so they are ready to be used from Editra
# 
# This script can be run multiple time in order to update
# Jaluino IDE, it'll just overwrite some default files.
#

import os, sys, glob, re
import subprocess
import cPickle


def common():
    # this is where install.py is located
    runfrom = os.path.split(os.path.abspath(sys.argv[0]))[0]
    jaluino_root = runfrom
    jaluino_bin = os.path.join(jaluino_root,"bin")
    # adjust if running from SVN or release package
    jallib_root = None
    jallib_respo = None
    jaluino_svn = None
    if os.path.exists(os.path.join(jaluino_root,"3rdparty","jallib_svn")):
        jallib_root = os.path.join(jaluino_root,"3rdparty","jallib_svn")
        jallib_repos = os.pathsep.join([os.path.join(jaluino_root,"lib"),
                                        os.path.join(jallib_root,"include")])
        jaluino_svn = 1
    else:
        jallib_root = jaluino_root  # all in "lib"
        jallib_repos = os.path.join(jaluino_root,"lib")
        jaluino_svn = 0

    return {'RUNFROM'       : runfrom,
            'JALUINO_ROOT'  : jaluino_root,
            'JALLIB_ROOT'   : jallib_root,
            'JALUINO_BIN'   : jaluino_bin,
            'JALLIB_REPOS'  : jallib_repos,
            'JALUINO_SVN'   : jaluino_svn,
            'SYSTEM'        : sys.platform,
           }

def nix():
    common_env = common()
    # Determine where python is installed
    try:
        p = subprocess.Popen(["which","python"],stdout=subprocess.PIPE,
                                                stderr=subprocess.STDOUT,
                                                shell=False)
        out = p.stdout.read()
        p.communicate()
        python_exec = out.strip()
    except OSError,e:
        print >> sys.stderr, "Unable to find python, not installed...\nError: %s" % e
        raw_input("Press a key to quit...")
        sys.exit(255)

    nix_env = {'PYTHON_EXEC'         : python_exec,
               'JALUINO_LAUNCH_FILE' : "jaluino_launch.xml",
               'JALLIB_JALV2'        : os.path.join(common_env['JALLIB_ROOT'],"compiler","jalv2"),
               'JALLIB_PYPATH'       : os.path.join(common_env['JALLIB_ROOT'],"tools"),
              }

    # Editra configuration directories
    nix_env['EDITRA_CACHE'] = os.path.join(os.environ['HOME'],".Editra","cache")
    nix_env['EDITRA_PLUGINS'] = os.path.join(os.environ['HOME'],".Editra","plugins")

    nix_env.update(common_env)
    return nix_env

def osx():
    nix_env = nix()
    # override some values specific to OSX
    nix_env['EDITRA_CACHE'] = os.path.join(os.environ['HOME'],"Library","Application Support","Editra","cache")
    nix_env['EDITRA_PLUGINS'] = os.path.join(os.environ['HOME'],"Library","Application Support","Editra","plugins")
    return nix_env

def win():
    import _winreg as winreg
    common_env = common()
    # Determine where python is installed
    # 1. in Editra files
    # 2. on system
    try:
        jaluino_dir = winreg.QueryValue(winreg.HKEY_LOCAL_MACHINE,r"Software\Microsoft\Windows\CurrentVersion\App Paths\Jaluino")
        python_exec = os.path.join(jaluino_dir,"3rdparty","Editra","python.exe")
        if not os.path.isfile(python_exec):
            raise OSError
        jallib_pypath = os.pathsep.join([
                os.path.join(common_env['JALLIB_ROOT'],"tools"),
                os.path.join(jaluino_dir,"3rdparty","Editra","library.zip")])
    except OSError,e:
        try:
            python_exec = winreg.QueryValue(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Python.exe")
            # ok, not using bundle python, so we need to adjust PYTHONPATH to include libraries from standard python installtion
            rootpylib = os.path.split(python_exec)[0]
            pylib = os.path.join(rootpylib,"Lib")
            pysite = os.path.join(pylib,"site-packages")
            jallib_pypath  = os.pathsep.join([pylib,pysite,os.path.join(common_env['JALLIB_ROOT'],"tools")]),
        except OSError,e:
            print >> sys.stderr, "Unable to find python, not installed...\nError: %s" % e
            raw_input("Press a key to quit...")
            sys.exit(255)

    # exception for windows, when Editra is bundled as binaries. We'll adjust PYTHONPATH to include
    # python2.5 libraries


    win_env = {'PYTHON_EXEC'         : '"%s"' % python_exec,
               'JALUINO_LAUNCH_FILE' : "jaluino_launch_win.xml",
               'JALLIB_JALV2'        : os.path.join(common_env['JALLIB_ROOT'],"compiler","jalv2.exe"),
               'JALLIB_PYPATH'       : jallib_pypath,
              }

    # Editra configuration directories
    win_env['EDITRA_CACHE'] = os.path.join(os.environ['APPDATA'],"Editra","cache")
    win_env['EDITRA_PLUGINS'] = os.path.join(os.environ['APPDATA'],"Editra","plugins")

    win_env.update(common_env)
    return win_env

def get_env():
    if sys.platform.startswith("win"):
        return win()
    elif sys.platform.startswith("darwin"):
        return osx()
    else:
        return nix()
        

def install():
    # TODO: check if already installed
    #  - check dates
    #  - and/or put a hidden ".installed" directory
    # For now, not a big deal, as files are small and not numerous

    print
    print

    env = get_env()
    print "Jaluino running from %s" % (env.get("JALUINO_SVN") and "SVN" or "release package")
    print
    print

    print "Jaluinoide env:" % env
    for k,v in env.items():
        print "    %s : %s" % (k,v)
    # check one Editra directory, to see if it already ran
    print "EDITRA %s" % env['EDITRA_CACHE']
    if not os.path.exists(env['EDITRA_CACHE']): 
        print """


It seems Editra has never run before, can't install.
Please run Editra once, and re-launch this script !


"""
        raw_input("Press a key to quit...")

    path = os.path.join(env['EDITRA_CACHE'],"install.pick")
    print "Now generating default configuration file '%s'" % path
    cPickle.dump(env,file(path,"wb"))

    cachefiles = glob.glob(os.path.join("ide","conf","*"))
    pluginfiles = glob.glob(os.path.join("ide","plugins","*.egg"))
    
    for cfilen in cachefiles:
        print "Installing conf '%s'" % cfilen
        destn = os.path.join(env['EDITRA_CACHE'],os.path.basename(cfilen))
        content = file(cfilen,"rb").read()
        file(destn,"wb").write(content)

    for pfilen in pluginfiles:
        print "Installing plugin '%s'" % pfilen
        destn = os.path.join(env['EDITRA_PLUGINS'],os.path.basename(pfilen))
        content = file(pfilen,"rb").read()
        file(destn,"wb").write(content)
    
    print "Enabling Jaluino plugin"
    plugincfg = os.path.join(env['EDITRA_PLUGINS'],"..","plugin.cfg")
    # Append config to existing or new file, Editra will clean up this when
    # it quits...
    fout = file(plugincfg,"a")
    print >> fout,"jaluino=True"
    fout.close()
    print
    print
    print """

All Jaluino IDE configuration files and plugins have installed.
You can now run Editra and enable Jaluino IDE plugin.


"""
    return



if __name__ == "__main__":
    install()


