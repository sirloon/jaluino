from picshell.engine.util.Format import Format
from picshell.ui.Context import Context
import  wx.lib.newevent
import wx

class StaticText:
   def __init__(self, type, name ):      
        self.ui = None
        self.type = "StaticText"
        self.name = name
        self.type = type
               
   def CreateUI(self,parent, psizer ):
        self.ui = wx.StaticText( parent, -1, self.name )
        psizer.Add(self.ui,0,0)
          