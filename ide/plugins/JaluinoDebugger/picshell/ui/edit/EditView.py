from picshell.ui.edit.JalEditor import JalEditor
from picshell.ui.edit.DrawWindow import MarkWindow
from wx.lib.splitter import MultiSplitterWindow
import wx
class EditView:
    def __init__(self,parent,uiManager):

        # -------------------------------------------------------
        # editor view
      
        self.mainSplitter = MultiSplitterWindow(parent, style=wx.SP_LIVE_UPDATE)
        # -------------------------------------------------------
        # Compile   panel
        #
        compileTab = wx.Notebook(self.mainSplitter,-1) 
        compilePanel = wx.Panel(compileTab, -1)
        logPanel = wx.Panel(compileTab, -1)
        helpPanel = wx.Panel(compileTab, -1)
       
        compileTab.AddPage(compilePanel,"Errors/Warnings list");
        compileTab.AddPage(logPanel,"Output");
        compileTab.AddPage(helpPanel,"Quick help");
        # AF LATER compileTab.AddPage(compilePanel,"Programmer's output");
        
        
        compileTab.SetSelection(2)
        
        # Help panel
        self.helpText = JalEditor(helpPanel,-1)#wx.TextCtrl(helpPanel,style=wx.TE_MULTILINE);
        
        self.helpText.SetText("-- Double click on a procedure name (or function or annotation...) to get a short description")
        
        helpSizer = wx.BoxSizer(wx.VERTICAL);
        helpPanel.SetSizer(helpSizer);
        helpSizer.Add(self.helpText,-1,wx.EXPAND)
        self.helpText.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))
        
        # Compiler's text result 
        self.log = wx.TextCtrl(logPanel,style=wx.TE_MULTILINE);
        self.log.SetBackgroundColour("#ffffe1")
        logSizer = wx.BoxSizer(wx.VERTICAL);
        logPanel.SetSizer(logSizer);
        logSizer.Add(self.log,-1,wx.EXPAND)
        self.log.SetFont(wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL))
        
        # Compilers's parsed result
        self.listResult =  wx.ListCtrl(compilePanel, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        self.listResult.InsertColumn(0, 'Lines')
        self.listResult.InsertColumn(1, 'Files')
        self.listResult.InsertColumn(2, 'Errors/Warnings')
        self.listResult.SetColumnWidth(0, 50)
        self.listResult.SetColumnWidth(1, 200)
        self.listResult.SetColumnWidth(2, 600)
        self.listResult.Bind(wx.EVT_LIST_ITEM_SELECTED, uiManager.OnErrorList)
        self.listResult.Bind(wx.EVT_LEFT_DCLICK, uiManager.OnErrorListDCLICK)
        
        vboxCompile = wx.BoxSizer(wx.VERTICAL);
        vboxCompile.Add(self.listResult, -1,wx.EXPAND, 1 )
        compilePanel.SetSizer(vboxCompile)
        
        
        
        # -------------------------------------------------------
        # Editor  panel
        #
        
        self.editorTopSplitter = MultiSplitterWindow(self.mainSplitter, style=wx.SP_LIVE_UPDATE)
        editorPanel = wx.Panel(self.editorTopSplitter, -1) 
        outlinePanel = wx.Panel(self.editorTopSplitter, -1) 
        editorSizer = wx.BoxSizer(wx.HORIZONTAL);
        outlineSizer = wx.BoxSizer(wx.VERTICAL);
        editorPanel.SetSizer(editorSizer)
        outlinePanel.SetSizer(outlineSizer)
        outlineTree = wx.TreeCtrl(outlinePanel, 1, wx.DefaultPosition, (-1,-1), wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        #outlineTree.SetBackgroundColour("#ffffe1")
        outlineSearch = wx.TextCtrl(outlinePanel,-1)
        outlineSizer.Add(outlineSearch,0,wx.wx.EXPAND)
        outlineSearch.Bind(wx.EVT_KEY_UP, uiManager.OnOutlineSearch)
        outlineSizer.Add(outlineTree,-1,wx.EXPAND)
        
        editor = JalEditor(editorPanel,-1)
        fixedMark = MarkWindow(editorPanel)
        
        
        editor.parentTab = parent
        editor.uiManager = uiManager
       
        #self.editor.setLibPath(self.libpath) 
        
        editorSizer.Add(editor,-1,wx.EXPAND)
        editorSizer.Add(fixedMark,0,wx.EXPAND)
        #self.editorTopSplitter.SplitVertically(outlinePanel,editorPanel)
        
        self.editorTopSplitter.AppendWindow(outlinePanel)
        self.editorTopSplitter.AppendWindow(editorPanel)
        self.editorTopSplitter.SetOrientation(wx.HORIZONTAL)
        
        self.mainSplitter.AppendWindow(self.editorTopSplitter)
        self.mainSplitter.AppendWindow(compileTab)
        self.mainSplitter.SetOrientation(wx.VERTICAL)
        
        self.editorTopSplitter.SetWindowStyle(wx.SP_NOBORDER)
        
        uiManager.outLineTree=outlineTree
        uiManager.outLineSearch=outlineSearch
        uiManager.mainEditor=editor
        uiManager.listResult = self.listResult
        uiManager.compileLog = self.log
        uiManager.helpText = self.helpText
        uiManager.fixedMark = fixedMark
        uiManager.compileTab = compileTab
        uiManager.outlinePanel = outlinePanel
        uiManager.editorPanel = editorPanel
        uiManager.mainSplitter = self.mainSplitter
        uiManager.editorTopSplitter = self.editorTopSplitter
        self.mainSplitter.SetMinimumPaneSize(100)
        #self.mainSplitter.SetSetSashGravity(1.0)
        self.editorTopSplitter.SetMinimumPaneSize(100)
       
        
    def getView(self):
        return self.mainSplitter
    
    
        
    
        
