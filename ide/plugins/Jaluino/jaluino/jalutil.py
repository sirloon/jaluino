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
from profiler import Profile_Get, Profile_Set
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

def MergeCodeTemplates(fileobj,overwrite=False):
    '''Parse file-like object, extract code templates 
       and merge them with existing ones, that is, ones 
       created through CodeTemplater plugin and stored
       in registry.

       While merging, those declared via CodeTemplater have
       precedence: if a template name exist in registry and
       in the file, the ones in the file are ignored. This 
       behavior can be altered with 'overwrite' parameter.

       In no code templates could be found in the registry,
       appropriate dict keys will be created so once
       CodeTemplater is activated, it'll work out of the box
    '''
    import syntax.synglob as synglob
    if not hasattr(synglob,"ID_LANG_JAL"):
        raise AttributeError("Can't find Jalv2 language definition, check edxml files")

    # prepare defaults if no templates were registered before
    import codetemplater.templates
    cfg = Profile_Get(codetemplater.templates.PROFILE_KEY_TEMPLATES,default=dict())
    if not cfg or not cfg.get("Jalv2"):
        cfg = {"Jalv2" : {}}
    jaltpldict = cfg["Jalv2"]
        
    # templates (or code snippets) looks like:
    # {"template name (key)" : { "name" : str,
    #                            "description" : str,
    #                            "indent" : bool,
    #                            "templ" : str

    # for now, templates are stored in a python file. This file must contain
    # a "templates" variable (dict)
    # pros: we can mix templates from other files and add some logic if needed
    # cons: not a proper exchange format
    try:
        exec(fileobj.read())
        print "templates: %s" % repr(templates)
        if overwrite:
            # templates in files have precedence
            jaltpldict.update(templates)
        else:
            # existing templates have precedence
            templates.update(jaltpldict)
            jaltpldict = templates

        # save back to registry
        cfg["Jalv2"] = jaltpldict
        Profile_Set(codetemplater.templates.PROFILE_KEY_TEMPLATES,cfg)

        tpls = codetemplater.templates.load_templates()
        return tpls

    except Exception,e:
        # exception was caught, and won't be caught anymore by wx 
        raise e

