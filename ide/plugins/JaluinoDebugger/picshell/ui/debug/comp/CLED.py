import  wx.lib.newevent
import wx

from picshell.ui.Context import Context
from picshell.engine.util.Format import Format
from picshell.util.FileUtil import FileUtil

import picshell.icons.embedded_icons


class CLED:
   # bit in 1,2,4,8,16,32,64,128
   #
   def __init__(self,ui,on,off,address,bit,name="",color="red",varAdrMapping=None):

        self.varname = address
        self.address = Format.toNumber(str(address),varAdrMapping)
        self.bit = bit
        # print "Create LED at address " + str( address ) + "=> %02X" % self.address + " bit %d" % bit
        self.color = color
        self.oldValue = -1
        self.name = name
        self.off = on
        self.on = off
        self.ui = ui
        self.reset()      
        self.type = "CLED"
        
   def reset(self):
        self.cpt = 0
        
   def execute(self,value): 
       # print "CLED Execute value %02X" % value + " MY ADDRESS %04X" % self.address
       value = value & self.bit

       if value != self.oldValue:
           self.oldValue = value
           wx.CallAfter(self.UpdateUI, value )

   def UpdateUI(self,value): 
        if value > 0 :
            self.ui.SetBitmap(self.on)
        else :
            self.ui.SetBitmap(self.off)

   def CreateUI(self,parent, psizer ):

        self.off =  picshell.icons.embedded_icons.gray_icon.GetBitmap()

        col = self.color

        if col == "red" :
            self.on =  picshell.icons.embedded_icons.red_icon.GetBitmap()
        elif col == "blue" :
            self.on =  picshell.icons.embedded_icons.blue_icon.GetBitmap()
        elif col == "green" :
            self.on =  picshell.icons.embedded_icons.green_icon.GetBitmap()
        elif col == "orange" :
            self.on =  picshell.icons.embedded_icons.orange_icon.GetBitmap()
        elif col == "yellow" :
            self.on =  picshell.icons.embedded_icons.yellow_icon.GetBitmap()


        panel = wx.Panel(parent,-1)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        label = wx.StaticText(panel,-1," " + self.name)
        self.ui = wx.StaticBitmap(panel, -1, self.off, (10, 0), (self.off.GetWidth(), self.off.GetHeight()))
        sizer.Add(self.ui,0,0)
        sizer.Add(label,0,0)
        psizer.Add(panel,0,0)
