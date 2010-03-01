from picshell.engine.core.PicEngine import PicEngine
from picshell.engine.core.PicThreadEngine import PicThreadEngine
from picshell.engine.util.Format import Format
from picshell.parser.AnnotationParser import AnnotationParser
from picshell.parser.JalV2AsmParser import JalV2AsmParser
from picshell.parser.JalV2Parser import JalV2Parser
from picshell.ui.Context import Context
from picshell.monitors.RegisterUpdater import RegisterUpdater
from picshell.monitors.DeviceStateMonitors import DeviceSourceStateMonitor
from picshell.monitors.DeviceStateMonitors import DeviceTargetStateMonitor
from picshell.ui.debug.comp.CLED import CLED
from picshell.ui.debug.comp.Counter import UpDownCounter
from picshell.ui.debug.comp.Dual7Seg import Dual7Seg
from picshell.ui.debug.comp.LCD import LCD
from picshell.ui.debug.comp.StaticText import StaticText
from picshell.ui.debug.comp.LED import LED
from picshell.ui.debug.comp.Watch import Watch
from picshell.ui.edit.EditorUtil import EditorUtil
from picshell.util.AssertUtil import AssertUtil
from picshell.util.DocHelper import AsmDocHelp
from picshell.util.FileUtil import FileUtil
from picshell.engine.core.pics import PicFactory
from wx._gdi import HOURGLASS_CURSOR
from wx._gdi import STANDARD_CURSOR
from wx.stc import STC_EOL_CRLF
import  wx.lib.newevent
from zipfile import ZipFile
import zipfile
# import JALsPy_globals
import os
import platform
import re
import subprocess
import sys
import time
import wx

from picshell.ui.debug.DrawWindow import DrawWindow


class DebugView :

    MY_EVT_CALLBACK = None
    (UpdateCallbackEvent, MY_EVT_CALLBACK) = wx.lib.newevent.NewEvent()

    COL_ADR = 0
    COL_RUN = 1
    COL_BP = 2
    COL_CODE = 3
    COL_COM = 4
    
    ID_PSD_NEXT_ASM = wx.NewId()
    ID_PSD_NEXT_SRC = wx.NewId()
    ID_PSD_NEXT_STEPOVER = wx.NewId()

    
    def __init__(self,parent,uiManager):

        self.emu = None
        self.breakpoints = {}
        self.threadEngine = None
        self.listBreakpoint = None
        self.running = False
        self.listLang = None
        self.drawWindow = None
        self.Quit = False

        self.inOutPanel = None
        self.inOutSizer = None
        self.curCycles = 0
        self.varTypeDict = None
        self.devices = []
        self.plugins = []

        # debug view
        self.mainSplitter = wx.SplitterWindow(parent, -1,style=wx.NO_BORDER)
        topSplitter = wx.SplitterWindow(self.mainSplitter, -1) # jal / asm splitter
        bottomSplitter = wx.SplitterWindow(self.mainSplitter, -1)
        
        
        self.bottomSplitter = bottomSplitter
        self.topSplitter = topSplitter

        self.oldWatchedValues={} # to save watched value so that we can color value that changed
        self.oldWatchedVars = {}
        self.listWatchVars = None
        self.listWatchRegs = None
        self.watchedReg = set()

       
        # -------------------------------------------------------
        # ASM Debug list  panel
        #
        panelAsm = wx.Panel(topSplitter, -1, style=wx.NO_BORDER)
        vboxAsm = wx.BoxSizer(wx.VERTICAL)
        panelAsm.SetSizer(vboxAsm)

        self.listAsm =  wx.ListCtrl(panelAsm, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        self.listAsm.InsertColumn(self.COL_RUN, ' ')
        self.listAsm.InsertColumn(self.COL_BP, 'BP')
        self.listAsm.InsertColumn(self.COL_ADR, 'Addr')
        self.listAsm.InsertColumn(self.COL_CODE, 'ASM Code')
        self.listAsm.InsertColumn(self.COL_COM, '')
        self.listAsm.SetColumnWidth(self.COL_RUN, 20)
        self.listAsm.SetColumnWidth(self.COL_BP, 30)
        self.listAsm.SetColumnWidth(self.COL_ADR, 60)
        self.listAsm.SetColumnWidth(self.COL_CODE, 200)
        self.listAsm.SetColumnWidth(self.COL_COM, 600)
        self.listAsm.Bind(wx.EVT_LEFT_DCLICK, self.OnBreakPointAsm)
        vboxAsm.Add(self.listAsm, -1,wx.EXPAND, 0 )
        self.bNextAsm = wx.Button(panelAsm,id=DebugView.ID_PSD_NEXT_ASM, label='Next [F5]')
        
        vboxAsm.Add(self.bNextAsm)

        # -------------------------------------------------------
        # JAL Debug code list  panel
        #
        panelLang = wx.Panel(topSplitter, -1, style=wx.NO_BORDER)
        vboxLang  = wx.BoxSizer(wx.VERTICAL)
        self.listLang =  wx.ListCtrl(panelLang, -1, style=wx.LC_REPORT)
        self.listLang.InsertColumn(self.COL_RUN, '')
        self.listLang.InsertColumn(self.COL_BP, 'BP')
        self.listLang.InsertColumn(self.COL_ADR, 'Addr')
        self.listLang.InsertColumn(self.COL_CODE, 'Code')
        self.listLang.SetColumnWidth(self.COL_RUN, 20)
        self.listLang.SetColumnWidth(self.COL_BP, 30)
        self.listLang.SetColumnWidth(self.COL_ADR, 60)
        self.listLang.SetColumnWidth(self.COL_CODE, 600)
        self.listLang.Bind(wx.EVT_LEFT_DCLICK, self.OnBreakPointLang)
        self.listLang.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListLangSelected)
        
        vboxLang.Add(self.listLang, -1,wx.EXPAND, 0 )
        
        panelButtonLang = wx.Panel(panelLang, -1, style=wx.NO_BORDER)
        vBoxLangButton = wx.BoxSizer(wx.HORIZONTAL)
        panelButtonLang.SetSizer(vBoxLangButton)
        self.bNextLang = wx.Button(panelButtonLang,id=DebugView.ID_PSD_NEXT_SRC,label='Next [F6]')
        # self.bNextLangStepOver = wx.Button(panelButtonLang,id=DebugView.ID_PSD_NEXT_STEPOVER,label='Step over')
        vBoxLangButton.Add(self.bNextLang,0)
        #vBoxLangButton.Add(self.bNextLangStepOver,0) # not woking good enougth for now
        
        vboxLang.Add(panelButtonLang,0)
        
        
        #action
        self.mainSplitter.Bind(wx.EVT_BUTTON, self.OnNextAsm,id=DebugView.ID_PSD_NEXT_ASM)
        self.mainSplitter.Bind(wx.EVT_BUTTON, self.OnNextLang, id=DebugView.ID_PSD_NEXT_SRC)
        self.mainSplitter.Bind(wx.EVT_BUTTON, self.OnNextLangStepOver, id=DebugView.ID_PSD_NEXT_STEPOVER)
        
        
        panelLang.SetSizer(vboxLang)
                
        # -------------------------------------------------------
        # REG WATCH Panel
        #
        watchTab = wx.Notebook(bottomSplitter,-1,style=wx.NO_BORDER)
        # adr panel 
        panelRegs = wx.Panel(watchTab, -1 ,  style=wx.NO_BORDER)
        panelRegs.SetBackgroundColour(wx.WHITE)
        vboxRegs  = wx.BoxSizer(wx.VERTICAL)
        panelRegs.SetSizer(vboxRegs)
        self.regFilter =  wx.TextCtrl(panelRegs, -1, "")
        self.regFilter.SetToolTip(wx.ToolTip("Register filter, use , separtor to show several expression.\nuse .. to display a range of register. example : 2..5\nuse *nb to cumulate byte, example: 0x30*2"))
        self.regFilter.Bind(wx.EVT_TEXT, self.OnRegFilterKeyDown)
        vboxRegs.Add(self.regFilter, 0, wx.EXPAND)
        
        self.listWatchRegs =  wx.ListCtrl(panelRegs, -1, style=wx.LC_REPORT)
        self.listWatchRegs.InsertColumn(0, 'Reg')
        self.listWatchRegs.InsertColumn(1, 'Values')
        self.listWatchRegs.InsertColumn(2, 'Comment')
        self.listWatchRegs.SetColumnWidth(0, 100)
        self.listWatchRegs.SetColumnWidth(1, 150)
        self.listWatchRegs.SetColumnWidth(2, 250)
        
        vboxRegs.Add(self.listWatchRegs, -1,wx.EXPAND, 0 )

        # vars panel
        panelVars = wx.Panel(watchTab, -1, style=wx.NO_BORDER)
        panelVars.SetBackgroundColour(wx.WHITE)
        vboxVars  = wx.BoxSizer(wx.VERTICAL)
        panelVars.SetSizer(vboxVars)
        self.varFilter =  wx.TextCtrl(panelVars, -1, "")
        self.varFilter.SetToolTip(wx.ToolTip("Variable filter, use , separtor to show several vars"))
        self.varFilter.Bind(wx.EVT_TEXT, self.OnVarFilterKeyDown)
        vboxVars.Add(self.varFilter, 0, wx.EXPAND)

        self.listWatchVars =  wx.ListCtrl(panelVars, -1, style=wx.LC_REPORT)
        self.listWatchVars.InsertColumn(0, 'Vars')
        self.listWatchVars.InsertColumn(1, 'Type')
        self.listWatchVars.InsertColumn(2, 'Values')
        self.listWatchVars.InsertColumn(3, 'Addr.')
        self.listWatchVars.SetColumnWidth(0, 150)
        vboxVars.Add(self.listWatchVars, -1,wx.EXPAND, 0 )
        
        # data eeprom panel
        panelDataEEProm = wx.Panel(watchTab, -1, style=wx.NO_BORDER)
        panelDataEEProm.SetBackgroundColour(wx.WHITE)
        vboxEEProm  = wx.BoxSizer(wx.VERTICAL)
        panelDataEEProm.SetSizer(vboxEEProm)
        self.dataEEPromFilter =  wx.TextCtrl(panelDataEEProm, -1, "")
        self.dataEEPromFilter.SetToolTip(wx.ToolTip("Use , separtor to show several expression.\nuse .. to display a range. example : 2..5"))
        self.dataEEPromFilter.Bind(wx.EVT_TEXT, self.OnEEPromFilterKeyDown)
        vboxEEProm.Add(self.dataEEPromFilter, 0, wx.EXPAND)

        self.listWatchDataEEProm =  wx.ListCtrl(panelDataEEProm, -1, style=wx.LC_REPORT)
        self.listWatchDataEEProm.InsertColumn(0, 'Addr.')
        self.listWatchDataEEProm.InsertColumn(1, 'Values')
        vboxEEProm.Add(self.listWatchDataEEProm, -1,wx.EXPAND, 0 )
        
        # Breakpoints
        bpPanel = wx.Panel(watchTab, -1 ,  style=wx.NO_BORDER)
        bpPanel.SetBackgroundColour(wx.WHITE)
        bpSizer  = wx.BoxSizer(wx.VERTICAL)
        bpPanel.SetSizer(bpSizer)
        self.listBreakpoint =  wx.ListCtrl(bpPanel, -1, style=wx.LC_REPORT)
        self.listBreakpoint.InsertColumn(0, 'Addr.')
        self.listBreakpoint.InsertColumn(1, 'Line')
        self.listBreakpoint.SetColumnWidth(1, 280)
        #self.listBreakpoint.Bind(wx.EVT_LEFT_DCLICK, self.OnlistBreakPointDClick)
        self.listBreakpoint.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnlistBreakPointSelected)

        bpSizer.Add(self.listBreakpoint, -1,wx.EXPAND, 0 )        
        self.bpRemoveAll = wx.Button(bpPanel,-1,"Remove all")
        self.bpRemoveAll.Bind(wx.EVT_BUTTON, self.OnRemoveAllBreakpoints)
        bpSizer.Add(self.bpRemoveAll, 0, 0)


        #Unit Test
        unitTestPanel = wx.Panel(watchTab, -1 ,  style=wx.NO_BORDER)
        self.listUnitTest =  wx.ListCtrl(unitTestPanel, -1, style=wx.LC_REPORT)
        self.listUnitTest.InsertColumn(0, 'Test name')
        self.listUnitTest.InsertColumn(1, 'Status')
        self.listUnitTest.InsertColumn(2, 'Comment')
        
        self.listUnitTest.SetColumnWidth(1, 50)
        self.listUnitTest.SetColumnWidth(2, 400)
        
        unitTestSizer  = wx.BoxSizer(wx.VERTICAL)
        unitTestPanel.SetSizer(unitTestSizer)
        unitTestSizer.Add(self.listUnitTest, -1,wx.EXPAND, 0 )     

        self.drawWindow = DrawWindow(watchTab)
        
        panelAsmExplain = wx.Panel(watchTab, -1 ,  style=wx.NO_BORDER)
        explainAsmText = wx.TextCtrl(panelAsmExplain,style=wx.TE_MULTILINE);
        panelAsmExplainSizer = wx.BoxSizer(wx.VERTICAL);
        panelAsmExplain.SetSizer(panelAsmExplainSizer);
        panelAsmExplainSizer.Add(explainAsmText,-1,wx.EXPAND)
        explainAsmText.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.explainAsmText =  explainAsmText
        
        watchTab.AddPage(panelVars,"Vars")
        watchTab.AddPage(panelRegs,"Regs")
        watchTab.AddPage(panelDataEEProm,"Data EEPROM")
        watchTab.AddPage(unitTestPanel,"Unit Testing")
        watchTab.AddPage(bpPanel,"Breakpoints")
        watchTab.AddPage(self.drawWindow,"Devices")
        watchTab.AddPage(panelAsmExplain,"ASM Explainer")

        self.nodesForAddress = [0]*1024*128
        self.devicesForAddressRead = [0]*1024*128
        self.devicesForAddressWrite = [0]*1024*128

        for i in range(0,1024*128):
            self.nodesForAddress[i] = None
            self.devicesForAddressRead[i] = None
            self.devicesForAddressWrite[i] = None
        

        # -------------------------------------------------------
        # IN / OUT Panel
        #
        
        panelInOut = wx.ScrolledWindow(bottomSplitter, -1,  style=wx.NO_BORDER)  
        vboxInOut  = wx.FlexGridSizer(vgap = 0, hgap = 20 )
        vboxInOut.SetCols(2)
        panelInOut.SetSizerAndFit(vboxInOut)
        panelInOut.SetScrollRate(1,1)
        panelInOut.SetBackgroundColour(wx.WHITE)
        panelInOut.SetSizerAndFit(vboxInOut)
        self.inOutPanel = panelInOut
        self.inOutSizer = vboxInOut 

        # -------------------------------------------------------
        # Split both windows 
        #
        topSplitter.SplitVertically(panelAsm, panelLang)
        bottomSplitter.SplitVertically(watchTab, panelInOut)
        
        self.mainSplitter.SplitHorizontally(topSplitter,bottomSplitter)
        
        self.listAsm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.listLang.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))
        
        self.listWatchRegs.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))
        self.listWatchVars.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL)) 
        self.listWatchDataEEProm.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL)) 
        self.listBreakpoint.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL)) 
        
        listAsm = self.listAsm
        
        self.mainSplitter.SetMinimumPaneSize(100)
        topSplitter.SetMinimumPaneSize(100)
        bottomSplitter.SetMinimumPaneSize(100)
        bottomSplitter.SetSashGravity(0.5)
        topSplitter.SetSashGravity(0.5)
        self.mainSplitter.SetSashGravity(0.5)
        self.uiManager = uiManager
        self.asmParser = JalV2AsmParser()
        
    def OnNextAsm(self,event):
        self.nextAsm()
    def OnNextLang(self,event):
        self.nextLang()
    def OnNextLangStepOver(self,event):
        self.nextStepOverLang()
        
                            
    def getView(self):
        return self.mainSplitter
        

    def Clear( self ):   
        self.oldWatchedValues={} # to save watched value so that we can color value that changed
        self.oldWatchedVars = {}
        self.watchedReg =set()
        self.listWatchVars.DeleteAllItems()
        self.listWatchRegs.DeleteAllItems()
        self.listWatchDataEEProm.DeleteAllItems()
        self.listAsm.DeleteAllItems()
        self.listLang.DeleteAllItems()

    #----------------------------------------------------------------
    # Watched Regs / Vars
    #
    def updateWatchVarView( self ):   
        format4 ="%4d"
        format2 = "0x%02X"
        self.listWatchVars.DeleteAllItems()
    
        # display var list
        self.listWatchVars.InsertStringItem(0,"PC")
        self.listWatchVars.SetStringItem(0,2, format2  %self.emu.state.getPc())
        
        font = self.listWatchVars.GetItemFont(0)
        font.SetWeight(wx.BOLD)
        self.listWatchVars.InsertStringItem(1,"W")
        self.listWatchVars.SetStringItem(1,2, format2 % self.emu.state.getW())
        self.listWatchVars.InsertStringItem(2,"STATUS")
        self.listWatchVars.SetStringItem(2,2, Format.binf(self.emu.state.getStatus()))
        self.listWatchVars.SetItemFont(0,font)
        self.listWatchVars.SetItemFont(1,font)
        self.listWatchVars.SetItemFont(2,font)
        index = 3
        if hasattr(self,"langParser"):
            for var in sorted(self.langParser.varAdrMapping):
                varDispType ="h:"
                varName = var.replace("v_","")
                show = False
                filters = self.varFilter.GetValue()
                if (filters.strip() != ""):
                    for filter in filters.split(","):
                        filter = filter.strip()
                        filter = filter.upper()
                        
                        if filter.startswith("B:"):
                            filter = filter[2:]
                            varDispType="b:"
                        elif filter.startswith("H:") or filter.startswith("0X"):
                            filter = filter[2:]
                            varDispType="h:"
                        elif filter.startswith("D:"):
                            filter = filter[2:]
                            varDispType="d:"
                        
                        if varName.upper().startswith(filter):
                            show = True
                else:
                    show =True
                
                if (show):
                    self.listWatchVars.InsertStringItem(index,varName)
                    adr = self.langParser.varAdrMapping[var]
                    
                    type= ""

                    if hasattr(self, "varTypeDict") and self.varTypeDict != None and self.varTypeDict.has_key(varName):
                        type = self.varTypeDict[varName]
                    else:
                        type = "? (byte)"
                    type = type.upper()  
                    self.listWatchVars.SetStringItem(index,1,type )
                    
                    # BIT - 1 bit
                    # BYTE - 8 bit, unsigned
                    # SBYTE - 8 bit, signed
                    # WORD - 16 bit, unsigned
                    # SWORD - 16 bit, signed
                    # DWORD - 32 bit, unsigned
                    # SDWORD - 32 bit, signed
                    # user defined : [S]BYTE*n, creates an n-BYTE signed            
                    
                    val = self.emu.varValue(adr,type)  
                    valAsStr = str(val)
                    if (varDispType =="b:") :
                        valAsStr = Format.binf(val)
                    if (varDispType =="h:") :
                        valAsStr = "0x%X" % val
                    
                        
                    self.listWatchVars.SetStringItem(index,2,valAsStr )
                    self.listWatchVars.SetStringItem(index,3,format2 % adr )
                    
                    # Highlight changes
                    changed = True
                    if self.oldWatchedVars.has_key(var):
                        if val != self.oldWatchedVars[var]:
                            changed = True
                        else:
                            changed = False
                    if changed :
                        self.listWatchVars.SetItemTextColour(index,"#FF0000")
                    else:
                        self.listWatchVars.SetItemTextColour(index,"#000000")
                    self.oldWatchedVars[var] = val
                    index +=1

    # -------------------------------------------------------------------------
    #
    #
    def updateWatchRegView(self):
        self.listWatchRegs.DeleteAllItems()
        format4 ="%4d"
        format2 = "0x%02X"
        self.listWatchRegs.InsertStringItem(0,"PC")
        self.listWatchRegs.SetStringItem(0,1, "0x%X"  % self.emu.state.getPc())
        self.listWatchRegs.SetStringItem(0,2, "%d"  % self.emu.state.getPc())
        
        font = self.listWatchRegs.GetItemFont(0)
        font.SetWeight(wx.BOLD)
        self.listWatchRegs.InsertStringItem(1,"W")
        self.listWatchRegs.SetStringItem(1,1, format2 % self.emu.state.getW())
        self.listWatchRegs.SetStringItem(1,2, format4 % self.emu.state.getW())
        
        self.listWatchRegs.InsertStringItem(2,"STATUS")        
        statusValue = self.emu.state.getStatus()
        self.listWatchRegs.SetStringItem(1,2, format4 % statusValue )
        
        bs = Format.bin(statusValue)
        status="IRP=%s, RP1=%s, RP0=%s, TO=%s" %(bs[0],bs[1],bs[2],bs[3])
        status2="PD=%s, Z=%s, DC=%s, C=%s" %(bs[4],bs[5],bs[6],bs[7])
        self.listWatchRegs.SetStringItem(2,2, status)
        self.listWatchRegs.InsertStringItem(3,"")
        self.listWatchRegs.SetStringItem(3,2, status2)
        
        self.listWatchRegs.SetItemFont(0,font)
        self.listWatchRegs.SetItemFont(1,font)
        self.listWatchRegs.SetItemFont(2,font)
        self.listWatchRegs.SetItemFont(3,font)
        index = 4

        regs = set()
        regsType = {}
        filters = self.regFilter.GetValue()
        regTxt = []
        if (filters.strip() != ""):
            regTxt = filters.split(",")
        
        
        #--------------------------------------
        # Main reg param loop
        
        for reg in regTxt :
            if reg != "":
                if reg.upper().startswith("B:"):
                    reg = reg[2:]
                    try:
                        parts = reg.split("..")
                        regsType[Format.toNumber(parts[0])] ="b:"
                    except : pass
                elif reg.upper().startswith("H:"):
                    reg = reg[2:]
                    try:
                        parts = reg.split("..")
                        regsType[Format.toNumber(parts[0])] ="h:"
                    except : pass
                elif reg.upper().startswith("D:"):
                    reg = reg[2:]
                    try:
                        parts = reg.split("..")
                        regsType[Format.toNumber(parts[0])] ="d:"
                    except : pass
                else :
                    try:
                        parts = reg.split("..")
                        regsType[Format.toNumber(parts[0])] ="h:"
                    except : pass
                try :
                    if ".." in reg:
                        parts = reg.split("..")
                        n1 = Format.toNumber(parts[0])
                        n2 = Format.toNumber(parts[1])+1
                        for val in range (n1,n2):
                            if val <= (0x1FF):
                                regs.add(val)
                                regsType[val] =regsType[n1]
                                
                    elif "*" in reg :
                        regs.add(reg)
                    else:
                        val = Format.toNumber(reg)
                        if val <= (0x1FF):
                            regs.add(val)
                except  :
                    #print sys.exc_info()[0]
                    pass # something wrong entred ? TODO : message
        regs = list(regs)
        regs.sort()
        wregs = list(self.watchedReg)
        wregs.sort()
        regs += ["-"]+wregs       
        for reg in regs :
            
            if reg == "-":
                self.listWatchRegs.InsertStringItem(index,"-"*10)
                self.listWatchRegs.SetStringItem(index,1, "-"*10)
                self.listWatchRegs.SetStringItem(index,2, "-"*20)
            else:
                
                # multi byte mode
                parts = str(reg).split("*")
                nReg = 0
                if (len(parts)==2) and parts[1] != "":
                    
                    startReg= Format.toNumber(parts[0])
                    nbBytes = int(parts[1])
                    vReg ="b"
                    if nbBytes == 0:
                        nbBytes = 1   
                    for i in range(startReg+nbBytes-1,startReg-1,-1):
                        vReg += Format.bin(self.emu.state.absreg(i))
                    format ="%d"
                    if parts[0].startswith("0x"):
                        format = "0x%X"
                    nReg = Format.toNumber(vReg)
                    vReg = format  % nReg
                    regStr = reg
                else :
                    nReg = self.emu.state.absreg(Format.toNumber(parts[0]))
                    vReg =  format2 % nReg
                    regStr = "%4d 0x%03X" % (Format.toNumber(parts[0]),Format.toNumber(parts[0]))
                
                # if prefix avaiable("b:"), override default display
                
                if (regsType.has_key(reg)):
                    if(regsType[reg]=="d:"):
                        vReg =str(nReg)
                    elif(regsType[reg]=="b:"):
                        vReg =Format.binf(nReg)
                    elif(regsType[reg]=="h:"):
                        vReg = "0x%X"  % nReg    
                    
                #---------------------------
                # display
                
                self.listWatchRegs.InsertStringItem(index,regStr)
                self.listWatchRegs.SetStringItem(index,1, vReg)
                comment =""
                
                if hasattr(self, "langParser") and (self.langParser.adrVarMapping.has_key(reg)):
                    comment =self.langParser.adrVarMapping[reg]
                    comment = comment.replace("v_","")
                tmp = "?"
                try:
                    tmp = regStr.strip().split(" ")[0]
                    nReg = int(tmp)
                    #if (Format.spAdrReg.has_key(nReg)) :
                    #    comment = Format.spAdrReg[nReg]
                    if ( self.emu.state.spAdrReg.has_key(nReg)) :
                        comment = self.emu.state.spAdrReg[nReg]
                except :
                    #print "UIManager.updateWatchRegView : ["+tmp+"]"
                    pass
                self.listWatchRegs.SetStringItem(index,2, comment)
                changed = True
                if self.oldWatchedValues.has_key(str(reg)):
                    if vReg != self.oldWatchedValues[str(reg)]:
                        changed = True
                    else:
                        changed = False
                if changed :
                    self.listWatchRegs.SetItemTextColour(index,"#FF0000")
                else:
                    self.listWatchRegs.SetItemTextColour(index,"#000000")
                self.oldWatchedValues[str(reg)] = vReg
            index += 1

    def OnVarFilterKeyDown(self,event):
        if self.listWatchVars.GetItemCount() > 0:
            self.updateWatchVarView()


    def OnRegFilterKeyDown(self,event):
        if self.listWatchRegs.GetItemCount() > 0:
            self.updateWatchRegView()
        
    def OnEEPromFilterKeyDown(self,event):
        if hasattr(self.emu, "state") :
            self.updateWatchDataEEPromView()
        
        
    # -----------------------------------------------------------------------------
    #
    #
    def updateWatchDataEEPromView(self):
        #format4 ="%4d"
        format2 = "0x%02X"
        #--------------------------------------------
        # display regs to watch
        # reg get added when state.regWrite() by the RegisterUpdater class
        self.listWatchDataEEProm.DeleteAllItems()
        addrs = set()
        filters = self.dataEEPromFilter.GetValue()
        addrTxt = []
        if (filters.strip() != ""):
            addrTxt = filters.split(",")
        else:
            if hasattr( self.emu.pic, "eeprom_size" ):
                addrTxt= ["0..%d" % (self.emu.pic.eeprom_size-1) ]
    
        for addr in addrTxt :
            if addr != "":
                try :
                    if ".." in addr:
                        parts = addr.split("..")
                        n1 = Format.toNumber(parts[0])
                        n2 = Format.toNumber(parts[1])+1
                        for val in range (n1,n2):
                            if val <= (0xFF):
                                addrs.add(val)    
                    else:
                        val = Format.toNumber(addr)
                        if val <= (0xFF):
                            addrs.add(val)
                except : pass # something wrong entred ? TODO : message
        addrs = list(addrs)
        addrs.sort()
        
        try:
            for i,adr in enumerate(addrs) :
                self.listWatchDataEEProm.InsertStringItem(i,str(adr))
                val = format2  % self.emu.state.eeData[adr]
                self.listWatchDataEEProm.SetStringItem(i,1,val)
        except : pass # something wrong entred ? TODO : message
        
    def updateViews(self):
        self.updateWatchRegView()
        self.updateWatchVarView()
        self.updateWatchDataEEPromView()
        
        
    def OnRemoveAllBreakpoints(self,event):
        self.removeAllBreakpoints()
        
    def removeAllBreakpoints(self):
        # clear bp
        #for i in range(0,len( self.breakpoints ) ):
        #    self.breakpoints[i] = False  
        #for i in range(0,len( self.breakpoints ) ):
        self.breakpoints = {}

        # remove marks
        nb = self.listLang.GetItemCount()
        for i in range (0,nb):
            self.listLang.SetStringItem(i,Context.COL_BP,"")
        nb = self.listAsm.GetItemCount()
        for i in range (0,nb):
            self.listAsm.SetStringItem(i,Context.COL_BP,"")
        
        #clear list
        self.listBreakpoint.DeleteAllItems()
    
    
    def OnlistBreakPointSelected(self,event):
        currentItem = event.m_itemIndex
        adr =  self.listBreakpoint.GetItem(currentItem,0).GetText()
        line = None
        if hasattr(self, "langParser") : 
            line = self.langParser.adrToLine[int(adr)]
        self.clearDebugListSelectedLine()
       
        if  line != None :
            self.listLang.Select(line, True)
            self.listLang.EnsureVisible(line)
        else:
            self.listAsm.Select(int(adr), True)
            self.listAsm.EnsureVisible(int(adr))
        
        
    def loadDebugList(self,instructionList,lastAddress,code,wholeCode):
    
        self.listAsm.DeleteAllItems()
        if code != None:
            self.listLang.DeleteAllItems()
        
        # fill asm list
        for i in range(0,lastAddress+1):
            inst = instructionList[i]
            self.listAsm.InsertStringItem(i, "")
            self.listAsm.SetStringItem(i,Context.COL_ADR,  "%06X" % inst.adresse )
            self.listAsm.SetStringItem(i,Context.COL_CODE, Format.formatInstructionWithoutAddress(inst, 0, True).strip())
            #print str(inst.adresse)+" "+Format.formatInstructionWithoutAddress(inst, 0, False).strip()
            
    
        # decorate with jal comment
        for i in range (0,len(wholeCode)):
           if (wholeCode[i] != None):
               if (self.asmParser.lineToAdr[i] != None):
                  
                      text = wholeCode[i].line
                      tmpText =  self.listAsm.GetItem(self.asmParser.lineToAdr[i],Context.COL_COM).GetText()
                      if (tmpText.strip() != ''):
                          try :
                              text = unicode(tmpText+" / "+wholeCode[i].line)
                          except : 
                              print "Warning : Exception occurs in UIManager.loadDebugList on text :"
                              print tmpText,
                              print " / ",
                              print wholeCode[i].line
                      try :        
                          self.listAsm.SetStringItem(self.asmParser.lineToAdr[i],Context.COL_COM,text.replace("\t","    ")) 
                      except :
                          first_error = False
                          # something got wrong...
                          print "======================================================="
                          print "Error in loadDebugList(...)"
                          print i        
                          print text
                          print "Unreachable adress : "+str(self.asmParser.lineToAdr[i])
                          print "======================================================="
                          
        if code != None :      
            # fill lang list

            self.allLineAddresses =  {}

            for i in range (0,len(code)):
               if (code[i] != None):
                  #print "PL : " code[i].line
                  self.listLang.InsertStringItem(i,"") # breakpoint
                  if code[i].address != " ":
                      # print ":" + code[i].address + ":"
                      self.listLang.SetStringItem(i,Context.COL_ADR, "%06X" % code[i].address)
                  else:
                      self.listLang.SetStringItem(i,Context.COL_ADR, "")
                      
                  self.listLang.SetStringItem(i,Context.COL_CODE, code[i].line.replace("\t","    "))
                  
                  if code[i].address != " ":
                      self.allLineAddresses[code[i].address] = True
                     
                  curLine = self.listLang.GetItem(i,Context.COL_CODE).GetText()
                  upCurLine = curLine.upper()
                  if (curLine.startswith('--')):
                      self.listLang.SetItemTextColour(i,'#55CC55')
                  elif ('PROCEDURE' in upCurLine)  or ('FUNCTION' in upCurLine) or ('LOOP' in upCurLine) or ('IF ' in upCurLine) or ('ELSE' in upCurLine) or ('END ' in upCurLine):
                      font = self.listLang.GetItemFont(i)
                      font.SetWeight(wx.BOLD)
                      font.SetPointSize(8)
                      self.listLang.SetItemFont(i,font)
                      # set asm list boldness
                      try :
                          self.listAsm.SetItemFont(self.langParser.lineToAdr[i],font)
                      except : pass

    #----------------------------------------------------------------
    # Lists (ASM AND LANG)
    #
    def updateDebugListPosition(self,adr):
        self.clearDebugListSelectedLine()
        self.listAsm.Select(adr, True)
        self.listAsm.EnsureVisible(long(adr))

        if ( self.emu != None ) :        
        	newCycles = self.emu.state.GetCycles()
        	self.uiManager.SetStatusText("Cycles %d" % newCycles + ", delta cycles %d" % ( newCycles - self.curCycles ) )  
        
        if hasattr(self, "langParser"):
            langLine = self.langParser.adrToLine[adr]
            
            if (langLine != None):
                self.listLang.Select(langLine, True)
                nbLines = self.listLang.GetItemCount() 
                for i in range(langLine,nbLines):
                    nextadr =  self.listLang.GetItem(i,Context.COL_ADR).GetText()
                    try :
                        nextadr = int(nextadr,16)
                        if adr == nextadr:
                            self.listLang.Select(i, True)
                        else:
                            break
                    except :
                        break
                self.listLang.EnsureVisible(long(langLine))
        
    def buildEmu(self,hexFileName,wholeCode=None):
        adrDelay = None
        if wholeCode != None :
            jalCode = [""]*1024*128
            adrDelay = {}
            # build an array with address as index and code as content
            for i in range (0, len (wholeCode)) :
                adr = str(wholeCode[i].address).strip()
                if adr != "" :
                    if jalCode[int(adr)] != "":
                        jalCode[int(adr)] += str("-"+wholeCode[i].line)
                    else :
                        jalCode[int(adr)] = str(wholeCode[i].line)
            
            for i in range (0, len (jalCode)) :
                line = jalCode[i].replace("--",";")
                line = line.split(";")[0]
                line = line.upper().strip()
                if "DELAY_" in line and "PROCEDURE" not in line.upper():
                    line = line[line.index("DELAY_"):]
                    # print line
                    factor =1
                    if "MS" in line :
                        factor = 0.001
                    elif "US" in line :
                        factor = 0.000001
                    
                    time=0
                    nbr = 1
                    partNbr = line.split("(")
                    if len(partNbr) > 1:
                        nbr = partNbr[1]
                        try :
                            nbr = int(nbr.replace(")","").strip())
                        except : nbr = 1
                    time = line[6:]
                    time = re.split("[MSU]+",time)[0]
                    delay = int(time) * nbr * factor
                    adrDelay[i]= delay        
                    # print " adrDelay[i] %d " % i + " = %d " % delay
        
        self.emu = PicEngine.newInstance( self.picName , hexFileName, self.programMemCallBack, adrDelay)
        
        mon = RegisterUpdater(self.watchedReg)
        devTarget =  DeviceTargetStateMonitor(self) # use to update device state from emu.state (ie led.. lcd...)
        devSource =  DeviceSourceStateMonitor(self) # used to update emu.state from device state (ie buttons)
        
        #profiler = ProfilerPulgin(self)
        #self.plugins = [profiler]     
        #self.emu.monitors = [profiler]     
        
        self.emu.state.globalWriteMonitors = [mon,devTarget]  
        self.emu.state.globalReadMonitors = [devSource] 
        
        
    def toggleBreakPointAtAdr(self,adr):
        if adr != None:
            # self.breakpoints[adr] = not self.breakpoints[adr]
            if self.breakpoints.has_key( adr ):
               del self.breakpoints[adr]
            else:
               self.breakpoints[adr] = True
               
            #if (self.breakpoints[adr]):
            if (self.breakpoints.has_key( adr )):
                mark ="X"
                self.listBreakpoint.InsertStringItem(0,str(adr))
            else:
                mark =""
                # TODO : remove breakpoint from list
                self._removeBreakPointFromList(str(adr))
                
            self.listAsm.SetStringItem(adr,Context.COL_BP,mark)
            if  hasattr(self, "langParser") and self.langParser.adrToLine[adr] != None :
                self.listLang.SetStringItem(self.langParser.adrToLine[adr],Context.COL_BP,mark)
                
                #if (self.breakpoints[adr]):
                if (self.breakpoints.has_key(adr)):
                    tmpText =  self.listLang.GetItem(self.langParser.adrToLine[adr],Context.COL_CODE).GetText()
                    self.listBreakpoint.SetStringItem(0,1,tmpText)
                
            if (self.threadEngine != None):
               self.threadEngine.runTillAddress = self.breakpoints  
               self.clearDebugListSelectedLine()  
        
    def _removeBreakPointFromList(self,adr):
        lineToRemove = []
        cpt = self.listBreakpoint.GetItemCount()
        for i in range (0,cpt):
            curAdr =  self.listBreakpoint.GetItem(i,0).GetText()
            if curAdr == adr :
                lineToRemove.append(i)
        for i in lineToRemove:
            self.listBreakpoint.DeleteItem(i)
            
    def OnBreakPointAsm(self,event):
        adr = self.listAsm.GetFirstSelected()
        self.toggleBreakPointAtAdr(adr)
        
    def OnBreakPointLang(self,event):
        adr = self.langParser.lineToAdr[self.listLang.GetFirstSelected()]
        self.toggleBreakPointAtAdr(adr)
        
        
    def run(self):
         if (not self.running) and self.listAsm.GetItemCount()>0:
            self._runTo(self.breakpoints)
        
    def restart(self):
    	self.SetupDebugSession(self.sessionHexFileName , self.sessionJalSrcCode, self.sessionVirtualDelay )
        self.run()
        
    def reset(self):
        if self.running:
            self.stop() # reset will be call at the and of callback
            self.running = False
            self._reset()
        else:
            self._reset()
        
        
    #-------------------------------------------------------------------------------
    # Next action
    # 
    def nextAsm(self):
        self.uiManager.SetCursor(HOURGLASS_CURSOR)
        self.curCycles = self.emu.state.GetCycles()

        if (not self.running) and self.listAsm.GetItemCount()>0:
           if (self.threadEngine != None):
                self.threadEngine.stop()

           adr = self.emu.runNext()
           inst = self.emu.getCurInst() 
           self.explainAsmText.SetLabel("")
           self.explainAsmText.AppendText( AsmDocHelp.getAsmDescriptionHelp(inst, self.emu.state))
           self.explainAsmText.AppendText( AsmDocHelp.getAsmBeforeExecutionHelp(inst, self.emu.state))
           self.callback(adr)
           self.explainAsmText.AppendText( AsmDocHelp.getAsmAfterExecutionHelp(inst, self.emu.state))
        self.uiManager.SetCursor(STANDARD_CURSOR)
        newCycles = self.emu.state.GetCycles()
        self.uiManager.SetStatusText("Cycles %d" % newCycles + ", delta cycles %d" % ( newCycles - self.curCycles ) )  
    
    def nextLang(self):
        self.uiManager.SetCursor(HOURGLASS_CURSOR)
        self.curCycles = self.emu.state.GetCycles()
        if (not self.running) and self.listAsm.GetItemCount()>0:

           if hasattr(self, "allLineAddresses"): # inactif si import hex

               addresses = dict( self.allLineAddresses )

               # include asm breakpoint(s)
               for bp in self.breakpoints:
                  addresses[bp] = True 
               #print "ADDRESSES incl BP"
               #print addresses
               self._runTo(addresses ,self.unitTestCallBack)
        self.uiManager.SetCursor(STANDARD_CURSOR)
        newCycles = self.emu.state.GetCycles()
        self.uiManager.SetStatusText("Cycles %d" % newCycles + ", delta cycles %d" % ( newCycles - self.curCycles ) )  
        
    # not fully woking for now...    
    def nextStepOverLang(self):
        text =  self.listAsm.GetItem(self.emu.state.pc,Context.COL_COM).GetText()
        print text,
        if not JalV2Parser.mustStepOver(text):
            self.nextLang()
            return    
        
        self.uiManager.SetCursor(HOURGLASS_CURSOR)
        if (not self.running) and self.listAsm.GetItemCount()>0:
            addresses =  [0]*1024*128
            for i in range (0,len( addresses )):
                addresses[i] = False
           
            for a in self.langParser.lineToAdr :
                if (a != None) and (int(a) > self.emu.state.pc) :
                    addresses[a] = True
                    break
            
            # include breakpoint
            for adr,hasBreakpoint in enumerate(self.breakpoints):
                if hasBreakpoint :
                      addresses[adr] = True 
            self._runTo(addresses,self.unitTestCallBack)
        self.uiManager.SetCursor(STANDARD_CURSOR)
           
    def stop(self):
       if (self.threadEngine != None):
          self.threadEngine.stop()
          
          #while self.threadEngine.stopped == False : pass
       if ( self.emu != None ):   
       	self.uiManager.SetStatusText("Stopped, cycles: %d" % self.emu.state.GetCycles())  
       else:	
       	self.uiManager.SetStatusText("Stopped")  
 

    #-------------------------------------------------------------------------------
    # Callback function, called by thread engine when thread engine has finished
    # 
    def callback(self,adr):
    	self.running = False    	
    	if self.Quit == False:
        	wx.CallAfter( self.updateDebugListPosition, adr )
        	wx.CallAfter( self.updateViews)    	
        	wx.CallAfter( self.uiManager.enableActionWidget)


    def _runTo(self,to,unitTestCallBack=None):

       if self.emu != None :
           self.curCycles = self.emu.state.GetCycles()
       
           self.stop()
           self.running = True
           self.uiManager.disableActionWidget()
           self.clearDebugListSelectedLine()
           self.threadEngine = PicThreadEngine(self.emu,unitTestCallBack) 
           self.threadEngine.callback = self.callback
           self.threadEngine.runTillAddress = to
           self.threadEngine.start() 
           self.uiManager.SetStatusText("Running")  
    
    def updateBreakPoints(self):
        self.listBreakpoint.DeleteAllItems()
        for adr in range(0,self.listAsm.GetItemCount()) :
            #if (self.breakpoints[adr]):
            if (self.breakpoints.has_key(adr)):
                mark ="X"
                self.listBreakpoint.InsertStringItem(0,str(adr))
            else:
                mark =""
                # TODO : remove breakpoint from list
                self._removeBreakPointFromList(str(adr))
                
            self.listAsm.SetStringItem(adr,Context.COL_BP,mark)
            if  hasattr(self, "langParser") and self.langParser.adrToLine[adr] != None :
                self.listLang.SetStringItem(self.langParser.adrToLine[adr],Context.COL_BP,mark)
                
                #if (self.breakpoints[adr]):
                if (self.breakpoints.has_key(adr)):
                    tmpText =  self.listLang.GetItem(self.langParser.adrToLine[adr],Context.COL_CODE).GetText()
                    self.listBreakpoint.SetStringItem(0,1,tmpText)
        
    def _reset(self):
        self.uiManager.SetCursor(HOURGLASS_CURSOR)
        
        #
        # Realy dirty need to be cleaned !
        #
        self.clearDebugListSelectedLine()
        self.buildDevices(self.devices)
        self.Clear()
        
        self.curCycles = 0
        
        for plugin in self.plugins:
            plugin.reset()        
            
        uartProvider = None
        uartReceiver = None
        # get a thread engine
        #if self.emu != None:
        if False:
            if hasattr(self.emu.state, "uartProvider"):
                uartProvider = self.emu.state.uartProvider
            if hasattr(self.emu.state, "uartReceiver"):
                uartReceiver = self.emu.state.uartReceiver
            
            if hasattr(self.emu.state, "monitors"):
                monitors = self.emu.state.monitors
                for mon in monitors:
                    mon.reset()
                    
            
            hexFileName = self.emu.hexfilename

            parseRes = AnnotationParser.parse(self.mainEditor.GetText())
            self.buildEmu(hexFileName)

            self.emu.state.monitors = monitors
            
            if uartProvider != None :
                self.emu.state.uartProvider = uartProvider
            if uartReceiver != None :
                self.emu.state.uartReceiver = uartReceiver
            
            # Update asm list as it may have been update by program flash change
            self.asmParser = JalV2AsmParser()
            asmFileName = self.mainEditor.filename.replace(".jal",".asm")
            parse_an = parseRes["options"]
            
            if "virtual_delay" in parse_an :
                asmFileName = self.buildVirtualFileName(asmFileName)
           
            if os.path.exists(asmFileName):
                wholeCode = self.asmParser.parseAsmFile(asmFileName, [])
                self.loadDebugList(self.emu.instructionList, self.emu.lastAddress, None, wholeCode)
                
            
            noDebugList = parseRes["noDebug"] 
            debugList =parseRes["debug"]  
           
            if parseRes["regfilter"] != "":
               self.regFilter.SetLabel(parseRes["regfilter"])
            if parseRes["varfilter"] != "":
               self.varFilter.SetLabel(parseRes["varfilter"])
               
            self.hexFileName = self.mainEditor.filename.replace(".jal",".hex")
            virtualHexFileName = self.buildVirtualFileName(self.hexFileName)
            self.asmParser = JalV2AsmParser()
            wholeCode = self.asmParser.parseAsmFile(asmFileName, [])
            if "virtual_delay" in parse_an :
                self.buildEmu(virtualHexFileName,wholeCode)
            else :
                self.buildEmu(hexFileName)
           
            self.langParser = JalV2AsmParser()
            
            # set langParser to debugView
            self.langParser = self.langParser
            
            code = self.langParser.parseAsmFile(asmFileName, noDebugList,debugList)
            self.loadDebugList(self.emu.instructionList,self.emu.lastAddress,code,wholeCode)
            self.varTypeDict = JalV2AsmParser.buildVarTypeDict(wholeCode)
           
            wx.Yield()
            self.buildInOut(parseRes["inputs"],parseRes["outputs"])
            
            #build in / out
            
            self.devices = parseRes["devices"]
          
            self.buildDevices(self.devices)
            self.uiManager.top.toolbar.EnableTool(Context.TOOL_RUN,True)
            self.uiManager.top.GetMenuBar().Enable(124,True)
            self.uiManager.top.toolbar.EnableTool(Context.TOOL_RUN_UNIT_TEST,True)
        
            self.updateBreakPoints()
        
            self.uiManager.SetStatusText("Reseted")
            
        self.uiManager.SetCursor(STANDARD_CURSOR)        
        
        
    def buildInOut(self,inputs,outputs):

        self.inOutPanel.DestroyChildren()
        li = len(inputs)
        lo = len(outputs)
        max = li
        if lo>li :
            max = lo
        for i in range(0,max):
            if i< li:
                input = inputs[i]
                    
                if hasattr(input, "callbackRead"):
                    input.callbackRead = self.callbackRead
                if hasattr(input, "callbackWrite"):
                    input.callbackWrite = self.callbackWrite
                if hasattr(input, "callbackWriteAdc"):
                    input.callbackWriteAdc = self.callbackWriteAdc
                 
                but = input.CreateUI(self.inOutPanel,self.inOutSizer )

                # af need to find a cleaner way of doing this
                if hasattr(input, "hasData"):
                     self.emu.state.uartProvider = input
                
            else:
                self.inOutSizer.Add(wx.StaticText(self.inOutPanel,-1,""))
            if i< lo:
                output = outputs[i]
                comp = None
                                        
                varAdrMapping = None
                address = None
                						  
                if hasattr(self, "langParser"):
                        varAdrMapping = self.langParser.varAdrMapping
                        if hasattr(output, "address"):
                            output.address = Format.toNumber(str(output.address),varAdrMapping)

                output.CreateUI(self.inOutPanel, self.inOutSizer )
                comp = output
                    
                if (output.type=="uartReceiver"):
                    self.emu.state.uartReceiver = output
                
                if comp != None and hasattr(comp, "address"):                           
                     self.emu.state.appendMonitor( comp )
            else:
                self.inOutSizer.Add(wx.StaticText(self.inOutPanel,-1,""))
        
        #hack due to redraw problems on windows   
        self.bottomSplitter.SetSashPosition(self.bottomSplitter.GetSashPosition()+1,True) 
        self.bottomSplitter.SetSashPosition(self.bottomSplitter.GetSashPosition()-1,True) 
        
    def clearDebugListSelectedLine(self):
       if self.listLang != None : 
           item = self.listLang.GetFirstSelected()
           if item != -1:     
               self.listLang.Select(item,False)  
           while item != -1:
                item = self.listLang.GetNextSelected(item)
                self.listLang.Select(item,False)
           
       item = self.listAsm.GetFirstSelected()
       if item != -1:         
           self.listAsm.Select(item,False)
        
    def OnListLangSelected(self,event):
        currentItemDebug = event.m_itemIndex 
        # sync list asm
        item = self.listLang.GetItem(currentItemDebug,Context.COL_ADR)
        adr =  item.GetText().strip()
        if (adr != ""):
            self.listAsm.Select(int(adr,16), True)
            self.listAsm.EnsureVisible(int(adr,16))
        
    def gotoTopDebugList(self):
       if hasattr(self, "listLang") :
           self.listLang.Select(0,True)
           self.listLang.EnsureVisible(0)
      
       self.listAsm.Select(0,True)
       self.listAsm.EnsureVisible(0)
       
    def programMemCallBack(self,data,adr,lastAddress,instructionList):
        # any nedd to update asm debug list ?
        if adr<= lastAddress:
           self.asmParser = JalV2AsmParser()
           asmFileName = self.uiManager.mainEditor.filename.replace(".jal",".asm")
           wholeCode = self.asmParser.parseAsmFile(asmFileName, [])
           self.loadDebugList(instructionList,lastAddress,None,wholeCode)            
        
    def buildDevices(self,devices):
        if devices != None :
            nodeCounter = 0
            dc =wx.ClientDC ( self.drawWindow )
            self.drawWindow.diagram.Clear(dc)
            self.drawWindow.diagram.RemoveAllShapes()
           
            for i in range(0,1024*128):
                self.nodesForAddress[i] = None
                self.devicesForAddressRead[i] = None
                self.devicesForAddressWrite[i] = None
                
            for device in devices :
                parts = device.split(" ")
                deviceFullName = parts[1]
                deviceModule = deviceFullName.split(".")[0]
                deviceClass = deviceFullName.split(".")[1]
                deviceArgs = parts[2:]
                print sys.path
                exec("from %s import %s" % (deviceModule,deviceClass))
                
                deviceInstance = eval("%s()" % deviceClass)
                deviceInstance.NodeNr = [0] * (len(deviceArgs)+1)
                
                cptDeviceInstanceNodes = 1 # JALsPy defined that pin start at 1
                for arg in deviceArgs:
                    # transfer arg to device instance
                   
                    if "=" in arg :
                        parts = arg.split("=")
                        cmd = "deviceInstance.%s = %s" % (parts[0],parts[1])
                        exec(cmd)
                        
                    elif arg.startswith("pin_") :
                        pin = arg.upper()
                        #convert pin_a0 -> 5 bit 1
                        port = ord(pin[4])-60 
                        bit = pow(2,(ord(pin[5])-48))
                        
                        # some JALsPy needs...
                        # JALsPy_globals.V_Node.append(1)
                        # JALsPy_globals.G_Node.append(1)
                        # JALsPy_globals.C_Node.append(1)
                        # JALsPy_globals.T_Node.append(1)
                        deviceInstance.NodeNr[cptDeviceInstanceNodes] = nodeCounter
                        
                        # build a static map of (node - address_bit) for an address
                        # useful to update the NodeList (JALsPy_globals.V_Node) on which the device relies
                        # to know their states
                        nodesAndBits = self.nodesForAddress[port]
                        if (nodesAndBits == None) :
                            nodesAndBits = []
                        nodesAndBits.append((nodeCounter,bit)) # (6,128) -> node 0 is on portb bit 7 
                        self.nodesForAddress[port] = nodesAndBits   # [addr] = [(nodex,addr_bit),(nodey,addr_bit),...]
                        
                        # build a static map to retrieves all devices for an address
                        # useful to know wich devices need to be updated when a register changes
                        # comp needs update only if pic_pin  is output
                        #if self.emu.state.isOutput(port,bit): 
                        devicesForAddr = self.devicesForAddressWrite[port]
                        if (devicesForAddr == None) :
                            devicesForAddr = set()
                        devicesForAddr.add(deviceInstance)
                        self.devicesForAddressWrite[port] = devicesForAddr
                        print "device "+str(deviceInstance.__class__)+" binded to "+arg+" as target, node="+str(nodeCounter)
                        
                        #else :
                            #inputs
                        devicesForAddr = self.devicesForAddressRead[port]
                        if (devicesForAddr == None) :
                            devicesForAddr = set()
                        devicesForAddr.add(deviceInstance)
                        self.devicesForAddressRead[port] = devicesForAddr
                        print "device "+str(deviceInstance.__class__)+" binded to "+arg+" as source, node="+str(nodeCounter)
                        #end
                        
                        
                        cptDeviceInstanceNodes+=1
                        nodeCounter += 1
                        
                    elif arg.upper() == "LOW" or arg.upper() == "OFF" or arg.upper() == "FALSE":
                         print "device "+str(deviceInstance.__class__)+" connected to low, node="+str(nodeCounter)

                         deviceInstance.NodeNr[cptDeviceInstanceNodes] = nodeCounter
                         # JALsPy_globals.V_Node.append(1)
                         # JALsPy_globals.G_Node.append(1)
                         # JALsPy_globals.C_Node.append(1)
                         # JALsPy_globals.T_Node.append(1)
                         
                         # JALsPy_globals.V_Node[nodeCounter] = 0 # 0 Volt
                         cptDeviceInstanceNodes+=1
                         nodeCounter += 1
                        
                        
                    elif arg.upper() == "HIGH" or arg.upper() == "ON" or arg.upper() == "TRUE":
                         print "device "+str(deviceInstance.__class__)+" connected to high, node="+str(nodeCounter)

                         deviceInstance.NodeNr[cptDeviceInstanceNodes] = nodeCounter
                         # JALsPy_globals.V_Node.append(1)
                         # JALsPy_globals.G_Node.append(1)
                         # JALsPy_globals.C_Node.append(1)
                         # JALsPy_globals.T_Node.append(1)
                         
                         # JALsPy_globals.V_Node[nodeCounter] = 5 # 5 Volt
                         cptDeviceInstanceNodes+=1
                         nodeCounter += 1
                    
                deviceInstance.init()
                shape = deviceInstance.shape
                shape.SetX(deviceInstance.x)
                shape.SetY(deviceInstance.y)
                self.drawWindow.diagram.AddShape(shape)
                shape.Show(True)
                self.drawWindow.diagram.Redraw(dc)

    #
    # Used by debug components to read a register
    #
    def callbackRead(self,port):
        return self.emu.state.absreg(port)
    #
    # Used by debug components to write a register
    #
    def callbackWrite(self,port,value):
        self.emu.state.abswrite(port,value)
        

    #
    # Used by debug components to write the ADC register for the specified analog channel
    #
    def callbackWriteAdc(self,pinNumber,value):
        # print "UPDATE ADC FROM UI channel: %d" % int( pinNumber ) + " to value %d" % value        
        self.emu.state.adc[int(pinNumber)] = value
    
                
    def unitTestCallBack(self,address):
        #print "callback for address : "+str(address) 
        label =""
        res= ""
        status = "ERROR"
        item = 0 # insert error on top
        color = "red"
        if address >= len(self.langParser.adrToLine):
            res =  "Address is out of bound [0..8191] : "+str(address)
            status = "ERROR"
            self.listUnitTest.InsertStringItem(item,label)
            self.listUnitTest.SetStringItem(item,1,status)
            self.listUnitTest.SetStringItem(item,2,res)
            self.listUnitTest.SetItemTextColour(item,color)
        else :    
            line = self.langParser.adrToLine[address]
            if line != None:
                code =  self.listLang.GetItem(line,Context.COL_CODE).GetText()
                assertTag = AssertUtil.GetAssertTag( code )                

                if assertTag != None:                	 
                    res = AssertUtil.parse(code,assertTag)
                    var = res["var"].lower()
                    label = res["label"]
                    ref = res["ref"]
                    if (self.langParser.varAdrMapping.has_key("v_"+var)):
                        varAddr = self.langParser.varAdrMapping["v_"+var]
                        # print self.varTypeDict
                        
                        if self.varTypeDict.has_key( var ):
                            varType = type = self.self.varTypeDict[var]
                        else:
                            varType = "Unknown type: "
                        
                        val = self.emu.varValue(varAddr,varType)  
                        
                        [assertRes, cmpStr ] = AssertUtil.Assert( assertTag, val, ref )
                        
                        res= varType+ " " + var + " (@"+str(varAddr)+") = 0x%X " % val + cmpStr + " expected : 0x%X" % ref
                        
                        if ( assertRes ) :
                            status = "PASS"
                            color ="#008000"
                            item = self.listUnitTest.GetItemCount()
                        else :
                            status = "FAIL"
                            
                    else :
                        status = "ERROR"
                        res = "Test can't be run, var "+var+" can't be identified (address not found in asm file)"

                    self.listUnitTest.InsertStringItem(item,label)
                    self.listUnitTest.SetStringItem(item,1,status)
                    self.listUnitTest.SetStringItem(item,2,res)
                    self.listUnitTest.SetItemTextColour(item,color)
        
        
    def SetupDebugSession(self,hexFileName, jalSrcCode, virtualDelay ):
    
		self.sessionHexFileName = hexFileName
		self.sessionJalSrcCode = jalSrcCode
		self.sessionVirtualDelay = virtualDelay
		    
		if self.running:
			self.stop() # reset will be call at the and of callback
			self.running = False

		self.Clear()

    
		parseRes = AnnotationParser.parse( jalSrcCode )    
		
		noDebugList = parseRes["noDebug"] 
		debugList =parseRes["debug"]  
		
		if parseRes["regfilter"] != "":
		   self.regFilter.SetLabel(parseRes["regfilter"])
		if parseRes["varfilter"] != "":
		   self.varFilter.SetLabel(parseRes["varfilter"])
		
		asmFileName = hexFileName.replace(".hex",".asm")
		
		wholeCode = self.asmParser.parseAsmFile(asmFileName, [])
		self.picName = self.asmParser.picName
		self.langParser = JalV2AsmParser()			
		code = self.langParser.parseAsmFile(asmFileName, noDebugList, debugList )

		
		if virtualDelay :
			self.buildEmu( hexFileName )
		else:
			self.buildEmu( hexFileName, wholeCode )
								
		self.loadDebugList(self.emu.instructionList,self.emu.lastAddress,code,wholeCode)
		
		self.varTypeDict = JalV2AsmParser.buildVarTypeDict(wholeCode)
		
		#build in / out
		self.buildInOut(parseRes["inputs"],parseRes["outputs"])
		self.devices = parseRes["devices"]
		
		self.buildDevices(self.devices)
		
		self.listUnitTest.DeleteAllItems()
		
		self.pic = PicFactory( "pic_" + self.picName )           
		Format.spReg = self.pic.fsr_regs
		
    def Close( self ):
		self.Quit = True
		self.reset()
		self.listAsm.Unbind(wx.EVT_LEFT_DCLICK)
		self.listAsm.Unbind(wx.EVT_LEFT_DCLICK)
		self.listLang.Unbind(wx.EVT_LEFT_DCLICK)
		self.listLang.Unbind(wx.EVT_LIST_ITEM_SELECTED)
		self.mainSplitter.Unbind(wx.EVT_BUTTON)
		self.mainSplitter.Unbind(wx.EVT_BUTTON)
		self.regFilter.Unbind(wx.EVT_TEXT)
		self.varFilter.Unbind(wx.EVT_TEXT)
		self.dataEEPromFilter.Unbind(wx.EVT_TEXT)
		self.listBreakpoint.Unbind(wx.EVT_LIST_ITEM_SELECTED)
		self.bpRemoveAll.Unbind(wx.EVT_BUTTON)
		