###############################################################################
# Name: __init__.py                                                           #
# Purpose: Hello World Sample Plugin                                          #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Copyright: (c) 2007 Cody Precord <staff@editra.org>                         #
# Licence: wxWindows Licence                                                  #
###############################################################################
"""Jaluino debugger/simulator"""
__author__ = "Albert Faber"
__version__ = "0.12"

import wx
import iface
import plugin
import ps_dbgview

from ed_menu import EdMenuBar


#from picshell.ui.PicShell import PicShell

import platform
if platform.machine()=='i386':
    import psyco
    psyco.full()

    
_ = wx.GetTranslation



#-----------------------------------------------------------------------------#

ID_DBGMENU = wx.NewId()
ID_DBGMENU_START = wx.NewId()
ID_DBGMENU_STOP = wx.NewId()
ID_DBGMENU_BREAKALL = wx.NewId()

class Jaluino_debugger(plugin.Plugin):
    """Jaluino debugger/simulator"""
    plugin.Implements(iface.MainWindowI)
    def PlugIt(self, parent):
        """Adds the view menu entry registers the event handler"""
        if parent:
            self.control = None
            # This will let you use Editra's loggin system
            self._log = wx.GetApp().GetLog()
            self._log("[Jaluino_debugger][info] Installing Jaluino_debugger")
            vm = parent.GetMenuBar().GetMenuByName("tools")
            vm.Append(ID_DBGMENU_START, _("Jaluino Debugger"), 
                      _("Open a Jaluino_debugger dialog"))
            self._mw = parent
                        
            debug_menu = wx.Menu()
            debug_menu.Append(ID_DBGMENU_START   , _("&Start Debugging"))
            debug_menu.Append(ID_DBGMENU_STOP    , _("Sto&p Debugging"))
            debug_menu.Append(ID_DBGMENU_BREAKALL, _("&Break All"))
            parent.GetMenuBar().Append(debug_menu, _("Debug"))
        else:
            self._log("[Jaluino_debugger][err] Failed to install Jaluino_debugger plugin")

    def GetMenuHandlers(self):
        """This is used to register the menu handler with the app and
        associate the event with the parent window. It needs to return
        a list of ID/Handler pairs for each menu handler that the plugin
        is providing.

        """
        return [(ID_DBGMENU_START, self.StartDebugger),(ID_DBGMENU_STOP, self.StopDebugger)]

    def GetUIHandlers(self):
        """This is used to register the update ui handler with the app and
        associate the event with the parent window. This plugin doesn't use
        the UpdateUI event so it can just return an empty list.

        """
        return list()

    #-----------------------------------------------------------------------------#

    def StopDebugger(self,evt):
    	"""Startus the debugger"""
    	if evt.GetId() == ID_DBGMENU_STOP:
    		print "StopDebugger "
    		print evt.GetId()
    		if self.control != None:
    		   self.control.debugView.stop() 		

    def StartDebugger(self,evt):
    	"""Startus the debugger"""
    	if evt.GetId() == ID_DBGMENU_START:
    		print "StartDebugger "
    		print evt.GetId()
    		
    		createNew = False
    		
    		if ( self.control == None ):
    			print "StartDebugger  1"
    			createNew = True
    		else:
    			print "StartDebugger  2 isClosed is "
    			print self.control.IsClosed
    			if ( self.control.IsClosed  == True ):
	    			print "StartDebugger  3"
	    			createNew = True
    		
    		print "createNew ..."
    		print createNew
    			
    		if ( createNew == True ):
    			self.control = ps_dbgview.PsDebugView(self, self._mw, wx.ID_ANY)
    			# self.LOG("[ed_pages][evt] New Page Created ID: %d" % self.control.GetId())
    			#self.control.Hide()
    			self._mw.GetNotebook().AddPage(self.control)
    			self.control.Show()
    		else:
    			self.control.NewSession()
    	else:
    		evt.Skip()

