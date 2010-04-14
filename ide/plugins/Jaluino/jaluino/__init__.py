# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: Jaluino Plugin                                                      #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Adapted by: Sebastien Lelong <sebastien.lelong@gmail.com>
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Jaluino IDE"""

__author__ = "Sebastien Lelong"
__version__ = "0.16"


#-----------------------------------------------------------------------------#
# Imports
import os, sys
import wx

import jalutil
import util
# adjust PYTHONPATH for jallib.py
cfg = jalutil.GetJaluinoPrefs()
path = cfg.get("JALLIB_PYPATH")
if path:
    sys.path = path.split(os.pathsep) + sys.path

# HACK: Editra 0.5.51 win binary embeds library ctypes, but misses wintypes
# wintypes is required by pyserial. Even adjusting PYTHONPATH, through sys.path 
# modification above won't help in this case, as ctypes is already loaded by Editra
# long before we get there. Importing ctypes again, as done in pyserial, will just
# get ctypes already remaining in memory.
# In order to refresh PYTHONPATH so ctypes is imported again, we need to reload it.
import ctypes
reload(ctypes)

# Local modules
import jaluino
import cfgdlg
import jalcomp

# Editra imports
import iface
import plugin
import util
import autocomp
from profiler import Profile_Get
import ed_glob
import ed_msg
import syntax
import syntax.synglob as synglob
#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface Implementation
class Jaluino(plugin.Plugin):
    plugin.Implements(iface.ShelfI)
    plugin.Implements(iface.AutoCompI)
    ID_JALUINO = wx.NewId()
    INSTALLED = False
    SHELF = None

    #-- Shelf API --#
    @property
    def __name__(self):
        return u'Jaluino'

    def AllowMultiple(self):
        return False

    def CreateItem(self, parent):
        return jaluino.JaluinoWindow(parent)

    def GetBitmap(self):
        """Get the tab bitmap
        @return: wx.Bitmap

        """
        bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_CLASS_TYPE), wx.ART_MENU)
        return bmp

    def GetId(self):
        """The unique identifier of this plugin"""
        return self.ID_JALUINO

    def GetMenuEntry(self, menu):
        '''Shelf menu entry'''
        item = wx.MenuItem(menu, self.ID_JALUINO, self.__name__) 
        item.SetBitmap(self.GetBitmap())
        return item

    def GetMinVersion(self):
        return "0.5.33"

    def GetName(self):
        """The name of this plugin"""
        return self.__name__

    def InstallComponents(self, mainw):
        """Install extra menu components
        param mainw: MainWindow Instance

        """
        util.Log("[Jaluino][info] Building Jaluino menu")
        # Menu
        # TODO: deal with keybinder
        bar = mainw.GetMenuBar()
        menu = jaluino.GetMenu(mainw)
        # Insert just before Help
        idx = [i for i,e in enumerate(bar.GetMenus()) if e[1] == _("&Help").replace("&","")]
        if idx:
            util.Log("[Jaluino][info] Jaluino menu will be just before Help entry")
            bar.Insert(idx[0],menu,_("Jaluino"))
            # disable it, JaluinoWindow will handle this (so if Jaluino shelf isn't active
            # you can't click on menu entries
        else:
            # put menu just before last entry if can't fing Help menu entry
            # so at least it's displayed...
            util.Log("[Jaluino][info] Jaluino menu will be just before last entry")
            bar.Insert(bar.GetMenuCount()-1,menu,_("Jaluino"))
        jaluino.EnableJaluinoMenu(mainw,False)

        util.Log("[Jaluino][info] Registering jalv2/jaluino commands")
        self.RegisterJaluinoCommands()

    def IsInstalled(self):
        """Check whether jaluino has been installed yet or not
        @note: overridden from Plugin
        @return bool

        """
        return Jaluino.INSTALLED

    def IsStockable(self):
        return True

    #-- AutoComp API --#

    def GetCompleter(self, buff):
        return jalcomp.Completer(buff)

    def GetFileTypeId(self):
        return synglob.ID_LANG_JAL


    # Jaluino API
    def RegisterJaluinoCommands(self):
        # Plugins deps
        try:
            import launch.handlers as handlers
            import launch.launchxml as launchxml
        except ImportError,e:
            msg = _("Launch plugin is missing and is required for Jaluino IDE\nPlease first install Launch plugin.")
            util.Log("[Jaluino][info] %s" % msg)
            wx.MessageBox(msg)
            return

        loaded = False
        xmlcmds = {}
        path = ed_glob.CONFIG['CACHE_DIR']
        xmlfile = jalutil.GetJaluinoPrefs().get("JALUINO_LAUNCH_FILE","jaluino_launch.xml")
        path = os.path.join(path,xmlfile)
        if os.path.exists(path):
            lxml = launchxml.LaunchXml()
            lxml.SetPath(path)
            try:
                loaded = lxml.LoadFromDisk()
            except Exception,e:
                util.Log(u"[Jaluino][err] Unable to load default commands because: %s" % e)

            if loaded:
                for hndlr in lxml.GetHandlers().values():
                    handlers.HANDLERS[hndlr.GetLangId()] = handlers.XmlHandlerDelegate(hndlr)
                    xmlcmds.setdefault(hndlr.GetLangId(),handlers.HANDLERS[hndlr.GetLangId()].GetCommands())
            else:
                util.Log(u"[Jaluino][warn] failed to load launch extensions for Jaluino")
        else:
            util.Log(u"[Jaluino][warn] No jaluino_launch.xml file found for Jaluino commands !!!")

        # merge custom and original commands
        hstate = Profile_Get(jaluino.JALUINO_KEY)
        if hstate is not None:
            for langid,cmds in xmlcmds.items():
                langname = handlers.GetHandlerById(langid).GetName()
                if not hstate.get(langname):
                    util.Log(u"[Jaluino][warn] Can't find previous declared commands for language '%s', no merge needed" % langname)
                    continue
                default,prevcmds = hstate[langname]
                # default commands have precedence
                util.Log(u"[Jaluino][info] Merging %s and %s" % (cmds,prevcmds))
                dcmds = dict(cmds)
                dprevcmds = dict(prevcmds)
                dprevcmds.update(dcmds)
                hstate[langname] = (default,dprevcmds.items())
                util.Log(u"[Jaluino][info] For language %s, available commands are: %s" % (langname,hstate[langname]))
                handlers.SetState(hstate)

#-----------------------------------------------------------------------------#

def GetConfigObject():
    return JaluinoConfigObject()

class JaluinoConfigObject(plugin.PluginConfigObject):
    def GetConfigPanel(self, parent):
        return cfgdlg.ConfigNotebook(parent)

    def GetLabel(self):
        return _("Jaluino")

#-----------------------------------------------------------------------------#

