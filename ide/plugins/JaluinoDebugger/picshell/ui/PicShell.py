# -*- encoding: iso-8859-1 -*-
# cool doc here
# http://wiki.wxpython.org/AnotherTutorial
from picshell.engine.util.Format import Format
from picshell.parser.JalV2Parser import JalV2Parser
from picshell.ui.Context import Context
from picshell.ui.UIManager import UIManager
from picshell.ui.browser.BrowserView import BrowserView
from picshell.ui.debug.DebugView import DebugView
from picshell.ui.debug.OutlineDialog import OutlineDialog
from picshell.ui.debug.comp import CLED, Counter, Dual7Seg, LCD, LED, Watch, \
    uart
from picshell.ui.edit.EditView import EditView
from picshell.ui.edit.stc_printer_code import STCPrintout
from picshell.ui.search.SearchView import SearchView
from wx.lib import ogl
from wx.lib.splitter import MultiSplitterWindow
import os
import platform
import sys
import wx

import picshell.icons.embedded_icons


if platform.machine()=='i386':
    import psyco

#
# Main PicShell app
#
class MyFrame(wx.Frame):
    
    
    def __init__(self, parent, id, title):

        self.numsaves = 1        
        self._printData = wx.PrintData()
        self._print_margins_TopLeft =(10,10)
        self._print_margins_BottomRight = (10,10)
        self._print_zoom = 100
        
        ogl.OGLInitialize()
        
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition, wx.Size(600, 600))
       
        #Context.sourcepath = "c:\\picshell\\example" # the default source path proposed when opening files
        #Context.libpath="C:\\JAL\\Libraries"
        #Context.compiler="C:\\JAL\\Compiler\\jalv2.exe"
        Context.load("config.txt")
        
        Context.top= self
        self.CreateStatusBar()
        self.uiManager = UIManager()
        Context.uiManager = self.uiManager
        
        self.rootSplitter = MultiSplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.tab = wx.Notebook(self.rootSplitter,-1,style=wx.SP_NOBORDER)
        self.uiManager.statusBar = self.GetStatusBar()
        self.uiManager.tab = self.tab
        self.uiManager.top=self
        searchView = SearchView(self.rootSplitter,self.uiManager)
        self.searchPanel = searchView.getView()
        self.rootSplitter.AppendWindow(self.searchPanel)
        self.rootSplitter.AppendWindow(self.tab)
        self.rootSplitter.SetOrientation(wx.VERTICAL)
        
        # -------------------------------------------------------
        # build views
        #
        self.debugView = DebugView(self.tab,self.uiManager)
        editView = EditView(self.tab,self.uiManager)
        browserView = BrowserView(self.tab,self.uiManager)
        
        self.uiManager.debugView = self.debugView
        self.uiManager.editView = editView
        self.uiManager.browserView = browserView
        
        #Context.configView = configView.getView()
        self.tab.AddPage(self.debugView.getView(),"Debug view")
        self.tab.AddPage(editView.getView(),"Main file")
        self.tab.AddPage(browserView.getView(),"Includes viewer")
        
        self.tab.Bind(wx.EVT_LEFT_DCLICK,self.OnTabDClick);
        
        #self.tab.AddPage(configView.getView(),"Config")
        
        self.tab.SetSelection(Context.TAB_EDIT)
        self.Centre()
        
        
        
        # -------------------------------------------------------
        # menu Bar
        #
        self.menuBar = wx.MenuBar()
        
        menu2 = wx.Menu()
        menu2.Append(103, "&Compile\t[F9]", "")
        menu2.AppendSeparator()
        menu2.Append(104, "&Reset\t[F4]", "")
        menu2.Append(123, "&Stop\t[F8]", "")
        menu2.Append(124, "&Run\t[F7]", "")
        menu2.AppendSeparator()
        menu2.Append(121, "&Launch programmer", "")
        menu2.AppendSeparator()
        menu2.Append(132, "&JSG validate", "")
        menu2.AppendSeparator()
        menu2.Append(130, "&Port usage", "")
        
        
        menuEdit = wx.Menu()
        
        menuEdit.Append(125, "&Cut\t[Ctrl+X]", "")
        menuEdit.Append(126, "&Copy\t[Ctrl+C]", "")
        menuEdit.Append(127, "&Paste\t[Ctrl+V]", "")
        
        menuEdit.AppendSeparator()
        
        menuEdit.Append(114, "&Select All\t[Ctrl+A]", "")
        menuEdit.AppendSeparator()
        menuEdit.Append(109, "&Find/Replace...\t[Ctrl+F]", "")
        menuEdit.AppendSeparator()
        menuEdit.Append(116, "&Comment/Uncomment selected lines...\t[Ctrl+-]", "")
        menuEdit.Append(120, "&Format code\t[Shift+Ctrl+F]", "")
        
        
        menuNav = wx.Menu()
        menuNav.Append(115, "&Outline search window\t[Ctrl+O]", "")
        menuNav.Append(117, "&Go to declaration\t[Ctrl+H]", "Search the declaration of selected procedure or function, or open selected include file")
        menuNav.AppendSeparator()
        menuNav.Append(118, "Search &Next\t[F3]", "")
        menuNav.Append(119, "Search &Prev\t[Shift+F3]", "")
        menuNav.AppendSeparator()
        menuNav.Append(129, "&Show occurences\t[Ctrl+double click]", "")
        menuNav.AppendSeparator()
        menuNav.Append(128, "&Show Search panel\t[F2]", "",wx.ITEM_CHECK)
        
        
        
        
        menuPref = wx.Menu()
        menuPref.Append(111, "&Preferences...", "")
        
        menuHelp = wx.Menu()
        #menuHelp.Append(112, "&Help...", "")
        #menuHelp.AppendSeparator()
        menuHelp.Append(113, "&About PicShell...", "")
        
        # Add menu to the menu bar
        self.menuBar.Append(self.buildMenu1(), "&File")
        self.menuBar.Append(menuEdit, "&Edit")
        self.menuBar.Append(menuNav, "&Search")
        self.menuBar.Append(menu2, "&Action")
        self.menuBar.Append(menuPref, "&Configuration")
        self.menuBar.Append(menuHelp, "&Help")
        
        self.SetMenuBar(self.menuBar)
        self.Bind(wx.EVT_MENU, self.OnNew, id=100)
        self.Bind(wx.EVT_MENU, self.OnOpen, id=101)
        self.Bind(wx.EVT_MENU, self.OnSave, id=102)
        self.Bind(wx.EVT_MENU, self.OnCompile, id=103)
        self.Bind(wx.EVT_MENU, self.OnReset, id=104)
        self.Bind(wx.EVT_MENU, self.OnMenu_Print_Preview, id=105)
        self.Bind(wx.EVT_MENU, self.OnMenu_Print, id=106)
        self.Bind(wx.EVT_MENU, self.OnMenu_Page_Setup, id=107)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=108)
        self.Bind(wx.EVT_MENU, self.OnFindReplace, id=109)
        self.Bind(wx.EVT_MENU, self.OnImportHex, id=110)
        self.Bind(wx.EVT_MENU, self.OnShowPreferences, id=111)
        self.Bind(wx.EVT_MENU, self.OnShowHelp, id=112)
        self.Bind(wx.EVT_MENU, self.OnShowAbout, id=113)
        self.Bind(wx.EVT_MENU, self.OnSelectAll, id=114)
        self.Bind(wx.EVT_MENU, self.OnShowBrowser, id=115)
        self.Bind(wx.EVT_MENU, self.OnCommentLines, id=116)
       
        
        self.Bind(wx.EVT_MENU, self.OnLocateDeclaration, id=117)
        self.Bind(wx.EVT_MENU, self.OnFindNext, id=118)
        self.Bind(wx.EVT_MENU, self.OnFindPrev, id=119)
        self.Bind(wx.EVT_MENU, self.OnFormatCode, id=120)
        self.Bind(wx.EVT_MENU, self.OnProgram, id=121)
        self.Bind(wx.EVT_MENU, self.OnRun, id=124)
        self.Bind(wx.EVT_MENU, self.OnStop, id=123)
        self.Bind(wx.EVT_MENU, self.OnCut, id=125)
        self.Bind(wx.EVT_MENU, self.OnCopy, id=126)
        self.Bind(wx.EVT_MENU, self.OnPaste, id=127)
        self.Bind(wx.EVT_MENU, self.OnSearchInFiles, id=128)
        self.Bind(wx.EVT_MENU, self.OnShowOccurences, id=129)
        self.Bind(wx.EVT_MENU, self.OnFindPinMapping, id=130)
        self.Bind(wx.EVT_MENU, self.OnExportBundle, id=131)
        self.Bind(wx.EVT_MENU, self.OnJSGValidate, id=132)
        
        

        self.Bind(wx.EVT_MENU, self.OnClose, id=150)
        
        # -------------------------------------------------------
        #Toolbar
        self.toolbar = self.CreateToolBar( wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT | wx.TB_TEXT )

        self.toolbar.AddSimpleTool(Context.TOOL_NEW, wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, size=(16,16)), 'New', '')
        self.toolbar.AddSimpleTool(Context.TOOL_OPEN,wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, size=(16,16)), 'Open', '')
        self.toolbar.AddSimpleTool(Context.TOOL_SAVE,wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, size=(16,16)), 'Save [ctrl+s]', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(Context.TOOL_SHOW_OUTLINE, wx.ArtProvider.GetBitmap(wx.ART_FIND, size=(16,16)), 'Quick outline search [ctrl+o]', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(Context.TOOL_PROGRAM, picshell.icons.embedded_icons.program_icon.GetBitmap(), 'Start programer tool [F10]', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(Context.TOOL_COMPILE, wx.ArtProvider.GetBitmap(wx.ART_EXECUTABLE_FILE, size=(16,16)), 'Compile [F9]', '')
        self.toolbar.AddSimpleTool(Context.TOOL_STOP, picshell.icons.embedded_icons.stop_icon.GetBitmap(), 'Stop [F8]', '')
        self.toolbar.AddSimpleTool(Context.TOOL_RUN, picshell.icons.embedded_icons.run_icon.GetBitmap(), 'Run [F7]', '')
        self.toolbar.AddSeparator()       
        self.toolbar.AddSimpleTool(Context.TOOL_RUN_UNIT_TEST, picshell.icons.embedded_icons.run_unit_icon.GetBitmap(), 'Run as unit test', '')
        
        self.toolbar.EnableTool(Context.TOOL_RUN,False)
        self.toolbar.EnableTool(Context.TOOL_RUN_UNIT_TEST,False)
        
        self.Bind(wx.EVT_TOOL, self.OnOpen, id=Context.TOOL_OPEN)
        self.Bind(wx.EVT_TOOL, self.OnSave, id=Context.TOOL_SAVE)
       
        self.Bind(wx.EVT_TOOL, self.OnNew, id=Context.TOOL_NEW)
        
        self.Bind(wx.EVT_TOOL, self.OnRunUnitTest, id=Context.TOOL_RUN_UNIT_TEST)
        self.Bind(wx.EVT_TOOL, self.OnRun, id=Context.TOOL_RUN)
        self.Bind(wx.EVT_TOOL, self.OnStop, id=Context.TOOL_STOP)
        self.Bind(wx.EVT_TOOL, self.OnCompile, id=Context.TOOL_COMPILE)
        self.Bind(wx.EVT_TOOL, self.OnProgram, id=Context.TOOL_PROGRAM)
        
        self.toolbar.Realize()
        #these tools are not visisble, I do that just for the accelerator shortcut
        self.Bind(wx.EVT_TOOL, self.debugView.OnNextAsm, id=803)
        self.Bind(wx.EVT_TOOL, self.debugView.OnNextLang, id=804)
        self.Bind(wx.EVT_TOOL, self.OnRefreshWatch, id=805)
        self.Bind(wx.EVT_TOOL, self.OnCompileAlternate, id=807)
        self.Bind(wx.EVT_TOOL, self.OnShowBrowser, id=Context.TOOL_SHOW_OUTLINE)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
       
        
        
        #
        # Accelerators
        #
        aTable = wx.AcceleratorTable([\
            (wx.ACCEL_NORMAL, wx.WXK_F5, 803), #next asm
            (wx.ACCEL_NORMAL, wx.WXK_F6, 804), #next lang
            (wx.ACCEL_NORMAL, wx.WXK_F7, Context.TOOL_RUN), # run
            (wx.ACCEL_NORMAL, wx.WXK_F8, Context.TOOL_STOP), # stop
            (wx.ACCEL_NORMAL, wx.WXK_F2, 128), # search panel 
            (wx.ACCEL_NORMAL, wx.WXK_F4, 104), # reset 
            (wx.ACCEL_NORMAL, wx.WXK_F9, 103),  # compile
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('b'), 103),  # compile
            #(wx.ACCEL_SHIFTCTRL, ord('b'), 103),  # compile
            (wx.ACCEL_CTRL, wx.WXK_F9, 807),  # compile alternate
            (wx.ACCEL_NORMAL, wx.WXK_F10, 813),  # programer tool
            
            (wx.ACCEL_NORMAL, wx.WXK_F12, 805),  # refresh watch reg : TODO
            (wx.ACCEL_CTRL, ord('O'), Context.TOOL_SHOW_OUTLINE)  # show outline search dialog
            ])
        self.SetAcceleratorTable(aTable)
        
        if len(sys.argv) == 2:
            self.uiManager.newProject()  
            self.uiManager.openEditor(Context.TAB_EDIT,sys.argv[1])
            Context.stackOpenedFile(sys.argv[1])
            self.rebuildMenuFile();
        else :
            if len(Context.lastOpenedFiles) >0 :
                filename = Context.lastOpenedFiles[0]
                if os.path.exists(filename) :
                    self.uiManager.openEditor(Context.TAB_EDIT,filename=filename,newProject=True)
            
        if Context.APP_SIZE_X  == 0 :
            self.Maximize()
        else :
            self.SetSize((Context.APP_SIZE_X,Context.APP_SIZE_Y))
            self.SetPosition((Context.APP_POS_X,Context.APP_POS_Y)) 
    #
    # Action
    #
    
    #Maximize on/off the window
    def OnTabDClick (self,event): 
        
        if ( self.tab.GetSelection() == Context.TAB_EDIT):
            self.uiManager.tabEditMaximized = not self.uiManager.tabEditMaximized;
            if (self.uiManager.tabEditMaximized) :
                self.lastPos = self.uiManager.editorTopSplitter.GetSashPosition(0)
                self.uiManager.mainSplitter.DetachWindow(self.uiManager.compileTab)
                self.uiManager.editorTopSplitter.DetachWindow(self.uiManager.outlinePanel)
                self.uiManager.compileTab.Hide()
                self.uiManager.outlinePanel.Hide()
            else :
                self.uiManager.mainSplitter.AppendWindow(self.uiManager.compileTab)
                
                self.uiManager.editorTopSplitter.DetachWindow(self.uiManager.editorPanel)
                self.uiManager.editorTopSplitter.AppendWindow(self.uiManager.outlinePanel)
                self.uiManager.editorTopSplitter.AppendWindow(self.uiManager.editorPanel)
                self.uiManager.editorTopSplitter.SetSashPosition(0,self.lastPos)
            
        if ( self.tab.GetSelection() == Context.TAB_BROWSER):
            self.uiManager.tabBrowserMaximized = not self.uiManager.tabBrowserMaximized;
            if (self.uiManager.tabBrowserMaximized) :
                self.uiManager.browserSplitter.DetachWindow(self.uiManager.editorTreePanel)
                self.uiManager.editorTreePanel.Hide()
            else :
                self.uiManager.browserSplitter.AppendWindow(self.uiManager.editorTreePanel)
        
        
    def OnExportBundle(self,event):
        self.uiManager.exportBundle();
        
    def OnJSGValidate(self,event):
        self.uiManager.JSGValidate();
        
        
    def OnShowOccurences (self,event):
        editor = self.uiManager.getEditor(self.tab.GetSelection())
        editor.showOccurences()
        
    def OnSearchInFiles(self,event):
        if event.Checked() :
            self.rootSplitter.SetSashPosition(0,250)
            self.uiManager.deepSearchText.SetFocus()
        else :
            self.rootSplitter.SetSashPosition(0,0)
       
    def OnCommentLines(self,event):
       if self.tab.GetSelection() == Context.TAB_EDIT:
           self.uiManager.mainEditor.toggleCommentSelectedLines()
              
       elif self.tab.GetSelection() == Context.TAB_BROWSER:
           self.uiManager.browserEditor.toggleCommentSelectedLines()

    def OnFindPinMapping(self,event):
        self.uiManager.findPinMapping()
        
    def OnFormatCode(self,event):
        if self.tab.GetSelection() == Context.TAB_EDIT:
           self.uiManager.mainEditor.formatCode()
              
        elif self.tab.GetSelection() == Context.TAB_BROWSER:
           self.uiManager.browserEditor.formatCode()

    def OnCut(self,event):
        editor = self.uiManager.getEditor(self.tab.GetSelection())
        editor.Cut()

    def OnCopy(self,event):
        editor = self.uiManager.getEditor(self.tab.GetSelection())
        editor.Copy()
        
    def OnPaste(self,event):
        editor = self.uiManager.getEditor(self.tab.GetSelection())
        editor.Paste()

    def OnFindNext(self,event):
        editor = self.uiManager.getEditor(self.tab.GetSelection())
        editor.findNext()

    def OnFindPrev(self,event):
        editor = self.uiManager.getEditor(self.tab.GetSelection())
        editor.findPrev()
   
    def OnLocateDeclaration(self,event):
        editor = self.uiManager.getEditor(self.tab.GetSelection())
        editor.locateSelectionDeclaration()  
        
    def OnSelectAll (self,event):
        editor = self.uiManager.getEditor(self.tab.GetSelection())
        editor.SelectAll()  
            
    def buildMenu1(self):
        menu1 = wx.Menu()
        menu1.Append(100, "&New", "New file")
        menu1.Append(101, "&Open File...", "Open jal  file")
        menu1.Append(102, "&Save\t[Ctrl+S]", "Save  file")
        menu1.Append(108, "&Save as...", "Save file as...")
        menu1.AppendSeparator()
        menu1.Append(131, "&Export as zip bundle...", "Export jal file and its dependencies as a single zip file")

        menu1.AppendSeparator()

        menu1.Append(110, "&Import .hex file...", "import an hex file")
        
        menu1.AppendSeparator()
        menu1.Append(107, "&Page setup...", "Print setup")
        menu1.Append(105, "&Print preview...", "Print preview")
        menu1.Append(106, "&Print...", "Print")
        
        if len(Context.lastOpenedFiles[:Context.MAX_RECENT_FILE]) >0 :
            menu1.AppendSeparator()
            index = 0;
            self.menuFiles = {}
            for file in Context.lastOpenedFiles[:Context.MAX_RECENT_FILE] :
                menu1.Append(200+index, file, "Open file "+file)
                self.Bind(wx.EVT_MENU, self.openRecentFile,id=200+index) 
                self.menuFiles[200+index] = file   
                index += 1    
        
        menu1.AppendSeparator()
        menu1.Append(150, "&Exit", "Exit")
        
        return menu1  
        
        
    def CheckOpenFile( self ):
        openFile = False
    
        # AF Check if there are any modified files, if so, show dialog box   
        if ( self.uiManager.browserEditor.parentTab.GetPageText(Context.TAB_EDIT).endswith("*") or  
           self.uiManager.browserEditor.parentTab.GetPageText(Context.TAB_BROWSER).endswith("*") ):

	        dlg = wx.MessageDialog(self, 'Modified files, do you really want to open another file...\n'+
	        'Select cancel to abort exit,\n' +
	        'yes to save the files,\n' +
	        'no to open a new file without saving the modified files',
	          'Open new file, with modified files', wx.CANCEL  | wx.YES_NO | wx.ICON_EXCLAMATION)
	        dlgResult = dlg.ShowModal()
	        dlg.Destroy()

	        if ( dlgResult == wx.ID_YES ) :
	           if self.uiManager.browserEditor.parentTab.GetPageText(Context.TAB_EDIT).endswith("*"):
	               self._save(Context.TAB_EDIT)
	           if self.uiManager.browserEditor.parentTab.GetPageText(Context.TAB_BROWSER).endswith("*"):
	               self._save(Context.TAB_BROWSER)
	           openFile = True
	        elif ( dlgResult == wx.ID_NO ) :
	           openFile = True
        else:
           openFile = True
        return openFile

        
          
    def openRecentFile(self,event):
        if self.CheckOpenFile():
           self.tab.SetSelection( Context.TAB_EDIT )
           self.menuBar.GetMenu(0);
           filename = self.menuFiles[event.GetId()]
           Context.stackOpenedFile(filename)
           self.uiManager.openEditor(Context.TAB_EDIT,filename=filename,newProject=True)
        
    def OnShowBrowser(self,event):
        if self.tab.GetSelection() == Context.TAB_DEBUG:
            dlg = OutlineDialog(self, -1, "Quick Outline",self.uiManager, size=(300, 250),
                         style =  wx.THICK_FRAME | wx.CAPTION)
            dlg.uiManager = self.uiManager
            dlg.tab = Context.TAB_DEBUG
            dlg.CenterOnScreen()
            dlg.setItems(self.getLangListItems())
            val = dlg.ShowModal()
            if val == wx.ID_OK:
                self.uiManager.listLang.SetFocus()
                self.uiManager.listLang.Focus(dlg.pos)
                self.uiManager.listLang.Select(dlg.pos,True)
                self.uiManager.listLang.EnsureVisible(dlg.pos)
            dlg.Destroy()    

        elif self.tab.GetSelection() == Context.TAB_EDIT:
            
            self.showBrowserForEditor(self.uiManager.mainEditor)  
        
        elif self.tab.GetSelection() == Context.TAB_BROWSER:
            self.showBrowserForEditor(self.uiManager.browserEditor)  

    def showBrowserForEditor(self,editor):
        dlg = OutlineDialog(self, -1, "Quick Outline",self.uiManager, size=(300, 250),
                         style =  wx.THICK_FRAME | wx.CAPTION )
        dlg.CenterOnScreen()
        dlg.setItems(self.getEditorItems(editor))
        dlg.uiManager = self.uiManager
        dlg.editor = editor
        val = dlg.ShowModal()
        if val == wx.ID_OK:
           editor.GotoLine(dlg.pos)
        dlg.Destroy()
    
    def getLangListItems(self):
        items = {}
        for i in range (0,self.uiManager.listLang.GetItemCount()): 
            text = self.uiManager.listLang.GetItem(i,Context.COL_CODE).GetText()
            lg = text.strip()
            if lg.upper().startswith("PROCEDURE") or lg.upper().startswith("FUNCTION") :
                name = JalV2Parser.extractMethodeName(lg)
                items[name]=i
            if lg.upper().startswith("FOREVER"):
                items["forever loop"]=i
        return {"items":items,"types":None}
    
    def getEditorItems(self,editor):
        
        items = {}
        #types = {}
        lines = editor.GetText().split("\n")
        for i in range (0,len(lines)): 
            text = lines[i]
            lg = text.strip()
            if lg.upper().startswith("PROCEDURE") or lg.upper().startswith("FUNCTION") :
                name = JalV2Parser.extractMethodeName(lg)
                items[name]=i
            if lg.upper().startswith("FOREVER"):
                items["forever loop"]=i

            #if lg.upper().startswith("VAR "):
            #    name = JalV2Parser.extractVarName(lg)
            #    type = JalV2Parser.extractVarType(lg)
            #    items[name]=i
            #    types[name]="var "+type
            
        return {"items":items,"types":None}
                   
    
      
    def OnNew (self,event):
        self.uiManager.newProject()  


    #
    # Open a lang file
    #
    def OnOpen(self,event):
        if self.CheckOpenFile():
	        self.tab.SetSelection(Context.TAB_EDIT)
	        filename =  self.uiManager.openEditor(Context.TAB_EDIT,newProject=True)
	        if filename != "" :
	            Context.stackOpenedFile(filename)
	            self.rebuildMenuFile()
	        # AF REMOVE? else :
	        # self.uiManager.openEditor(Context.TAB_BROWSER)
     
    def rebuildMenuFile(self):
        mb = self.GetMenuBar()
        mb.Remove(0)
        mb.Insert(0,self.buildMenu1(),"&File")
       
            
    def OnShowPreferences(self,event):
        self.uiManager.showPreferences()
       
    #
    # Save content of the current editor.
    # if current view is debug, save the main file.
    #
    
    def OnSave(self,event):
        self._save()
    
    def OnSaveAs(self,event):
        self._saveAs()
    
    def OnFindReplace (self,event):
        self.uiManager.findReplace()
    
    def OnImportHex(self,event):
        self.uiManager.importHex()
    
    def _saveAs(self,pageNumber=None):
        if pageNumber == None:
            pageNumber = self.tab.GetSelection()
            if pageNumber == Context.TAB_DEBUG :
                pageNumber = Context.TAB_EDIT
            
        filename = self.uiManager.saveEditorAs(pageNumber)
        if (filename !=""):
            self.tab.SetPageText(pageNumber,filename)
            self.uiManager.browserView.updateTree(self.uiManager.mainEditor.filename, self.uiManager.mainEditor.GetText())
            self.uiManager.updateOutLineTree()     
    
    def _save(self,pageNumber=None):
        if pageNumber == None:
            pageNumber = self.tab.GetSelection()
            if pageNumber == Context.TAB_DEBUG :
                pageNumber = Context.TAB_EDIT
                        
        filename = self.uiManager.saveEditor(pageNumber)
        
        if (filename !=""):

            self.uiManager.browserView.updateTree(self.uiManager.mainEditor.filename, self.uiManager.mainEditor.GetText())
            self.uiManager.updateOutLineTree()        

            self.numsaves = self.numsaves + 1
            self.tab.SetPageText(pageNumber,filename)
    def OnProgram(self,event):
       self.uiManager.startProgrammer()
    
    def OnCompile(self,event):

        self._save(Context.TAB_EDIT)
        
        if self.uiManager.getEditor(Context.TAB_BROWSER).filename != "" :
           self._save(Context.TAB_BROWSER)
        
        self.uiManager.compileProject(Context.compiler,Context.libpath,Context.compilerOptions)
        self.tab.SetSelection(Context.TAB_EDIT)    
         
    def OnCompileAlternate(self,event):
        self._save(Context.TAB_EDIT)
        
        if self.uiManager.getEditor(Context.TAB_BROWSER).filename != "" :
           self._save(Context.TAB_BROWSER)

        self.uiManager.compileProjectAlternate()
        self.tab.SetSelection(Context.TAB_EDIT)    
        
    def OnRun(self,event):
       
        self.uiManager.debugView.run()
    
    def OnRunUnitTest(self,event):
        self.tab.SetSelection(Context.TAB_DEBUG) # goto debug tab
        self.uiManager.runUnitTest()
        
    def OnStop(self,event):
        self.uiManager.debugView.stop()
    def OnReset(self,event):
        self.uiManager.debugView.reset()
    def OnRefreshWatch(self,event):
        pass
    
            
    def OnClose(self,event):

        # AF Check if there are any modified files, if so, show dialog box   
        if ( self.uiManager.browserEditor.parentTab.GetPageText(Context.TAB_EDIT).endswith("*") or  
           self.uiManager.browserEditor.parentTab.GetPageText(Context.TAB_BROWSER).endswith("*") ):

	        dlg = wx.MessageDialog(self, 'Modified files, do you really want to exit...\n'+
	        'Select cancel to abort exit,\n' +
	        'yes to save the files,\n' +
	        'no to exit without saving the modified files',
	          'Exit application with modified files', wx.CANCEL  | wx.YES_NO | wx.ICON_EXCLAMATION)
	        dlgResult = dlg.ShowModal()
	        dlg.Destroy()

	        if ( dlgResult == wx.ID_YES ) :
	           if self.uiManager.browserEditor.parentTab.GetPageText(Context.TAB_EDIT).endswith("*"):
	               self._save(Context.TAB_EDIT)
	           if self.uiManager.browserEditor.parentTab.GetPageText(Context.TAB_BROWSER).endswith("*"):
	               self._save(Context.TAB_BROWSER)
	               
	           self.uiManager.close(event)
	        elif ( dlgResult == wx.ID_NO ) :
	           self.uiManager.close(event)	                   
        else:
           self.uiManager.close(event)
        
    def OnShowHelp(self,event):
        pass
    def OnShowAbout(self,event):
        dlg = wx.MessageDialog(self, 'PicShell '+PicShell.VERSION+' by Olivier Carnal.\n\n'+
        'This program contains contributions by\n\n'+
        ' - Stef Mientki\n'+
        ' - Jeroen Wouters\n'+
        ' - Albert Faber',
          'About', wx.OK  | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnMenu_Print ( self, event ) :
        pdd = wx.PrintDialogData ()
        pdd.SetPrintData ( self._printData )
        printer = wx.Printer ( pdd )
        printout = STCPrintout ( self.uiManager.getEditor(self.tab.GetSelection()),
                                 self._printData,
                                 self._print_margins_TopLeft,
                                 self._print_margins_BottomRight,
                                 "")
                                     #JG.Active_JAL_File )
    
        if not printer.Print ( self, printout ) :
          #JG.em ( 'Print' )
          print "print"
        else:
          self.printData = wx.PrintData ( printer.GetPrintDialogData().GetPrintData() )
        printout.Destroy()

    def OnMenu_Print_Preview ( self, event ) :
        filename = "" #JG.Active_JAL_File
        
        po1 = STCPrintout ( self.uiManager.getEditor(self.tab.GetSelection()),
                            self._printData,
                            self._print_margins_TopLeft,
                            self._print_margins_BottomRight,
                            filename )
        po2 = STCPrintout ( self.uiManager.getEditor(self.tab.GetSelection()),
                            self._printData,
                            self._print_margins_TopLeft,
                            self._print_margins_BottomRight,
                            filename )
        printPreview = wx.PrintPreview ( po1, po2, self._printData )
        printPreview.SetZoom ( self._print_zoom)
        if not printPreview.Ok():
          #JG.em ( 'Print Preview' )
          print "";
          return
    
        frame = wx.PreviewFrame ( printPreview, self, "Print Preview   " + filename )
        frame.Initialize ()
        frame.Maximize ()
        frame.Show ( True )
        
    
    def OnMenu_Page_Setup ( self, event ) :
        # there seems to be 3 almost identical datasets:
        #    PrintData, PrintDialogData, PageSetupDialogData
        # PageSetupDialogData, seems to have the best overall set
        # but for example no orientation :-(
    
        # Create dataset, and copy the relevant data
        #   from printData and margins into this dataset
        dlgData = wx.PageSetupDialogData ( self._printData )
        dlgData.SetDefaultMinMargins ( True )
        dlgData.SetMarginTopLeft ( self._print_margins_TopLeft )
        dlgData.SetMarginBottomRight ( self._print_margins_BottomRight )
    
        # start page setup dialog
        printDlg = wx.PageSetupDialog ( self, dlgData )
        if printDlg.ShowModal () == wx.ID_OK :
          # if ok, copy data back into globals
          dlgData = printDlg.GetPageSetupData ()
          self._printData = wx.PrintData ( dlgData.GetPrintData () )
          self._print_margins_TopLeft = dlgData.GetMarginTopLeft ()
          self._print_margins_BottomRight = dlgData.GetMarginBottomRight ()
    
          # store data in inifile
        printDlg.Destroy()
   
       
#       
# Main App
#    
class PicShell(wx.App):
    VERSION = "2.10 beta"
    def OnInit(self):
        self.frame = MyFrame(None, -1, 'PicShell '+PicShell.VERSION)
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        Context.app = self
        Context.frame = self.frame;
        uiManager = Context.uiManager
        
        #browser sash
        browserPos = 600
        if Context.BROWSER_SASH_POSITION != 0 :
            browserPos = Context.BROWSER_SASH_POSITION 
        
        # AF CHECK uiManager.debugView.browserSplitter.SetSashPosition(0,browserPos)    
        
        # Editor's sash
        uiManager.editView.mainSplitter.SetSashPosition(0,self.frame.GetSize()[1]-self.frame.GetSize()[1]/2)
        uiManager.editView.editorTopSplitter.SetSashPosition(0,200)
        
        #debug sash
        uiManager.debugView.mainSplitter.SetSashPosition(self.frame.GetSize()[1]/2)
        uiManager.debugView.bottomSplitter.SetSashPosition(self.frame.GetSize()[0]/2)
        uiManager.debugView.topSplitter.SetSashPosition(self.frame.GetSize()[0]/2)
        
        # search sash (closed by default)
        self.frame.rootSplitter.SetSashPosition(0,0)
        #self.frame.Bind(wx.EVT_MAXIMIZE, self.OnResize)
        #self.frame.Bind(wx.EVT_SIZING, self.OnResize)
        self.frame.Bind(wx.EVT_SIZE, self.OnResize)
        self.pos =  uiManager.mainSplitter.GetSashPosition(0);
        self.pos = self.frame.GetSize()[1] - self.pos
        
        uiManager.editView.mainSplitter.Bind(wx.EVT_LEFT_UP,self.OnSashChanged)
        
        return True
    
    def OnSashChanged(self,event):
        
         uiManager  = Context.uiManager
         self.pos =  uiManager.mainSplitter.GetSashPosition(0);
         self.pos = self.frame.GetSize()[1] - self.pos
         event.Skip();
    
    def OnResize(self,event):
        #print self.frame.GetSize()[1]
        uiManager  = Context.uiManager
        uiManager.mainSplitter.SetSashPosition(0,self.frame.GetSize()[1]-self.pos)
        self.pos =  uiManager.mainSplitter.GetSashPosition(0);
        self.pos = self.frame.GetSize()[1] - self.pos
        event.Skip();
# start
if platform.machine()=='i386':
    psyco.full()
    

app = PicShell(0)
app.MainLoop()

