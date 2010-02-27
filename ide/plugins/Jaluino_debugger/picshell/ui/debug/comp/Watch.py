from picshell.engine.util.Format import Format
import  wx.lib.newevent
import wx


class Watch:
   def __init__(self, address,mode="bin",name="",varAdrMapping=None):
      
        self.address = Format.toNumber(address,varAdrMapping)
        # print "Create WATCH at address " + str( address ) + "=> %02X" % self.address

        self.ui = None
        self.mode = mode
        self.reset()
        self.name = name
        self.oldValue = -1
        self.type = "Watch"

   def reset(self):
        self.cpt = 0
        # let's say that value = None -> clear value
        wx.CallAfter(self.UpdateUI, None )
        
   def execute(self,value): 
       if value != self.oldValue:
           self.oldValue = value
           wx.CallAfter(self.UpdateUI, value )
           
   def UpdateUI(self, value):
       if ( self.ui != None ):
           self.ui.Clear() 
           if value != None :
               if ("bin" == self.mode):
                   self.ui.AppendText(Format.binf( value ) )
               elif ("hex" == self.mode):
                   self.ui.AppendText( "0x%0X" % value )
               elif ("dec" == self.mode):
                   self.ui.AppendText( "%0d" % value )
               
   def CreateUI(self,parent, psizer ):
        panel = wx.Panel(parent,-1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        label = wx.StaticText(panel,-1," " + self.name)
        self.ui = wx.TextCtrl(panel)
        self.ui.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.ui,0,0)
        sizer.Add(label,0,0)
        psizer.Add(panel,0,0)
          