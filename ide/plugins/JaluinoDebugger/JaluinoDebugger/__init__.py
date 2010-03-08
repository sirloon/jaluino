###############################################################################
# Name: __init__.py                                                           #
# Purpose: JAL Debugger plugin                                                #
# Author: Albert Faber                                                        #
# Copyright: (c) 2010 Albert Faber                                            #
# Licence: BSD Licence                                                        #
###############################################################################
"""Jaluino debugger/simulator"""


import wx
import iface
import plugin
import ps_dbgview
from ed_menu import EdMenuBar, EdMenu
import platform

# Import Psyco if available
try:
	import psyco
	psyco.full()
except ImportError:
	pass
    
_ = wx.GetTranslation



#-----------------------------------------------------------------------------#

ID_DBGMENU = wx.NewId()
ID_DBGMENU_START = wx.NewId()
ID_DBGMENU_STEPINTO = wx.NewId()
ID_DBGMENU_STOP = wx.NewId()
ID_DBGMENU_CONTINUE = wx.NewId()
ID_DBGMENU_START_AND_RUN = wx.NewId()
ID_DBGMENU_RESTART = wx.NewId()

DBG_STATE_IDLE = 0
DBG_STATE_RUNNING = 1
DBG_STATE_PAUSED = 2

class Jaluino_debugger(plugin.Plugin):
    """Jaluino debugger/simulator"""
    plugin.Implements(iface.MainWindowI)
    def PlugIt(self, parent):
        """Adds the view menu entry registers the event handler"""
        
        self.bStepInto = False
        
        if parent:
            self.control = None

            # This will let you use Editra's loggin system
            self._log = wx.GetApp().GetLog()
            self._log("[Jaluino_debugger][info] Installing Jaluino_debugger")

            
            self._mw = parent
            bar = parent.GetMenuBar()
                        
            debug_menu = EdMenu()
            self.menuStartDebugger = debug_menu.Append(ID_DBGMENU_START        , _("&Start Debugger"))
            self.menuStartAndRunDebugger = debug_menu.Append(ID_DBGMENU_START_AND_RUN, _("&Start && Run Debugger"))
            self.menuStopDebugger = debug_menu.Append(ID_DBGMENU_STOP          , _("Sto&p Debugging"))
            #self.menuRestartDebugger = debug_menu.Append(ID_DBGMENU_RESTART    , _("&Restart"))
            self.menuContinueDebugger = debug_menu.Append(ID_DBGMENU_CONTINUE  , _("&Continue"))

            bar.Insert(bar.GetMenuCount() - 1,debug_menu,  _("&Debug"))
            
            self.UpdateMenu(DBG_STATE_IDLE)
            
        else:
            self._log("[Jaluino_debugger][err] Failed to install Jaluino_debugger plugin")

    def GetMenuHandlers(self):
        """This is used to register the menu handler with the app and
        associate the event with the parent window. It needs to return
        a list of ID/Handler pairs for each menu handler that the plugin
        is providing.

        """
        return [(ID_DBGMENU_START, self.StartDebugger),(ID_DBGMENU_START_AND_RUN, self.StartAndRunDebugger),(ID_DBGMENU_STOP, self.StopDebugger),(ID_DBGMENU_CONTINUE, self.ContinueDebugger)]

    def GetUIHandlers(self):
        """This is used to register the update ui handler with the app and
        associate the event with the parent window. This plugin doesn't use
        the UpdateUI event so it can just return an empty list.

        """
        return list()

    #-----------------------------------------------------------------------------#

    def UpdateMenu(self,state):
    	self._log("[JaluinoDebugger][info] UpdateMenu(%d)" % state)
    	if state == DBG_STATE_IDLE:
            self.menuStartDebugger.Enable( True )
            self.menuStartAndRunDebugger.Enable( True )
            self.menuStopDebugger.Enable( False )
            self.menuContinueDebugger.Enable( False )
            #self.menuRestartDebugger.Enable( False )
    	if state == DBG_STATE_RUNNING:
            self.menuStartDebugger.Enable( False )
            self.menuStartAndRunDebugger.Enable( False )
            self.menuStopDebugger.Enable( True )
            self.menuContinueDebugger.Enable( False )
            #self.menuRestartDebugger.Enable( True )
    	if state == DBG_STATE_PAUSED:
            self.menuStartDebugger.Enable( True )
            self.menuStartAndRunDebugger.Enable( True )
            self.menuStopDebugger.Enable( True )
            self.menuContinueDebugger.Enable( True )
            #self.menuRestartDebugger.Enable( True )

    def CloseDebugWindow(self):
    	self._log("[JaluinoDebugger][info] CloseDebugWindow")
    	self.control = None
    	self.UpdateMenu(DBG_STATE_IDLE)    	 
    
    def RestartDebugger(self,evt):
    	"""Restart the debugger"""
    	if evt.GetId() == ID_DBGMENU_RESTART:
    		self._log("[JaluinoDebugger][info] RestartDebugger")
    		
    		if self.control != None:
    			self.UpdateMenu(DBG_STATE_RUNNING)
    			self.control.debugView.restart( self.bStepInto) 		
    		
    		#if self.bStepInto == True:
    		#    self.UpdateMenu(DBG_STATE_PAUSED)
    		#else:
    		#    self.UpdateMenu(DBG_STATE_RUNNING)
    		

    def StopDebugger(self,evt):
    	"""Stop the debugger"""
    	if evt.GetId() == ID_DBGMENU_STOP:
    		self._log("[JaluinoDebugger][info] StopDebugger")
    		
    		if self.control != None:
    			self.control.debugView.stop() 		
    		
    		self.UpdateMenu(DBG_STATE_PAUSED)
		
    def ContinueDebugger(self,evt):
    	"""Continue the debugger"""
    	if evt.GetId() == ID_DBGMENU_CONTINUE:
    		self._log("[JaluinoDebugger][info] Continue")
    		
    		if self.control != None:
    			self.UpdateMenu(DBG_STATE_RUNNING)
    			self.control.debugView.run(False) 		

    def _StartAndRunDebugger(self, bStepInto):
		"""Start and run the debugger"""
		self.bStepInto = bStepInto

		createNew = False
		
		if ( self.control == None ):
			createNew = True
		else:
			if ( self.control.IsClosed  == True ):
			    createNew = True
		    			
		if ( createNew == True ):
			self.control = ps_dbgview.PsDebugView(self, self._mw, wx.ID_ANY)
			# self.LOG("[ed_pages][evt] New Page Created ID: %d" % self.control.GetId())
			#self.control.Hide()
			self._mw.GetNotebook().AddPage(self.control)
			self.control.Show()
			
		self.UpdateMenu( DBG_STATE_RUNNING )
		if ( self.control.NewSession(self.bStepInto) == False ):
			self.UpdateMenu(DBG_STATE_IDLE)


    def StartAndRunDebugger(self,evt):
    	"""Start and run the debugger"""

        self.bStepInto = False

    	if evt.GetId() == ID_DBGMENU_START_AND_RUN:
    		self._log("[JaluinoDebugger][info] Start and Run debugger")
    		self._StartAndRunDebugger(False)    		
    	else:
    		evt.Skip()

    			
    def StartDebugger(self,evt):
    	"""Startus the debugger"""

    	self.bStepInto = True

    	if evt.GetId() == ID_DBGMENU_START:
    		self._log("[JaluinoDebugger][info] Start debugger")
    		self._StartAndRunDebugger(True)    		
    	else:
    		evt.Skip()

    def OnBreak(self):
    	self.UpdateMenu(DBG_STATE_PAUSED)
