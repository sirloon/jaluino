###############################################################################
# Name: ps_dbgview.py                                                         #
# Purpose: Picshell debug view                                                #
# Author: Albert Faber                                                        #
# Copyright: (c) 2010 Albert Faber                                            #
# License: BSD License                                                        #
###############################################################################

"""
Picshell debug notebook page

@summary: Picshell debug view

"""

__author__ = "Albert Faber"

#--------------------------------------------------------------------------#
# Imports
import wx
import os

# Editra Libraries
import ed_glob
import ed_menu
import ed_msg
import ed_stc
import ed_tab

import ed_txt
import ed_event

from doctools import DocPositionMgr
from profiler import Profile_Get
from util import Log, SetClipboardText
from ebmlib import GetFileModTime
from extern import aui

# External libs
from extern.stcspellcheck import STCSpellCheck

from picshell.ui.debug.DebugView import DebugView


#--------------------------------------------------------------------------#

ID_SPELL_1 = wx.NewId()
ID_SPELL_2 = wx.NewId()
ID_SPELL_3 = wx.NewId()

_ = wx.GetTranslation

def modalcheck(func):
    """Decorator method to add extra modality guards to functions that
    show modal dialogs. Arg 0 must be a Window instance.

    """
    def WrapModal(*args, **kwargs):
        """Wrapper method to guard against multiple dialogs being shown"""
        self = args[0]
        self._has_dlg = True
        func(*args, **kwargs)
        self._has_dlg = False

    WrapModal.__name__ = func.__name__
    WrapModal.__doc__ = func.__doc__
    return WrapModal

#--------------------------------------------------------------------------#

class PsDebugView(wx.Panel, ed_tab.EdTabBase):
    """Tab editor view for main notebook control."""
    ID_NO_SUGGEST = wx.NewId()
    DOCMGR = DocPositionMgr()
    RCLICK_MENU = None


    def __init__(self, plug_parent, mainWindow, id_=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, use_dt=True):
        """Initialize the editor view"""
        # ed_stc.EditraStc.__init__(self, parent, id_, pos, size, style, use_dt)
        
        self.plug_parent = plug_parent
        
        self.IsClosed = False        
        self._log = wx.GetApp().GetLog()
        self.picName = ""
        
        self._mw = mainWindow
        self.noteBook = self._mw.GetNotebook()
        
        wx.Panel.__init__(self, self.noteBook, id_, pos, size, style )
        ed_tab.EdTabBase.__init__(self)
        self.file = ed_txt.EdFile()

        self.debugView = DebugView(self,self)
        

        vboxSplitter = wx.BoxSizer( wx.VERTICAL )
        vboxSplitter.Add(self.debugView.getView(), -1,wx.EXPAND, 0 )
        self.SetSizer(vboxSplitter)
        # self.NewSession()

    def OnBreak(self):
    	self.plug_parent.OnBreak()

    def NewSession(self):
        debuggerStarted = False
        self.debugView.reset()
        self._fnames = list()
        for txt_ctrl in self._mw.GetNotebook().GetTextControls():
            #if lang_id == txt_ctrl.GetLangId():
            if hasattr(txt_ctrl, 'IsActiveJalFile'):
            	if ( txt_ctrl.IsActiveJalFile == True ):
            		self._fnames.append(txt_ctrl.GetFileName())


        currentPage = self.noteBook.GetCurrentPage()
        
        if ( len( self._fnames ) > 0  ):

        	self.dbgfname = self._fnames[0]
        	self._log("[jaluino_debugger][info], set filename to : %s" % self.dbgfname )

			
        	hexFilename = self.dbgfname[:-4] + u".hex"

        	if ( self.debugView.SetupDebugSession( hexFilename, file(self.dbgfname).read(), False ) ):
        		self._log("[jaluino_debugger][info], picname: %s" % self.debugView.picName)
        		debuggerStarted = True
        	else:
        		self._log("[jaluino_debugger][info], SetupDebugSession failed")
        		
			
        else:
        	self._log("[jaluino_debugger][info] No files to debug" )
        	

        # Attributes
        #self._ignore_del = False
        #self._has_dlg = False
        #self._mdata = dict(menu=None, handlers=list(), buff=self)
        #self._lprio = 0     # Idle event priority counter
        #self._spell = STCSpellCheck(self, check_region=self.IsNonCode)
        #spref = Profile_Get('SPELLCHECK', default=dict())
        #self._spell_data = dict(choices=list(),
        #                        word=('', -1, -1),
        #                        enabled=spref.get('auto', False))

        # Initialize the classes position manager for the first control
        # that is created only.
        if not PsDebugView.DOCMGR.IsInitialized():
            PsDebugView.DOCMGR.InitPositionCache(ed_glob.CONFIG['CACHE_DIR'] + \
                                                  os.sep + u'positions')

        if ( debuggerStarted ):
        	self.debugView.run()

        return debuggerStarted
		
		
    def GetLength(self):
    	return 1

    def disableActionWidget(self):
		self.debugView.bNextLang.Disable()

    def enableActionWidget(self):
        self.debugView.bNextLang.Enable()


    def __del__(self):
        ed_msg.Unsubscribe(self.OnConfigMsg)
        super(PsDebugView, self).__del__()

    def _MakeMenu(self, pos):
        menu = ed_menu.EdMenu()
        menu.Append(ed_glob.ID_UNDO, _("Run"))
        menu.Append(ed_glob.ID_REDO, _("Redo"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_CUT, _("Cut"))
        menu.Append(ed_glob.ID_COPY, _("Copy"))
        menu.Append(ed_glob.ID_PASTE, _("Paste"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_TO_UPPER, _("To Uppercase"))
        menu.Append(ed_glob.ID_TO_LOWER, _("To Lowercase"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_SELECTALL, _("Select All"))

        # Allow clients to customize the context menu
        self._mdata['menu'] = menu
        self._mdata['handlers'] = list()
        self._mdata['position'] = self.PositionFromPoint(self.ScreenToClient(pos))
        ed_msg.PostMessage(ed_msg.EDMSG_UI_STC_CONTEXT_MENU,
                           self._mdata,
                           self.GetId())

        # Spell checking
        # TODO: de-couple to the forthcoming buffer service interface
        menu.InsertSeparator(0)
        words = self.GetWordFromPosition(self._mdata['position'])
        self._spell_data['word'] = words
        sugg = self._spell.getSuggestions(words[0])

        # Don't give suggestions if the selected word is in the suggestions list
        if words[0] in sugg:
            sugg = list()

        if not len(sugg):
            item = menu.Insert(0, PsDebugView.ID_NO_SUGGEST, _("No Suggestions"))
            item.Enable(False)
        else:
            sugg = reversed(sugg[:min(len(sugg), 3)])
            ids = (ID_SPELL_1, ID_SPELL_2, ID_SPELL_3)
            del self._spell_data['choices']
            self._spell_data['choices'] = list()
            for idx, sug in enumerate(sugg):
                id_ = ids[idx] 
                self._mdata['handlers'].append((id_, self.OnSpelling))
                self._spell_data['choices'].append((id_, sug))
                menu.Insert(0, id_, sug)

        return menu

    #---- EdTab Methods ----#

    def DoDeactivateTab(self):
        """Deactivate any active popups when the tab is no longer
        the active tab.

        """
        self.HidePopups()

    def DoOnIdle(self):
        if self.IsLoading():
            return
        else:
            pass


    @modalcheck
    def DoReloadFile(self):
        """Reload the current file"""
        ret, rmsg = self.ReloadFile()
        if not ret:
            cfile = self.GetFileName()
            errmap = dict(filename=cfile, errmsg=rmsg)
            mdlg = wx.MessageDialog(self,
                                    _("Failed to reload %(filename)s:\n"
                                      "Error: %(errmsg)s") % errmap,
                                    _("Error"),
                                    wx.OK | wx.ICON_ERROR)
            mdlg.ShowModal()
            mdlg.Destroy()

    def DoTabClosing(self):
    	self.IsClosed = True

    	self.plug_parent.CloseDebugWindow()
    	self.debugView.Close()

        """Save the current position in the buffer to reset on next load"""
        if len(self.GetFileName()) > 1:
            PsDebugView.DOCMGR.AddRecord([self.GetFileName(),
                                           self.GetCurrentPos()])

    def DoTabOpen(self, ):
        """Called to open a new tab"""
        pass

    def DoTabSelected(self):
        """Performs updates that need to happen when this tab is selected"""
        Log("[ed_editv][info] Tab has file: %s" % self.GetFileName())
        self.PostPositionEvent()

    def GetName(self):
        """Gets the unique name for this tab control.
        @return: (unicode) string

        """
        return u"EditraTextCtrl"

    def GetTabMenu(self):
        """Get the tab menu
        @return: wx.Menu
        @todo: move logic from notebook to here
        @todo: generalize generic actions to base class (close, new, etc..)

        """
        ptxt = self.GetTabLabel()

        menu = ed_menu.EdMenu()
        menu.Append(ed_glob.ID_NEW, _("New Tab"))
        menu.Append(ed_glob.ID_MOVE_TAB, _("Move Tab to New Window"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_SAVE, _("Save \"%s\"") % ptxt)
        menu.Append(ed_glob.ID_CLOSE, _("Close \"%s\"") % ptxt)
        menu.Append(ed_glob.ID_CLOSE_OTHERS, _("Close Other Tabs"))
        menu.Append(ed_glob.ID_CLOSEALL, _("Close All"))
        menu.AppendSeparator()
        menu.Append(ed_glob.ID_COPY_PATH, _("Copy Full Path"))
        return menu

    def GetTitleString(self):
        """Get the title string to display in the MainWindows title bar
        @return: (unicode) string

        """
        #fname = self.GetFileName()
        #title = os.path.split(fname)[-1]

        # Its an unsaved buffer
        #if not len(title):
        #    title = fname = self.GetTabLabel()

        ##if selfGetModify() and not title.startswith(u'*'):
        ##    title = u"*" + title
        #return u"%s - file://%s" % (title, fname)
        return u"DEBUGGER"

    def CanCloseTab(self):
        """Called when checking if tab can be closed or not
        @return: bool

        """
        #if self._ignore_del:
        #    return True

        result = True
        #if self.GetModify():
        #    result = self.ModifySave()
        #    result = result in (wx.ID_YES, wx.ID_OK, wx.ID_NO)

        return result

    def OnSpelling(self, buff, evt):
        """Context menu subscriber callback
        @param buff: buffer menu event happened in
        @param evt: MenuEvent

        """
        e_id = evt.GetId()
        replace = None
        for choice in self._spell_data['choices']:
            if e_id == choice[0]:
                replace = choice[1]
                break

        if replace is not None:
            buff.SetTargetStart(self._spell_data['word'][1])
            buff.SetTargetEnd(self._spell_data['word'][2])
            buff.ReplaceTarget(replace)

		
	# AF ADDED 
    def GetDocument(self):
        """Return a reference to the document object represented in this buffer.
        @return: EdFile
        @see: L{ed_txt.EdFile}

        """
        return self.file

    def GetLangId(self):
        """Returns the language identifier of this control
        @return: language identifier of document
        @rtype: int

        """
        #return self._code['lang_id']
        return 0

    def GetEOLMode(self):
        return 0


    def GetFileName(self):
        """Returns the full path name of the current file
        @return: full path name of document

        """
        return self.file.GetPath()

    def PostPositionEvent(self):
        """Post an event to update the status of the line/column"""
        # line, column = self.GetPos()
        #pinfo = dict(lnum=line, cnum=column)
        # msg = _("Line: %(lnum)d  Column: %(cnum)d") % pinfo
        msg = _("DEBUGGER POSTEVENT")
        nevt = ed_event.StatusEvent(ed_event.edEVT_STATUS, self.GetId(), msg, ed_glob.SB_ROWCOL)
        tlw = self.GetTopLevelParent()
        wx.PostEvent(tlw, nevt)
        #ed_msg.PostMessage(ed_msg.EDMSG_UI_STC_POS_CHANGED, pinfo, tlw.GetId())

    def IsLoading(self):
        """Is a background thread loading the text into the file
        @return: bool

        """
        #return self._loading is not None
        return False

    def HidePopups(self):
        """Hide autocomp/calltip popup windows if any are active"""
        #if self.AutoCompActive():
        #    self.AutoCompCancel()

        #if self.CallTipActive():
        #    self.CallTipCancel()

    def GetZoom(self):
		return wx.ID_ZOOM_100
		
    def GetModify(self):
		return True

    def GetCaretLineVisible(self):
		return False

    def GetMarginWidth( self, val ):
		return val
	
    def GetViewWhiteSpace( self ):
		return False	
	
    def GetIndentationGuides(self):
		return False

    def GetEdgeMode(self ):
    	return 0

    def GetViewEOL(self ):
    	return False
		
    def GetBracePair(self ):
    	return (-1, -1)
		
    def GetSelectionStart(self ):
    	return -1
    	
    def GetSelectionEnd(self ):
    	return -1
		
    def GetUseTabs(self ):
    	return False
	
			
    def GetWrapMode(self ):
    	return False

    def GetAutoComplete(self ):
    	return False

    def SetEdgeMode(self, val ):
    	val = val

    def GetAutoIndent(self ):
    	return False

    def IsHighlightingOn(self ):
    	return False


    def IsBracketHlOn(self ):
    	return False

    def IsFoldingOn( self ):
    	return False

    def GetEOLModeId(self ):
    	return 0

	# endif
	
	        
    def OnTabMenu(self, evt):
        """Tab menu event handler"""
        e_id = evt.GetId()
        
        if e_id == ed_glob.ID_COPY_PATH:
            path = self.GetFileName()
            if path is not None:
                SetClipboardText(path)
        elif e_id == ed_glob.ID_MOVE_TAB:
            frame = wx.GetApp().OpenNewWindow()
            nbook = frame.GetNotebook()
            parent = self.GetParent()
            pg_txt = parent.GetRawPageText(parent.GetSelection())
            nbook.OpenDocPointer(self.GetDocPointer(),
                                 self.GetDocument(), pg_txt)
            self._ignore_del = True
            wx.CallAfter(parent.ClosePage)
        elif e_id == ed_glob.ID_CLOSE_OTHERS:
            parent = self.GetParent()
            if hasattr(parent, 'CloseOtherPages'):
                parent.CloseOtherPages()
        elif wx.Platform == '__WXGTK__' and \
             e_id in (ed_glob.ID_CLOSE, ed_glob.ID_CLOSEALL):
            # Need to relay events up to toplevel window on GTK for them to
            # be processed. On other platforms the propagate by them selves.
            wx.PostEvent(self.GetTopLevelParent(), evt)
        else:
            evt.Skip()

    #---- End EdTab Methods ----#

    def IsNonCode(self, pos):
        """Is the passed in position in a non code region
        @param pos: buffer position
        @return: bool

        """
        return self.IsComment(pos) or self.IsString(pos)

    def OnConfigMsg(self, msg):
        """Update config based on profile changes"""
        mtype = msg.GetType()
        mdata = msg.GetData()
        if mtype[-1] == 'SPELLCHECK':
            self._spell_data['enabled'] = mdata.get('auto', False)
            self._spell.setDefaultLanguage(mdata.get('dict', 'en_US'))
            if not self._spell_data['enabled']:
                self._spell.clearAll()
        elif mtype[-1] == 'AUTOBACKUP':
            self.EnableAutoBackup(Profile_Get('AUTOBACKUP'))
        elif mtype[-1] == 'SYNTHEME':
            self.UpdateAllStyles()
        elif mtype[-1] == 'SYNTAX':
            self.SyntaxOnOff(Profile_Get('SYNTAX'))
        elif mtype[-1] == 'AUTO_COMP_EX':
            self.ConfigureAutoComp()

    def OnContextMenu(self, evt):
        """Handle right click menu events in the buffer"""
        if PsDebugView.RCLICK_MENU is not None:
            PsDebugView.RCLICK_MENU.Destroy()
            PsDebugView.RCLICK_MENU = None

        PsDebugView.RCLICK_MENU = self._MakeMenu(evt.GetPosition())
        self.PopupMenu(PsDebugView.RCLICK_MENU)
        evt.Skip()

    def OnMenuEvent(self, evt):
        """Handle context menu events"""
        e_id = evt.GetId()
        handler = None
        for hndlr in self._mdata['handlers']:
            if e_id == hndlr[0]:
                handler = hndlr[1]
                break

        # Handle custom menu items
        if handler is not None:
            handler(self, evt)
        else:
            # Need to relay to tlw on gtk for it to get handled, other
            # platforms do not require this.
            if wx.Platform == '__WXGTK__':
                wx.PostEvent(self.GetTopLevelParent(), evt)
            else:
                evt.Skip()

    def OnModified(self, evt):
        """Overrides EditraBaseStc.OnModified"""
        super(PsDebugView, self).OnModified(evt)

        # Handle word changes to update spell checking
        # TODO: limit via preferences and move to buffer service once
        #       implemented.
        mod = evt.GetModificationType() 
        if mod & wx.stc.STC_MOD_INSERTTEXT or mod & wx.stc.STC_MOD_DELETETEXT: 
            pos = evt.GetPosition() 
            last = pos + evt.GetLength() 
            self._spell.addDirtyRange(pos, last, evt.GetLinesAdded(),
                                      mod & wx.stc.STC_MOD_DELETETEXT) 

    @modalcheck
    def PromptToReSave(self, cfile):
        """Show a dialog prompting to resave the current file
        @param cfile: the file in question

        """
        mdlg = wx.MessageDialog(self,
                                _("%s has been deleted since its "
                                  "last save point.\n\nWould you "
                                  "like to save it again?") % cfile,
                                _("Resave File?"),
                                wx.YES_NO | wx.ICON_INFORMATION)
        mdlg.CenterOnParent()
        result = mdlg.ShowModal()
        mdlg.Destroy()
        if result == wx.ID_YES:
            result = self.SaveFile(cfile)
        else:
            self.SetModTime(0)

    @modalcheck
    def AskToReload(self, cfile):
        """Show a dialog asking if the file should be reloaded
        @param cfile: the file to prompt for a reload of

        """
        mdlg = wx.MessageDialog(self,
                                _("%s has been modified by another "
                                  "application.\n\nWould you like "
                                  "to reload it?") % cfile,
                                  _("Reload File?"),
                                  wx.YES_NO | wx.ICON_INFORMATION)
        mdlg.CenterOnParent()
        result = mdlg.ShowModal()
        mdlg.Destroy()
        if result == wx.ID_YES:
            self.DoReloadFile()
        else:
            self.SetModTime(GetFileModTime(cfile))

    def SetLexer(self, lexer):
        """Override to toggle spell check context"""
        super(PsDebugView, self).SetLexer(lexer)

        if lexer == wx.stc.STC_LEX_NULL:
            self._spell.setCheckRegion(lambda p: True)
        else:
            self._spell.setCheckRegion(self.IsNonCode)

#-----------------------------------------------------------------------------#

    def ModifySave(self):
        """Called when document has been modified prompting
        a message dialog asking if the user would like to save
        the document before closing.
        @return: Result value of whether the file was saved or not

        """
        name = self.GetFileName()
        if name == u"":
            name = self.GetTabLabel()

        dlg = wx.MessageDialog(self,
                                _("The file: \"%s\" has been modified since "
                                  "the last save point.\n\nWould you like to "
                                  "save the changes?") % name,
                               _("Save Changes?"),
                               wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | \
                               wx.ICON_INFORMATION)
        result = dlg.ShowModal()
        dlg.Destroy()

        # HACK
        if result == wx.ID_YES:
            evt = wx.MenuEvent(wx.wxEVT_COMMAND_MENU_SELECTED, ed_glob.ID_SAVE)
            tlw = self.GetTopLevelParent()
            if hasattr(tlw, 'OnSave'):
                tlw.OnSave(evt)

        return result


    def SetFileName(self, path):
        """Set the buffers filename attributes from the given path"""
        path = path        
        #self.file.SetPath(path)

    def EmptyUndoBuffer(self):
		return

    def FireModified(self):
		"""Fire a modified event"""
		return

    def CheckEOL(self):
		return

    def GetCurrentPos(self):
		return 0
		
    def SetCaretPos(self,pos):
		pos = pos
		
    def ScrollToColumn(self,col):
		col = col

    def LoadFile(self, path):
        """Load the file at the given path into the buffer. Returns
        True if no errors and False otherwise. To retrieve the errors
        check the last error that was set in the file object returned by
        L{GetDocument}.
        @param path: path to file

        """
        # Post notification that a file load is starting
        path = path   
        return True
             
    def FindLexer(self, set_ext=u''):
        """Sets Text Controls Lexer Based on File Extension
        @param set_ext: explicit extension to use in search
        @postcondition: lexer is configured for file

        """
        set_ext = set_ext
        
    def SetStatusText(self,text):
		self._log("[jaluino_debugger][info], set SetStatusText to : %s" % text)


    def SetCursor(self,cursor):
		cursor = cursor

    def SetIndent( self, val ):
		self.SetTabTitle( _("Debugger") )        
		
    def SetUseTabs( self, val ):
		val = val
   	
    def GetTextRaw( self ):
    	return _("")
		
    def SetTextRaw( self, value ):
		return
		
    def GetSelection( self ):
    	return (0,0)
    	
    def GetSelectedText( self ):
    	return _("")
    	
    def BeginUndoAction( self ):
    	return

    def EndUndoAction( self ):
    	return
   	