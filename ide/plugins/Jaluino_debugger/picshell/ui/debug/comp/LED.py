from picshell.engine.util.Format import Format
import  wx.lib.newevent
import wx

class LED:
   # bit in 1,2,4,8,16,32,64,128
   #
   def __init__(self,ui,address,bit,name="",varAdrMapping=None):
      
        self.address = Format.toNumber(str(address),varAdrMapping)
        self.ui = ui
        self.bit = bit
        
        self.reset()
        self.oldValue = -1
        self.name = name
        self.type = "LED"
        self.oldValue = -1

   def reset(self):
        self.cpt = 0
        if self.ui != None :
           # let's say that value = None -> clear value
           wx.CallAfter(self.UpdateUI, None )
            
        
   def execute(self,value): 
       value = value & self.bit
       
       if value != self.oldValue:
           wx.CallAfter(self.UpdateUI, value )
           
   def UpdateUI(self,value): 
       self.ui.Clear() 
       if value != None :
          if value != self.oldValue :
              self.oldValue = value
              if value > 0 :
                  self.ui.SetValue("On")
              else :
                  self.ui.SetValue("Off")

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
           