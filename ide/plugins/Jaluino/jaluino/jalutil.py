# -*- coding: utf-8 -*-
###############################################################################
# Name: jalutil.py                                                             #
# Purpose: Utility module
# Author: Sebastien Lelong <sebastien.lelong@gmail.com>
# Copyright: (c) 2010 Sebastien Lelong <sebastien.lelong@gmail.com>           #
# License: wxWindows License                                                  #
###############################################################################

import os, cPickle

import ed_glob
from profiler import Profile_Get
import util

import cfgdlg

def GetDefaultConfig():
    '''Default configation, coming from Jaluino IDE install script'''
    deffn = os.path.join(ed_glob.CONFIG['CACHE_DIR'],"install.pick")
    if os.path.exists(deffn):
        cfg = cPickle.load(file(deffn))
    else:
        util.Log("[jaluino][warn] Unable to find default configuration file '%s', did you run install script ?" % deffn)
        cfg = {}

    return cfg

def GetJaluinoPrefs():
    '''Return merged preferences of custom/default'''
    # default
    cfg = GetDefaultConfig()
    # custom
    jalcfg = Profile_Get(cfgdlg.JALUINO_PREFS, default=dict())
    # clean if empty keys
    for k,v in jalcfg.items():
        if not v:
            del jalcfg[k]
    # merge, with jaluino custom > default
    cfg.update(jalcfg)

    return cfg
