from picshell.engine.util.Format import Format
import wx
import  wx.lib.newevent

class UARTReceiver:
    def __init__(self):
        self.type ="uartReceiver"
        self.dataReady = False
        self.address = 0x19 #TXREG
        
    # callbacks allow acces to emu's state
    def CreateUI(self,parent,psizer):
        mainPanel = wx.Panel(parent,-1,style=wx.NO_BORDER)
        #mainPanel.SetBackgroundColour("black")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainPanel.SetSizer(mainSizer)
        title = wx.StaticText(mainPanel,-1,"Basic UART Receiver")
        #title.SetForegroundColour("white")
        mainSizer.Add(title)
        panel = wx.Panel(mainPanel,-1,style=wx.NO_BORDER)
        mainSizer.Add(panel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        self.ui = wx.TextCtrl(panel,size=(200, 100),style=wx.TE_MULTILINE)
        self.ui.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.ui)
        clearBt= wx.Button(panel,-1,"Clear")
        clearBt.Bind(wx.EVT_BUTTON, self.OnClear)
        sizer.Add(clearBt)
        psizer.Add( mainPanel )
        

    def OnClear(self,event):
        self.reset()


    #
    # needed to be a byteMonitor
    # Called by emu State.regWrite() and absWrite()
    #
    def execute(self,value):  
        value = str(value)+"\n"
        wx.CallAfter(self.UpdateUI, chr( value ) )
    #
    # needed to be a byteMonitor
    # Called by emu State.regWrite() and absWrite()
    def reset(self):
        # value = None -> clear
        wx.CallAfter(self.UpdateUI, None )
    
    # Called by State.regRead
    # is output read to recieve ?
    # for TXIF
    def isReady(self):
        # this is a simulation... receiver is allways ready...
        return True 

    def setPic(self,pic):
        if pic.fsr_regs.has_key( "TXREG" ):
           self.address = pic.fsr_regs["TXREG"]

    def UpdateUI(self, value):
       if value != None :
           self.ui.AppendText(value)
       else:
           self.ui.Clear()

class ASCIIReceiver:
    def __init__(self):
        self.type ="uartReceiver"
        self.dataReady = False
        self.address = 0x19 #TXREG
        
    # callbacks allow acces to emu's state
    def CreateUI(self,parent,psizer):
        mainPanel = wx.Panel(parent,-1,style=wx.NO_BORDER)
        #mainPanel.SetBackgroundColour("black")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainPanel.SetSizer(mainSizer)
        title = wx.StaticText(mainPanel,-1,"Basic UART Receiver")
        #title.SetForegroundColour("white")
        mainSizer.Add(title)
        panel = wx.Panel(mainPanel,-1,style=wx.NO_BORDER)
        mainSizer.Add(panel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        self.ui = wx.TextCtrl(panel,size=(200, 100),style=wx.TE_MULTILINE)
        self.ui.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL))
        sizer.Add(self.ui)
        clearBt= wx.Button(panel,-1,"Clear")
        clearBt.Bind(wx.EVT_BUTTON, self.OnClear)
        sizer.Add(clearBt)        
        psizer.Add( mainPanel )

    def OnClear(self,event):
        self.reset()
        
    def setPic(self,pic):
        if pic.fsr_regs.has_key( "TXREG" ):
           self.address = pic.fsr_regs["TXREG"]
        
    #
    # needed to be a byteMonitor
    # Called by emu State.regWrite() and absWrite()
    #
    def execute(self,value):  
        if value != 13:
            wx.CallAfter(self.UpdateUI, chr( value ) )
    #
    # needed to be a byteMonitor
    # Called by emu State.regWrite() and absWrite()
    def reset(self):
        
        # value = None -> clear
        wx.CallAfter(self.UpdateUI, None )
    
    # Called by State.regRead
    # is output read to recieve ?
    # for TXIF
    def isReady(self):
        # this is a simulation... receiver is allways ready...
        return True 

    def UpdateUI(self, value):
           
       if value != None :
           self.ui.AppendText(value)
       else:
           self.ui.Clear()

class ASCIISender:
    def __init__(self):
        self.type ="asciiSender"
        self.dataReady = False
    
    
    # callbacks allow acces to emu's state
    def CreateUI(self,parent,psizer):
        
        mainPanel = wx.Panel(parent,-1,style=wx.NO_BORDER)
        #mainPanel.SetBackgroundColour("black")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainPanel.SetSizer(mainSizer)
        title = wx.StaticText(mainPanel,-1,"UART ASCII Sender")
        #title.SetForegroundColour("white")
        mainSizer.Add(title)
        panel = wx.Panel(mainPanel,-1,style=wx.NO_BORDER)
        mainSizer.Add(panel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        
        self.txtValue = wx.TextCtrl(panel,size=(100,-1))
        bSend = wx.Button(panel,-1,"Send")
        #sizer.Add(self.txtChanel)
        sizer.Add(self.txtValue)
        sizer.Add(bSend)

        bSend.Bind(wx.EVT_BUTTON, self.OnSend)
        psizer.Add( mainPanel )
        
    def OnSend(self,event):
        t2 = self.txtValue.GetValue()
        if t2 != "" :
           self.index = 0
          
           self.tab=[]
           for num in t2:
               self.tab.append(ord(num))
            
           self.dataReady = True

    #
    # Called by pic engine State.regRead(self,reg)
    #    
    def getNext(self):
         data = 1
         if (self.index < len(self.tab)):
             #print "data : "+str(self.tab[self.index])
             data = self.tab[self.index] 
         if self.index ==len(self.tab)-1:
             self.dataReady = False 
        
         self.index +=1
         return data
    #
    # Called by pic engine State.regRead(self,reg)
    #    
    def hasData(self):
        return self.dataReady

    def UpdateUI(self, value):
       if value != None :
           self.ui.AppendText(value)
       else:
           self.ui.Clear()

class ByteSender:
    def __init__(self):
        self.type ="byteSender"
        self.dataReady = False
       
    # callbacks allow acces to emu's state
    def CreateUI(self,parent,psizer):
        
        mainPanel = wx.Panel(parent,-1,style=wx.NO_BORDER)
        #mainPanel.SetBackgroundColour("black")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainPanel.SetSizer(mainSizer)
        title = wx.StaticText(mainPanel,-1,"UART BYTE Sender")
        #title.SetForegroundColour("white")
        mainSizer.Add(title)
        panel = wx.Panel(mainPanel,-1,style=wx.NO_BORDER)
        mainSizer.Add(panel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        
        self.txtValue = wx.TextCtrl(panel,size=(100,-1))
        bSend = wx.Button(panel,-1,"Send")
        #sizer.Add(self.txtChanel)
        sizer.Add(self.txtValue)
        sizer.Add(bSend)

        bSend.Bind(wx.EVT_BUTTON, self.OnSend)
        psizer.Add( mainPanel )
        
    def OnSend(self,event):
        t2 = self.txtValue.GetValue()
        if t2 != "":
            self.index = 0
            
            self.tab=[]
            for num in t2.split(","):
                num= num.strip()
                self.tab.append(Format.toNumber(num)&0xFF)
            self.dataReady = True

    #
    # Called by pic engine State.regRead(self,reg)
    #    
    def getNext(self):
         data = 1
         if (self.index < len(self.tab)):
             #print "data : "+str(self.tab[self.index])
             data = self.tab[self.index] 
         if self.index ==len(self.tab)-1:
             self.dataReady = False 
        
         self.index +=1
         return data
    #
    # Called by pic engine State.regRead(self,reg)
    #    
    def hasData(self):
        return self.dataReady

    
class MidiSender:
    def __init__(self):
        self.type ="midiSender"
        self.dataReady = False
        
    # callbacks allow acces to emu's state
    def CreateUI(self, parent, psizer ):
        
        mainPanel = wx.Panel(parent,-1,style=wx.NO_BORDER)
        #mainPanel.SetBackgroundColour("black")
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainPanel.SetSizer(mainSizer)
        title = wx.StaticText(mainPanel,-1,"Basic MIDI Sender")
        #title.SetForegroundColour("white")
        mainSizer.Add(title)
        panel = wx.Panel(mainPanel,-1,style=wx.NO_BORDER)
        mainSizer.Add(panel)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        
        #self.txtChanel = wx.TextCtrl(panel,size=(50,-1))
        self.txtCmd = wx.TextCtrl(panel,size=(50,-1))
       
        self.txtValue = wx.TextCtrl(panel,size=(50,-1))
        bSend = wx.Button(panel,-1,"Send")
        
        #sizer.Add(self.txtChanel)
        sizer.Add(self.txtCmd)
        sizer.Add(self.txtValue)
        sizer.Add(bSend)

        bSend.Bind(wx.EVT_BUTTON, self.OnSend)
        psizer.Add( mainPanel )
        
    def OnSend(self,event):
        self.index = 0
        t1 = self.txtCmd.GetValue()
        t2 = self.txtValue.GetValue()
        b1 = Format.toNumber(t1)
        b2 = Format.toNumber(t2)
        self.tab = [b1,b2]
        self.dataReady = True

    #
    # Called by pic engine State.regRead(self,reg)
    #    
    def getNext(self):
         data = 1
         if (self.index < 2):
             #print "data : "+str(self.tab[self.index])
             data = self.tab[self.index] 
         if self.index ==1:
             self.dataReady = False 
        
         self.index +=1
         return data
    #
    # Called by pic engine State.regRead(self,reg)
    #    
    def hasData(self):
        return self.dataReady

        