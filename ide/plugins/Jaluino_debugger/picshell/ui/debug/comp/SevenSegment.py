# Address monitor
import wx

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
       #self.ui.Clear()
       val = str(self.deci)+str(self.unitee)

       wx.CallAfter(self.UpdateUI, val )
       
       self.oldRaz = raz
       self.oldIncUnitee = incUnitee
       self.oldIncDeci = incDeci
           