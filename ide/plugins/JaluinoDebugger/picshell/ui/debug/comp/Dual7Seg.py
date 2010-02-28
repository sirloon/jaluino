# Address monitor
import wx
import  wx.lib.newevent

from wx import gizmos
from picshell.engine.util.Format import Format


class Dual7Seg:
   def __init__(self,ui,address,razBit,uniteeBit,deciBit,name=""):
        self.address = Format.toNumber(address)
        self.ui = ui
        self.unitee=0;
        self.deci=0;
        self.oldIncUnitee = 0
        self.oldRaz = 0
        self.oldIncDeci = 0
        self.razBit = razBit
        self.uniteeBit = uniteeBit
        self.deciBit = deciBit
        self.name = name
        self.type="Dual7Seg"
        self.reset()
        
   def reset(self):
        if (self.ui != None):
            wx.CallAfter(self.UpdateUI, "00" )
            
   def execute(self,value):  
       raz = value & pow(2,self.razBit)
       incUnitee = value & pow(2,self.uniteeBit)
       incDeci = value & pow(2,self.deciBit)
       
       if raz > 0 and self.oldRaz == 0:
            self.unitee = 0
            self.deci = 0
       if incUnitee >0 and self.oldIncUnitee == 0: 
           self.unitee += 1
           if (self.unitee > 9):
               self.unitee = 0
       if incDeci >0 and self.oldIncDeci == 0 :
           self.deci += 1
           if (self.deci > 9):
               self.deci = 0

       val = str(self.deci)+str(self.unitee)
       wx.CallAfter(self.UpdateUI, val )
       
       self.oldRaz = raz
       self.oldIncUnitee = incUnitee
       self.oldIncDeci = incDeci
           
   def UpdateUI(self, value):
       self.ui.SetValue(value)
           
   def CreateUI(self,parent, psizer ):

        panel = wx.Panel(parent,-1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        label = wx.StaticText(panel,-1," " + self.name)
        #ui = wx.TextCtrl(panel)
        #ui.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
        
        self.ui = gizmos.LEDNumberCtrl(panel, -1, (25,25), (280, 50))
        
        sizer.Add(self.ui,0,0)
        sizer.Add(label,0,0)
        psizer.Add(panel,0,0)
           
