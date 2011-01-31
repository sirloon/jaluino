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


#-----------------------------------------------------------------------------#
# Imports
import os, sys
import wx

import jalutil
import util
# adjust PYTHONPATH for jallib.py
try:
    cfg = jalutil.GetJaluinoPrefs()
except AttributeError:
    # not running from wx app
    cfg = {}
path = cfg.get("JALLIB_PYPATH")
if path:
    sys.path = path.split(os.pathsep) + sys.path

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

# pre-filled a list a custom commands, which will be loaded
# when Jaluino plugin will be up and available
CUSTOM_COMMANDS = []

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
        self.jaluino_window = jaluino.JaluinoWindow(parent)
        return self.jaluino_window

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
        return "0.5.99"

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
        RegisterJaluinoCommands()

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

    def GetJaluinoWindow(self):
        try:
            return self.jaluino_window
        except AttributeError:
            pass
        return None

#-----------------------------------------------------------------------------#

def GetConfigObject():
    return JaluinoConfigObject()

class JaluinoConfigObject(plugin.PluginConfigObject):
    def GetConfigPanel(self, parent):
        return cfgdlg.ConfigNotebook(parent)

    def GetLabel(self):
        return _("Jaluino")

#-----------------------------------------------------------------------------#


# Jaluino API
def RegisterJaluinoCommands():
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
        util.Log("[Jaluino][debug] \n\nCUSTOM_COMMANDS: %s" % repr(CUSTOM_COMMANDS))
        for langid,cmds in xmlcmds.items() + CUSTOM_COMMANDS:
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

def RegisterCustomCommand(langid,cmdname,cmdline):
    """Register new command, named 'cmdname', for language
       identified by langid.
       eg. Jalv2 is synglob.ID_LANG_JAL,
           HEX is synglob.ID_LANG_HEX
    """
    # register custom commands line, postponed because Jaluino plugin can be loaded
    # after other plugins registering commands
    CUSTOM_COMMANDS.append((langid,[(cmdname,cmdline,)],))

