# -*- coding: utf-8 -*-
###############################################################################
# Name: pk2cfg.py                                                             #
# Purpose: Some common definition e configuration panel                       #
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
import sys
import os.path
import platform
import wx
import wx.lib.filebrowsebutton

# Editra
from profiler import Profile_Get, Profile_Set

# Local imports


# Globals
_ = wx.GetTranslation

DEBUG = True

JPK2CMD_PREFS = "JPK2cmd.Prefs"
ID_CMDLOC = wx.NewId()
ID_DATLOC = wx.NewId()
ID_IDOPT = wx.NewId()
ID_PTOPT = wx.NewId()
ID_VEOPT = wx.NewId()
ID_UPOPT = wx.NewId()


ID_LISTPREFS = wx.NewId()
ID_DELPREFS = wx.NewId()
ID_SAVEPREF = wx.NewId()


mw = None

if sys.platform == "linux2": # or sys.platform == "sunos": # in case needed
    if platform.dist()[0]=="debian" :
        pk2cmdloc = "/usr/bin/pk2cmd"
        pk2datloc = "/usr/share/pk2cmd/PK2DeviceFile.dat"
    else:
        pk2cmdloc = ""
        pk2datloc = ""  
              
    pk2ptarg = "-P -R -T" 
    pk2idarg = "-P -I"
    pk2vearg = "-?v"
    pk2uparg = "-D"
    
if sys.platform == "win32":
    pk2cmdloc = ""
    pk2datloc = ""
    pk2ptarg = "-P -R -T" 
    pk2idarg = "-P -I"
    pk2vearg = "-?v"
    pk2uparg = "-D"

class ConfigDialog(wx.Frame):
    """Configuration dialog for configuring the location of the pk2cmd exec
    and the command line options for the actions.

    """
    def __init__(self, parent=None): # For Seb I've to use None 
        """Create the ConfigDialog
        @param parent: The parent window 
        
        """

        wx.Frame.__init__(self, parent, title=_("PK2CMD Configuration Panel"))

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Register with app
        wx.GetApp().RegisterWindow(repr(self), self)

    def __DoLayout(self):
        """Layout the dialog"""
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(self)
        dialog = ConfigPanel(panel)
        hsizer.AddMany([((5, 5), 0), (dialog, 1, wx.EXPAND), ((5, 5), 0)])
        vsizer.AddMany([((5, 5), 0), (hsizer, 1, wx.EXPAND), ((10, 10), 0)])
        panel.SetSizer(vsizer)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()
        self.SetMinSize((550, 345))

    def OnClose(self, evt):
        """Unregister the window when its closed"""
        wx.GetApp().UnRegisterWindow(repr(self))
        evt.Skip()


class ConfigPanel(wx.Panel):
    def __init__(self, parent):
        super(ConfigPanel, self).__init__(parent)
        # Make sure config has been initialized
        prefs = self.GetPrefs()
        # Attributes
        self._sb = wx.StaticBox(self, label=_("File Selection"))
        self._sbs = wx.StaticBoxSizer(self._sb, wx.VERTICAL)
        self._pk2cmdloc = wx.lib.filebrowsebutton.FileBrowseButton(self,ID_CMDLOC,labelText=_("PK2cmd location"),
                                                      initialValue=prefs.get("jpcmdloc") or pk2cmdloc,
                                                      changeCallback=self.OnFileSelected,fileMask="*")
        self._pk2datloc = wx.lib.filebrowsebutton.FileBrowseButton(self,ID_DATLOC,labelText=_("PK2DeviceFile.dat location"),
                                                      initialValue=prefs.get("jpdatloc") or pk2datloc,
                                                      changeCallback=self.OnFileSelected)
        self._pk2datloc.SetToolTipString(_("Location of the PK2DeviceFile.dat, \
            PK2cmd need to know it"))

         
        self._sb1 = wx.StaticBox(self, label=_("Command lines Options"))
        self._sbs1 = wx.StaticBoxSizer(self._sb1, wx.VERTICAL)
        self._sbp = wx.StaticBox(self,label="")
        self._sbp1 = wx.StaticBoxSizer(self._sbp, wx.HORIZONTAL)
        self._sg1 = wx.GridBagSizer(5,5)

        self._sg1.Add(wx.StaticText(self,-1,_("'Power the Target' options")),(0,0))
        self._sg1.Add(wx.StaticText(self,-1,_("'Identify' Options")),(1,0))
        self._sg1.Add(wx.StaticText(self,-1,_("'Version info' Options")),(2,0))
        self._sg1.Add(wx.StaticText(self,-1,_("'Update Firmware' Options")),(3,0))
        
        self._jpptarg = wx.TextCtrl(self,ID_PTOPT,prefs.get("jptgarg") or pk2ptarg,size=(200,-1),name="ptargs")
        self._sg1.Add(self._jpptarg,(0,1))      
        self._jpidarg = wx.TextCtrl(self,ID_IDOPT,prefs.get("jpigarg") or pk2idarg,size=(200,-1),name="idargs")
        self._sg1.Add(self._jpidarg,(1,1))          
        self._jpvearg = wx.TextCtrl(self,ID_VEOPT,prefs.get("jpvearg") or pk2vearg,size=(200,-1),name="veargs")
        self._sg1.Add(self._jpvearg,(2,1))      
        self._jpuparg = wx.TextCtrl(self,ID_UPOPT,prefs.get("jpuparg") or pk2uparg,size=(200,-1),name="upargs")
        self._sg1.Add(self._jpuparg,(3,1))


        self._prefsave = wx.Button(self,ID_SAVEPREF,_("Save Preferences"),name = "Spref")             
        self._sbp1.Add(self._prefsave,1)
        self._prefdel = wx.Button(self,ID_DELPREFS,_("Clear Preferences"),name = "Dprefs")
        self._sbp1.Add(self._prefdel,1)
        
        if DEBUG is True:                                                                                                        
            self._prefvis = wx.Button(self,ID_LISTPREFS,_("Dictionary read"),name = "Lprefs")
            self._sbp1.Add(self._prefvis,1)

        # Layout
        self.__DoLayout()
        # Event Handlers
        self.Bind(wx.EVT_BUTTON,self.OnButton)

    def SavePrefs(self):
        cfg = Profile_Get(JPK2CMD_PREFS, default=dict())
        cfg["jptgarg"] = self.FindWindowByName("ptargs").GetValue()
        cfg["jpigarg"] = self.FindWindowByName("idargs").GetValue()
        cfg["jpvearg"] = self.FindWindowByName("veargs").GetValue()
        cfg["jpuparg"] = self.FindWindowByName("upargs").GetValue()
 
 
    def __DoLayout(self):
        """Layout the window"""
        vsizer = wx.BoxSizer(wx.VERTICAL)
        self._sbs.Add(self._pk2cmdloc,1,wx.EXPAND)
        self._sbs.Add(self._pk2datloc,1,wx.EXPAND)
 
        self._sbs1.Add(self._sg1,1,wx.EXPAND)
 
            
        vsizer.Add(self._sbs, 0, wx.EXPAND|wx.ALL, 8)
        vsizer.Add(self._sbs1, 0, wx.EXPAND|wx.ALL, 8)
        vsizer.Add(self._sbp1, 0, wx.EXPAND|wx.ALL, 8)
        
        self.SetSizer(vsizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()
        self.SetMinSize((550,445))
   
    def GetPrefs(self):
        prefs = Profile_Get(JPK2CMD_PREFS, default=None)
        if prefs is None:
           wx.MessageBox( _("Initializing preferences"),_("PicKit2"))
           # Seb: what about just letting environment (PATH) decides where to pick
           # pk2cmd ?
           Profile_Set(JPK2CMD_PREFS,dict(jpcmdloc = pk2cmdloc,
                                          jpdatloc = pk2datloc,
                                          jptgarg = pk2ptarg,
                                          jpidarg = pk2idarg,
                                          jpvearg = pk2vearg,
                                          jpuparg = pk2uparg
                                          ))
           # Seb: it should a dict so prefs.get() won't raise an error
           prefs = {}
        else:
            pass
        return prefs
        
    def OnFileSelected(self,evt):
        pk2cmdlocn = self._pk2cmdloc.GetValue()
        pk2datlocn = self._pk2datloc.GetValue()
        # save file in profile
        cfg = Profile_Get(JPK2CMD_PREFS, default=dict())
        cfg["jpcmdloc"] = pk2cmdlocn
        cfg["jpdatloc"] = pk2datlocn

    def OnButton(self,evt):
        e_id = evt.GetId()
        e_type = evt.GetEventType()
        e_name = evt.GetEventObject().GetName()
        #wx.MessageBox(str(e_id) + " tipo = " + str(e_type)+ " nome " + str(e_name),_("PicKit2"))
        if e_name == "Lprefs": # won't get called outside debug mode
            self.ListPK2Prefs()
        if e_name == "Dprefs": # won't get called outside debug mode
            self.DelPK2Prefs()
        if e_name == "Spref": # won't get called outside debug mode
            self.SavePrefs()

        
    def ListPK2Prefs(self): # only for debugging purpose
        cfg = Profile_Get(JPK2CMD_PREFS, default=dict())
        msg = _("Saved Preferences \n\n") 
        if len(cfg) == 0:
            msg = msg + _("No Saved Preferences")
        for k,v in cfg.iteritems():
            msg = msg + str(k)+" > " + str(v) + "\n \n"
        if "jpdatloc" in cfg:
            msg = msg + _("Location of PK2DeviceFile.dat ") + os.path.dirname(cfg.get("jpdatloc"))
        wx.MessageBox(msg,_("PicKit2"))    
        
    def DelPK2Prefs(self): # only for debugging purpose
        Profile_Set(JPK2CMD_PREFS, dict())    
    
