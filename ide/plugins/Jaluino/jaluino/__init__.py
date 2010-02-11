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

#-----------------------------------------------------------------------------#
# Imports
import os
import wx

# Local modules
import jaluino
import cfgdlg

# Editra imports
import ed_glob
import iface
import plugin
import ed_msg
import util
from profiler import Profile_Get
import syntax
import syntax.synglob as synglob
from ed_menu import EdMenuBar

#-----------------------------------------------------------------------------#
# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------#
# Interface Implementation
class Jaluino(plugin.Plugin):
    plugin.Implements(iface.ShelfI)
    ID_JALUINO = wx.NewId()
    INSTALLED = False
    SHELF = None

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
        """This plugins menu entry"""
        item = wx.MenuItem(menu, self.ID_JALUINO, self.__name__, 
                           _("Run script from current buffer"))
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
        # TODO: deal with keybinder
        tmenu = mainw.GetMenuBar().GetMenuByName("tools")
        tmenu.Insert(0, jaluino.ID_COMPILE_LAUNCH, _("Compile") + \
                     EdMenuBar.keybinder.GetBinding(jaluino.ID_COMPILE_LAUNCH),
                     _("Compile current Jalv2 file"))
        mainw.AddMenuHandler(jaluino.ID_COMPILE_LAUNCH, OnCompile)
        tmenu.Insert(1, jaluino.ID_UPLOAD_LAUNCH, _("Upload") + \
                     EdMenuBar.keybinder.GetBinding(jaluino.ID_UPLOAD_LAUNCH),
                     _("Upload HEX file associated to current Jalv2 file"))
        mainw.AddMenuHandler(jaluino.ID_UPLOAD_LAUNCH, OnUpload)
        tmenu.Insert(2, wx.ID_SEPARATOR)

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
        xmlfile = os.environ.get("JALUINO_LAUNCH_FILE","jaluino_launch.xml")
        path = os.path.join(path, unicode(xmlfile))
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
                util.Log(u"[Jaluino][info] Merging %s and %s" % (cmds,prevcmds))
                hstate[langname] = (default,list(set(cmds + prevcmds)))
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

def OnCompile(evt):
    """Handle the Run Script menu event and dispatch it to the currently
    active Jaluino panel

    """
    ed_msg.PostMessage(jaluino.MSG_COMPILE)

def OnUpload(evt):
    """Handle the Run Last Script menu event and dispatch it to the currently
    active Launch panel

    """
    ed_msg.PostMessage(jaluino.MSG_UPLOAD)

