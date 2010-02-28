from picshell.ui.edit.JalEditor import JalEditor
from picshell.ui.Context import Context
from picshell.util.FileUtil import FileUtil
from picshell.ui.edit.EditorUtil import EditorUtil
from wx.lib.splitter import MultiSplitterWindow
from wx.stc import STC_EOL_CRLF
import wx
import os

class BrowserView:
    def __init__(self,parent,uiManager):
        # -------------------------------------------------------
        # lib Editor
        #
        self.mainSplitter = MultiSplitterWindow(parent, style=wx.SP_LIVE_UPDATE)
        
        
        browserTreePanel = wx.Panel(self.mainSplitter, -1) 
        
        browserTreeSizer = wx.BoxSizer(wx.VERTICAL);
        browserTreePanel.SetSizer(browserTreeSizer)
        self.browserTree = wx.TreeCtrl(browserTreePanel, 1, wx.DefaultPosition, (-1,-1), wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        self.browserTree.SetBackgroundColour("#ffffe1")
        self.browserTree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnBrowserTreeSelChanged)
        browserTreeSizer.Add(self.browserTree,-1,wx.EXPAND)
        
        libPanel = wx.Panel(self.mainSplitter, -1)
        libSizer = wx.BoxSizer(wx.VERTICAL);
        libPanel.SetSizer(libSizer)
        self.browserEditor = JalEditor(libPanel,-1)
        self.browserEditor.uiManager = uiManager
        self.browserEditor.parentTab = parent
        libSizer.Add(self.browserEditor,-1,wx.EXPAND)
        
        self.mainSplitter.AppendWindow(libPanel)
        self.mainSplitter.AppendWindow(browserTreePanel)
        self.mainSplitter.SetOrientation(wx.HORIZONTAL)
        
        self.browserSplitter = self.mainSplitter
        
        #self.mainSplitter.SetSashGravity(1)
        uiManager.browserEditor = self.browserEditor
        
        uiManager.browserSplitter = self.mainSplitter
        
        self.uiManager = uiManager
        
        
    def getView(self):
        return  self.mainSplitter
        
    def clearBrowerTree(self):
        self.browserTree.DeleteAllItems()

    def updateTree(self, jalFileName, jalFileContent ):
        self.browserTree.DeleteAllItems()
        root = self.browserTree.AddRoot('Root')
        includes = self.browserTree.AppendItem(root, 'includes')
        self.browserTree.SetItemBold(includes,True)
        pathes = FileUtil.expand_paths( Context.libpath+";"+os.path.dirname(jalFileName) )
        allincludes = EditorUtil.findAllIncludedFiles(jalFileContent,pathes)
        self.methodsMapping = {}
        for inc in allincludes:
            item = self.browserTree.AppendItem(includes, inc)
            self.browserTree.SetItemBold(item,True)
            funcRes = EditorUtil.findInFileStartswithNoPath(inc,"function",1)
            libFunc = funcRes[0]
            libFuncMapping = funcRes[1]

            procRes = EditorUtil.findInFileStartswithNoPath(inc,"procedure",1)
            libProc = procRes[0]
            libProcMapping = procRes[1]
            
            methodes = set(libFunc+libProc)
            self.methodsMapping.update(libFuncMapping)
            self.methodsMapping.update(libProcMapping)

            for func in methodes:
                self.browserTree.AppendItem(item,func)
        self.browserTree.Expand(includes)    
       
    def CheckBrowserModified( self,parentItem ):
        openFile = False
    
        # AF Check if there are any modified files, if so, show dialog box   
        if ( self.browserEditor.parentTab.GetPageText(Context.TAB_BROWSER).endswith("*") ):

	        dlg = wx.MessageDialog(None, 'Modified file, do you really want to open another file...\n'+
	        'Select cancel to abort exit,\n' +
	        'yes to save the files,\n' +
	        'no to open a new file without saving the modified files',
	          'Open new file, with modified files', wx.CANCEL  | wx.YES_NO | wx.ICON_EXCLAMATION)
	        dlgResult = dlg.ShowModal()
	        dlg.Destroy()

	        if ( dlgResult == wx.ID_YES ) :
	           self.saveEditor(Context.TAB_EDIT)
	           openFile = True
	        elif ( dlgResult == wx.ID_NO ) :
	           openFile = True
        else:
           openFile = True
        return openFile
       
    def OnBrowserTreeSelChanged(self, event):
        #try :
        item =  event.GetItem()
        itemText = self.browserTree.GetItemText(item)
        if ( itemText != "includes" ):
        
            parentItem = self.browserTree.GetItemParent(item)
            parentText =  self.browserTree.GetItemText(parentItem)
            if self.CheckBrowserModified(parentItem):
            #if not ( self.browserEditor.parentTab.GetPageText(Context.TAB_BROWSER).endswith("*") ):
                if itemText in self.methodsMapping:
                    if self.browserEditor.filename != parentText:
                        self.uiManager.openEditor(2,filename=parentText)
                    line = -1
                    line = EditorUtil.findLineForMethod(self.browserEditor.GetText(),itemText)
                    if line >-1:
                        self.browserEditor.GotoLine(line)
                        self.browserEditor.SetSelectionStart(self.browserEditor.GetLineEndPosition(line)- len(self.browserEditor.GetLine(line))+2)
                        self.browserEditor.SetSelectionEnd(self.browserEditor.GetLineEndPosition(line))                
                else:
                    filename=itemText
                    self.browserEditor.filename = filename
                    #self.browserEditor.SetText(FileUtil.getContentAsText(filename))
                    self.browserEditor.LoadFile(filename)
                    self.browserEditor.ConvertEOLs(STC_EOL_CRLF)
            else:
                self.GetStatusBar().SetStatusText("Can't show this file because the current one hasn't been saved")
        #except : pass # not realy clean handling for now...        
       