from picshell.engine.util.Format import Format
import wx

class MomentarySwitch:
    def __init__( self,name,pin,type):
        self.type = type
        self.name = name
        self.pin = pin
        self.callbackRead = None
        self.callbackWrite = None

    def SetBit(self,lowhigh ):  
        reg = self.callbackRead( self.port_addr )
        if lowhigh == False:
            self.callbackWrite( self.port_addr, reg & ( 255 - self.bit ) )
        else:
            self.callbackWrite( self.port_addr, reg | self.bit)
            

    def OnClickDown(self,event):  
        if self.type == "mpd":
            self.SetBit( True )
        if self.type == "mpu":
            self.SetBit( False )
        
        event.Skip()
        
    def OnClickUp(self,event):  
        if self.type == "mpd":
            self.SetBit( False )
        if self.type == "mpu":
            self.SetBit( True )
        event.Skip()
        
    def CreateUI(self,parent, psizer ):    
        but = wx.Button(parent, -1, self.name)
        but.SetToolTipString(self.pin)
        but.Bind(wx.EVT_LEFT_DOWN, self.OnClickDown)
        but.Bind(wx.EVT_LEFT_UP, self.OnClickUp)
        psizer.Add(but)

        port = "PORT" + self.pin[4]
        self.bit = pow(2,(ord(self.pin[5])-48))
        self.port_addr = Format.toNumber(port,None)        

        if self.type == "mpd":
            self.SetBit( False )
        if self.type == "mpu":
            self.SetBit( True )

