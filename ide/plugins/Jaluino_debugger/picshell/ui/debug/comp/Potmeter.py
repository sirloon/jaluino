from picshell.engine.util.Format import Format
import wx

class Potmeter:
    def __init__( self,name,pin ):
        self.type = "potmeter"
        self.name = name
        self.pin = pin
        self.callbackWriteAdc = None

        
    def OnChange(self,event):  
        bt = event.GetEventObject()
        self.callbackWriteAdc( self.pinNumber, bt.GetValue() )
        event.Skip()
        
    def CreateUI(self,parent, psizer ):    

        panel = wx.Panel(parent,-1)
	        
        slider =wx.Slider(panel, -1, 0, 0, 1023, wx.DefaultPosition, (250, -1), wx.SL_HORIZONTAL | wx.SL_LABELS)
        slider.SetToolTipString( self.pin )
        slider.Bind( wx.EVT_SCROLL, self.OnChange )

        # af TODO, does not work for pin numbers >= 10        
        self.pinNumber = self.pin[5] #pin as format : 'pin_aX'
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        label = wx.StaticText(panel,-1," " + self.name)
        sizer.Add(slider,0,0)
        sizer.Add(label,0,0)
        psizer.Add(panel,0,0)
