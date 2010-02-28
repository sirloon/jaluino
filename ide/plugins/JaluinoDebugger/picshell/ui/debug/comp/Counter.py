# Address monitor
from picshell.engine.util.Format import Format
import  wx.lib.newevent
import wx


class UpDownCounter:
   def __init__(self,ui,address,selectBit,incBit,upDownBit,max,name="",csBar=False):
        
        self.address = Format.toNumber(address)
        self.ui = ui
        self.selectBit =selectBit
        self.incBit =incBit
        self.upDownBit = upDownBit
        self.max = max
        self.name=name
        self.reset()
        self.type="UpDownCounter"
        self.oldIncBit = 0
        self.csBar = csBar
        
   def reset(self):
        self.cpt = 0
        if (self.ui != None):
            wx.CallAfter(self.UpdateUI, None )       

   def execute(self,value):
       select = value & pow(2,self.selectBit)
       incBit = value & pow(2,self.incBit)
       upDown = value & pow(2,self.upDownBit)
       
       
       if self.csBar :
           cs = (select == 0)  
       else :
           cs = (select > 0)  
       
       if cs:
           if incBit > 0 and self.oldIncBit == 0: # up edge
               if (upDown>0):
                   if self.cpt < self.max :
                       self.cpt += 1
               else:
                   if self.cpt > 0:
                       self.cpt -= 1
       
       wx.CallAfter(self.UpdateUI, str(self.cpt) )       
       self.oldIncBit = incBit

   def UpdateUI(self,value): 
       self.ui.Clear() 
       if value != None :
          self.ui.AppendText( value )

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
        