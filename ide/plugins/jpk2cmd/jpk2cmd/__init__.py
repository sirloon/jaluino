# -*- coding: utf-8 -*-
###############################################################################
# Name: __init__.py                                                           #
# Purpose: Jaluino PK2cmd Plugin                                              #
# Author: Carlo Dormeletti <carlo.dormeletti@email.it>                        #
# with consistent help of Sebastien Lelong <sebastien.lelong@gmail.com>       #
# Copyright: (c) 2010 Carlo Dormeletti <carlo.dormeletti@email.it>            #
# License: wxWindows License                                                  #
###############################################################################

"""PK2cmd JaluinoIDE"""

__author__ = "Carlo Dormeletti"
__version__ = "0.0.3"


#-----------------------------------------------------------------------------#
# Imports
import os, sys, os.path
import wx
from wx.lib.wordwrap import wordwrap

#Editra imports

import iface
import plugin
import util
from ed_menu import EdMenuBar,EdMenu
import ed_msg
import eclib
from profiler import Profile_Get, Profile_Set

#Local import
import jpk2cfg
import jpk2cmd
try:
    wx.GetApp().AddMessageCatalog('jpk2cmd', __name__)
except:
    pass

# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------# 

ID_JPK2        = wx.NewId()
 
 
class Jpk2cmd(plugin.Plugin):
    """Adds a Menu to control PicKit2"""
    plugin.Implements(iface.MainWindowI)
    def PlugIt(self,parent):
        """Implements MainWindowI's PlugIt Method"""
        jpk2cfg.mw = parent # Seb
        self._log = wx.GetApp().GetLog()
        self._log("[PicKit2][info] Starting PK2CMD")
        bar = parent.GetMenuBar()
        jpk2menu = jpk2cmd.GetMenu(self)
        # Seb Code
        # Insert just befor Help
        idx = [i for i,e in enumerate(bar.GetMenus()) if e[1] == _("&Help").replace("&","")]
        if idx:
            bar.Insert(idx[0],jpk2menu,_("PK2cmd"))
        else:
            # put menu just before last entry if can't fing Help menu entry
            # so at least it's displayed...
            bar.Insert(bar.GetMenuCount()-1,jpk2menu,_("PK2cmd"))
        #End of Seb Code

        jpk2cfg.GetPrefs()
        #ed_msg.Subscribe(self.OnProcessExit,eclib.edEVT_PROCESS_EXIT)

    def ExecuteCommandBuffer(self,cmd,arg):
        """Execute a command and show the result in buffer"""
        import jaluino
        pm = wx.GetApp().GetPluginManager()
        jp = pm[jaluino.Jaluino]
        buff = jp.GetJaluinoWindow().GetOutputBuffer()
        worker = eclib.ProcessThread(buff,cmd,args=arg)
        worker.start()
        #wx.MessageBox( _("Executed: "),_("PicKit2"))

    def GetMenuHandlers(self):
        """Returns the event handler for this plugins menu entry"""
        return [(jpk2cmd.ID_PK2PTARGET,  self.OnAction),
                (jpk2cmd.ID_PK2IDENTIFY, self.OnAction),
                (jpk2cmd.ID_PK2UPDATEFW, self.OnAction),
                (jpk2cmd.ID_PK2INFO,     self.OnAction),
                (jpk2cmd.ID_PK2VER,      self.OnAction),
                (jpk2cmd.ID_PK2SETTING,  self.OnSettings),
                (jpk2cmd.ID_PK2PLUGINFO,  self.OnInfo)
                ]

    def GetUIHandlers(self):
        return []

    def OnAction(self, evt):
        """Handles Powering the target"""
        # Seb: first run: prefs isn't defined at all, thus = None, needs to
        # have a default. A empty dict may be better
        prefs = Profile_Get(jpk2cfg.JPK2CMD_PREFS, default={})
        # Seb: prefs.get() needs a proper default here too
        # Carlo: for Windows we have to modify the -B option 
        devfile = os.path.dirname(prefs.get("jpdatloc",jpk2cfg.pk2datloc))
        pk2cmd = prefs.get("jpcmdloc",jpk2cfg.pk2cmdloc) + " -B" + devfile
            
        if evt.GetId() == jpk2cmd.ID_PK2PTARGET:
            """ Power the target """
            self.ExecuteCommandBuffer(pk2cmd,[prefs.get("jptgarg",jpk2cfg.pk2ptarg),""])
        if evt.GetId() == jpk2cmd.ID_PK2IDENTIFY:
            """Handles Identify the Chip"""
            self.ExecuteCommandBuffer(pk2cmd,[prefs.get("jpidarg",jpk2cfg.pk2idarg,),""])
        if evt.GetId() == jpk2cmd.ID_PK2INFO:
            """Handles the info from commandline"""
            arg = ["-?"]
            self.ExecuteCommandBuffer(pk2cmd,arg)
        if evt.GetId() == jpk2cmd.ID_PK2VER:
            """Handles Showing software Versione"""
            self.ExecuteCommandBuffer(pk2cmd,[prefs.get("jpvearg",jpk2cfg.pk2vearg,),""])
        if evt.GetId() == jpk2cmd.ID_PK2UPDATEFW:
            """Handles Updatinf PICKit2 Firmware"""
            options = prefs.get("jpuparg",jpk2cfg.pk2uparg,)
            
            
            self.ExecuteCommandBuffer(pk2cmd,[options,""])



    def OnInfo(self,evt):
        info = wx.AboutDialogInfo()
        info.Name = "JPK2cmd"
        info.Version = __version__
        info.Copyright = "(C) 2010" + __author__
        info.Description = _("""JPK2cmd is a software program that integrates \
in the JaluinoIDE plugin for Editra (C).\n It is a frontend to the Microchip \
(TM) PIC (TM) programmer PICKit2 through the PK2cmd command line interface \
program. \n It uses the JaluinoIDE Shelf window to show the informations.\n \n
Platform: """)
        info.Description = info.Description + sys.platform

        info.WebSite = ("", "")
        info.Developers = [ __author__,
                            "Sebastien Lelong"]

        info.License = _("wxWindows License")

        # Then we call wx.AboutBox giving it that info object
        wx.AboutBox(info)
       

    def OnProcessExit(self,msg):
        msg1 = "" # "Message Type:" +str(msg.GetType())
        msg2 = "Message Data:" + msg.GetData()
        wx.MessageBox( _("Uscita: " + msg1 + " : " + msg2),_("PicKit2"))

    def OnSettings(self, evt):
        """Handles the settings"""
        app = wx.GetApp()
        if evt.GetId() == jpk2cmd.ID_PK2SETTING:
            win = None # app.GetWindowInstance(jpk2cfg.ConfigDialog())
            # is it already created ?
            if win is None:
                # No: create a new window
                config = jpk2cfg.ConfigDialog()
                config.CentreOnParent()
                config.Show()
            else:
                # Yes: give focus
                win.Raise()

#-----------------------------------------------------------------------------#

# Manage the configuration dialog in plugin configuration from Editra Menu
def GetConfigObject():
    return PluginConfig()
 
class PluginConfig(plugin.PluginConfigObject):
    """Plugin configuration object."""
    def GetConfigPanel(self, parent):
        """Get the configuration panel for this plugin
        @param parent: parent window for the panel
        @return: wxPanel
        """
        return jpk2cfg.ConfigPanel(parent)
 
    def GetLabel(self):
        """Get the label for this config panel
        @return string
        """
        return _("JPK2cmd ")
