# -*- coding: utf-8 -*-
###############################################################################
# Name: jaluino.py                                                            #
# Purpose: Jaluino UI                                                         #
# Author: Sebastien Lelong, but loosely based on                              #
#         Cody Precord <cprecord@editra.org> Launch plugin code               #
# Copyright: (c) 2010 Sebastien Lelong <sebastien.lelong@gmail.com>           #
# License: wxWindows License                                                  #
# Note: this code is an horrible copy/paste from Launch plugin, which         #
# couldn't been adapted by inheritance or something like this (or this would  #
# have resulted in unreadble/unmaintainable code). So, most part is from      #
# Launch plugin, so credit goes to original author Cody Precord. I've just    #
# glued the whole...                                                          #
# Main things I've changed are:                                               #
#  - provide two workers for compile & upload step                            #
#  - deals with arguments' order while building command line                  #
#  - adjust config dialog for compile and upload prefs                        #
#  - provide more buttons for compile and upload                              #
#  - read a special launch XML file to retrieve specific, default commands    #
#  - merge custom commands with original defined in dedicated launch XML file #
###############################################################################

"""Jaluino development board IDE"""

#-----------------------------------------------------------------------------#
# Imports
import os
import wx
import wx.stc

# Local Imports
import cfgdlg

# Editra Libraries
import ed_glob
import util
from profiler import Profile_Get, Profile_Set
import ed_msg
import eclib
import syntax.synglob as synglob

# import placeholder...
handlers = None

#-----------------------------------------------------------------------------#
# Globals
ID_SETTINGS = wx.NewId()

ID_COMPILE = wx.NewId()
ID_COMPILE_EXE = wx.NewId()
ID_COMPILE_ARGS = wx.NewId()

ID_UPLOAD = wx.NewId()
ID_UPLOAD_EXE = wx.NewId()
ID_UPLOAD_ARGS = wx.NewId()

ID_COMPILE_LAUNCH = wx.NewId()
ID_UPLOAD_LAUNCH = wx.NewId()

# Profile Settings Key
JALUINO_KEY = 'Jaluino.Config'

# Custom Messages
MSG_COMPILE = ('jaluino', 'compile')
MSG_UPLOAD = ('jaluino', 'upload')

# Value request messages
REQUEST_ACTIVE = 'Jaluino.IsActive'
REQUEST_RELAUNCH = 'Jaluino.CanRelaunch'

_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

def OnStoreConfig(msg):
    Profile_Set(JALUINO_KEY, handlers.GetState())
ed_msg.Subscribe(OnStoreConfig, cfgdlg.EDMSG_JALUINO_CFG_EXIT)

#-----------------------------------------------------------------------------#

class JaluinoWindow(eclib.ControlBox):
    """Control window for showing and running scripts"""
    def __init__(self, parent):
        self._log = wx.GetApp().GetLog()
        eclib.ControlBox.__init__(self, parent)
        # depends on Launch
        try:
            import launch.handlers as handlersmod
            global handlers
            handlers = handlersmod
        except ImportError:
            msg = _("Launch plugin is missing and is required for Jaluino IDE\nPlease first install Launch plugin.")
            self._log(msg)
            return
            


        # Attributes
        self._mw = self.__FindMainWindow()
        self._buffer = OutputDisplay(self)
        self._fnames = list()
        self._chFiles = None # Created in __DoLayout
        self._compile_worker = None
        self._upload_worker = None
        self._busy = False
        self._isready = False
        self._config = dict(file='', lang=0,
                            cfile='', clang=0,
                            last='', lastlang=0,
                            prelang=0, largs='',
                            lastactionid = 0,
                            lcmd='')
        self._prefs = Profile_Get(cfgdlg.JALUINO_PREFS, default=None)

        # Setup
        self.__DoLayout()
        if not handlers.InitCustomHandlers(ed_glob.CONFIG['CACHE_DIR']):
            util.Log(u"ed_glob.CONFIG: %s" % ed_glob.CONFIG)
            util.Log(u"[jaluino][warn] failed to load jaluino extensions")

        hstate = Profile_Get(JALUINO_KEY)
        if hstate is not None:
            handlers.SetState(hstate)
        if self._prefs is None:
            Profile_Set(cfgdlg.JALUINO_PREFS,
                        dict(autoclear=False,
                             errorbeep=False,
                             defaultf=self._buffer.GetDefaultForeground().Get(),
                             defaultb=self._buffer.GetDefaultBackground().Get(),
                             errorf=self._buffer.GetErrorForeground().Get(),
                             errorb=self._buffer.GetErrorBackground().Get(),
                             infof=self._buffer.GetInfoForeground().Get(),
                             infob=self._buffer.GetInfoBackground().Get(),
                             warnf=self._buffer.GetWarningForeground().Get(),
                             warnb=self._buffer.GetWarningBackground().Get()))
            self._prefs = Profile_Get(cfgdlg.JALUINO_PREFS)

        self._buffer.SetPrefs(self._prefs)
        self.UpdateBufferColors()
        cbuffer = self._mw.GetNotebook().GetCurrentCtrl()
        self.SetupControlBar(cbuffer)
        self._config['lang'] = GetLangIdFromMW(self._mw)
        self.UpdateCurrentFiles(self._config['lang'])
        self.SetFile(GetTextBuffer(self._mw).GetFileName())

        # Setup filetype settings
        self.RefreshControlBar()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        ed_msg.Subscribe(self.OnPageChanged, ed_msg.EDMSG_UI_NB_CHANGED)
        ed_msg.Subscribe(self.OnFileOpened, ed_msg.EDMSG_FILE_OPENED)
        ed_msg.Subscribe(self.OnThemeChanged, ed_msg.EDMSG_THEME_CHANGED)
        ed_msg.Subscribe(self.OnLexerChange, ed_msg.EDMSG_UI_STC_LEXER)
        ed_msg.Subscribe(self.OnConfigExit, cfgdlg.EDMSG_JALUINO_CFG_EXIT)
        ed_msg.Subscribe(self.OnCompileMsg, MSG_COMPILE)
        ed_msg.Subscribe(self.OnUploadMsg, MSG_UPLOAD)
        ed_msg.RegisterCallback(self._CanLaunch, REQUEST_ACTIVE)
        ed_msg.RegisterCallback(self._CanReLaunch, REQUEST_RELAUNCH)

    def __del__(self):
        ed_msg.Unsubscribe(self.OnPageChanged)
        ed_msg.Unsubscribe(self.OnFileOpened)
        ed_msg.Unsubscribe(self.OnThemeChanged)
        ed_msg.Unsubscribe(self.OnLexerChange)
        ed_msg.Unsubscribe(self.OnConfigExit)
        ed_msg.Unsubscribe(self.OnCompileMsg)
        ed_msg.Unsubscribe(self.OnUploadMsg)
        ed_msg.UnRegisterCallback(self._CanLaunch)
        ed_msg.UnRegisterCallback(self._CanReLaunch)
        super(JaluinoWindow, self).__del__()

    def __DoLayout(self):
        """Layout the window"""
        #-- Setup ControlBar --#
        ctrlbar = eclib.ControlBar(self, style=eclib.CTRLBAR_STYLE_GRADIENT)
        if wx.Platform == '__WXGTK__':
            ctrlbar.SetWindowStyle(eclib.CTRLBAR_STYLE_DEFAULT)

        # Preferences
        prefbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU)
        pref = eclib.PlateButton(ctrlbar, ID_SETTINGS, '', prefbmp,
                                 style=eclib.PB_STYLE_NOBG)
        pref.SetToolTipString(_("Settings"))
        ctrlbar.AddControl(pref, wx.ALIGN_LEFT)

        # Compile exe
        ctrlbar.AddControl(wx.StaticText(ctrlbar, label=_("Compile") + ":"),
                           wx.ALIGN_LEFT)
        self._exe_ch = wx.Choice(ctrlbar, ID_COMPILE_EXE)
        self._exe_ch.SetToolTipString(_("Program Executable Command"))
        ctrlbar.AddControl(self._exe_ch, wx.ALIGN_LEFT)

        # Upload exe
        ctrlbar.AddControl(wx.StaticText(ctrlbar, label=_("Upload") + ":"),
                           wx.ALIGN_LEFT)
        self._up_ch = wx.Choice(ctrlbar, ID_UPLOAD_EXE)
        self._up_ch.SetToolTipString(_("Program Executable Command"))
        ctrlbar.AddControl(self._up_ch, wx.ALIGN_LEFT)

        # Upload Args
        # TODO: for now, deactivate extra args
        ##ctrlbar.AddControl((5, 5), wx.ALIGN_LEFT)
        ##ctrlbar.AddControl(wx.StaticText(ctrlbar, label=_("Args") + ":"),
        ##                   wx.ALIGN_LEFT)
        ##args = wx.TextCtrl(ctrlbar, ID_UPLOAD_ARGS)
        ##args.SetToolTipString(_("Upload arguments"))
        ##ctrlbar.AddControl(args, wx.ALIGN_LEFT)


        # Spacer
        ctrlbar.AddStretchSpacer()

        # Script Label
        ctrlbar.AddControl((5, 5), wx.ALIGN_RIGHT)
        self._chFiles = wx.Choice(ctrlbar, wx.ID_ANY)#, choices=[''])
        ctrlbar.AddControl(self._chFiles, wx.ALIGN_RIGHT)
        
        # Compile Button
        rbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
        if rbmp.IsNull() or not rbmp.IsOk():
            rbmp = None
        self._exe_btn = eclib.PlateButton(ctrlbar, ID_COMPILE, _("Compile"), rbmp,
                                style=eclib.PB_STYLE_NOBG)
        ctrlbar.AddControl(self._exe_btn, wx.ALIGN_RIGHT)

        # Upload Button
        ubmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_UP), wx.ART_MENU)
        if ubmp.IsNull() or not ubmp.IsOk():
            ubmp = None
        self._up_btn = eclib.PlateButton(ctrlbar, ID_UPLOAD, _("Upload"), ubmp,
                                style=eclib.PB_STYLE_NOBG)
        ctrlbar.AddControl(self._up_btn, wx.ALIGN_RIGHT)

        # Clear Button
        cbmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_DELETE), wx.ART_MENU)
        if cbmp.IsNull() or not cbmp.IsOk():
            cbmp = None
        self._clr_btn = eclib.PlateButton(ctrlbar, wx.ID_CLEAR, _("Clear"),
                                  cbmp, style=eclib.PB_STYLE_NOBG)
        ctrlbar.AddControl(self._clr_btn, wx.ALIGN_RIGHT)
        ctrlbar.SetVMargin(1, 1)
        self.SetControlBar(ctrlbar)

        self.SetWindow(self._buffer)

    def __FindMainWindow(self):
        """Find the mainwindow of this control
        @return: MainWindow or None

        """
        def IsMainWin(win):
            """Check if the given window is a main window"""
            return getattr(tlw, '__name__', '') == 'MainWindow'

        tlw = self.GetTopLevelParent()
        if IsMainWin(tlw):
            return tlw
        elif hasattr(tlw, 'GetParent'):
            tlw = tlw.GetParent()
            if IsMainWin(tlw):
                return tlw

        return None

    def _CanLaunch(self):
        """Method to use with RegisterCallback for getting status"""
        val = self.CanLaunch()
        if not val:
            val = ed_msg.NullValue()
        return val

    def _CanReLaunch(self):
        """Method to use with RegisterCallback for getting status"""
        val = self.CanLaunch()
        if not val or not len(self._config['last']):
            val = ed_msg.NullValue()
        return val

    def CanLaunch(self):
        """Can the jaluino window run or not
        @return: bool

        """
        parent = self.GetParent()
        return parent.GetParent().IsActive() and self._isready

    def GetFile(self):
        """Get the file that is currently set to be run
        @return: file path

        """
        return self._config['file']

    def GetLastCompile(self):
        """Get the last file that was run
        @return: (fname, lang_id)

        """
        return (self._config['last'], self._config['lastlang'])

    def GetMainWindow(self):
        """Get the mainwindow that created this instance
        @return: reference to MainWindow

        """
        return self._mw

    def OnButton(self, evt):
        """Handle events from the buttons on the control bar"""
        e_id = evt.GetId()
        if e_id == ID_SETTINGS:
            app = wx.GetApp()
            win = app.GetWindowInstance(cfgdlg.ConfigDialog)
            if win is None:
                config = cfgdlg.ConfigDialog(self._mw)
                config.CentreOnParent()
                config.Show()
            else:
                win.Raise()
        elif e_id == ID_COMPILE:
            # May be run or abort depending on current state
            self._config['lastactionid'] = ID_COMPILE
            self.StartStopCompile()
        elif e_id == ID_UPLOAD:
            self._config['lastactionid'] = ID_UPLOAD
            self.StartStopUpload()
        elif e_id == wx.ID_CLEAR:
            self._buffer.Clear()
        else:
            evt.Skip()

    def OnChoice(self, evt):
        """Handle events from the Choice controls
        @param evt: wx.CommandEvent

        """
        e_id = evt.GetId()
        e_sel = evt.GetSelection()
        if e_id == self._chFiles.GetId():
            fname = self._fnames[e_sel]
            self.SetFile(fname)
            self._chFiles.SetToolTipString(fname)
        elif e_id == ID_COMPILE_EXE:
            e_obj = evt.GetEventObject()
            handler = handlers.GetHandlerById(self._config['lang'])
            cmd = e_obj.GetStringSelection()
            e_obj.SetToolTipString(handler.GetCommand(cmd))
        else:
            evt.Skip()

    def OnConfigExit(self, msg):
        """Update current state when the config dialog has been closed
        @param msg: Message Object

        """
        util.Log("[jaluino][info] Saving config to profile")
        self.RefreshControlBar()
        Profile_Set(JALUINO_KEY, handlers.GetState())
        self.UpdateBufferColors()

    @ed_msg.mwcontext
    def OnFileOpened(self, msg):
        """Reset state when a file open message is received
        @param msg: Message Object

        """
        # Update the file choice control
        self._config['lang'] = GetLangIdFromMW(self._mw)
        self.UpdateCurrentFiles(self._config['lang'])

        fname = msg.GetData()
        self.SetFile(fname)

        # Setup filetype settings
        self.RefreshControlBar()

    @ed_msg.mwcontext
    def OnLexerChange(self, msg):
        """Update the status of the currently associated file
        when a file is saved. Used for updating after a file type has
        changed due to a save action.
        @param msg: Message object

        """
        self._log("[jaluino][info] Lexer changed handler - context %d" %
                  self._mw.GetId())

        mdata = msg.GetData()
        # For backwards compatibility with older message format
        if mdata is None:
            return

        fname, ftype = msg.GetData()
        # Update regardless of whether lexer has changed or not as the buffer
        # may have the lexer set before the file was saved to disk.
        if fname:
            #if ftype != self._config['lang']:
            self.UpdateCurrentFiles(ftype)
            self.SetControlBarState(fname, ftype)

    def OnPageChanged(self, msg):
        """Update the status of the currently associated file
        when the page changes in the main notebook.
        @param msg: Message object

        """
        # Only update when in the active window
        if not self._mw.IsActive():
            return

        mval = msg.GetData()
        ctrl = mval[0].GetCurrentCtrl()
        self.UpdateCurrentFiles(ctrl.GetLangId())
        if hasattr(ctrl, 'GetFileName'):
            self.SetupControlBar(ctrl)

    def OnCompileMsg(self, msg):
        """Run or abort a launch process if this is the current 
        jaluino window.
        """
        if self.CanLaunch():
            shelf = self._mw.GetShelf()
            shelf.RaiseWindow(self)
            self.StartStopCompile()

    def OnUploadMsg(self, msg):
        """Re-run the last run program.
        """
        if self.CanLaunch():
            fname, ftype = self.GetLastCompile()
            # If there is no last run file return
            if not len(fname):
                return

            shelf = self._mw.GetShelf()
            self.UpdateCurrentFiles(ftype)
            self.SetFile(fname)
            self.RefreshControlBar()
            shelf.RaiseWindow(self)

            if self._prefs.get('autoclear'):
                self._buffer.Clear()

            self.SetProcessRunning(True)

            self.Compile(fname, self._config['lcmd'], self._config['largs'], ftype)

    def OnThemeChanged(self, msg):
        """Update icons when the theme has been changed
        @param msg: Message Object

        """
        ctrls = ((ID_SETTINGS, ed_glob.ID_PREF),
                 (wx.ID_CLEAR, ed_glob.ID_DELETE))
        if self._busy:
            ctrls += ((ID_COMPILE, ed_glob.ID_STOP),)
        else:
            ctrls += ((ID_COMPILE, ed_glob.ID_BIN_FILE),)

        for ctrl, art in ctrls:
            btn = self.FindWindowById(ctrl)
            bmp = wx.ArtProvider.GetBitmap(str(art), wx.ART_MENU)
            btn.SetBitmap(bmp)
            btn.Refresh()

    def RefreshControlBar(self):
        """Refresh the state of the control bar based on the current config"""
        # TODO this piece of code really needs some serious refactoring, to split and
        # generalize compile and upload actions
        # sanity check
        if not hasattr(synglob,'ID_LANG_JAL') or not hasattr(synglob,'ID_LANG_HEX'):
            util.Log("[jaluino][err] Something is wrong, ID languae JAL and HEX can't be found")
            self._DisableToolbar()
            return

        handler = handlers.GetHandlerById(self._config['lang'])
        uhandler = handlers.GetHandlerByName("hex")
        csel = self._exe_ch.GetStringSelection()
        ucsel = self._up_ch.GetStringSelection()

        compile_enabled = False
        upload_enabled = False
        # if jalv2 relared, enable compile + upload
        if handler.GetName() != "Jalv2":
            util.Log("[jaluino][debug] Not jalv2 related, skip it")
            self._DisableCompileToolbar()
        else:
            compile_enabled = True
            upload_enabled = True
            cmds = handler.GetAliases()
            util.Log("[jaluino][info] Found %s commands: %s" % (handler.GetName(),cmds))
            # Set control states
            self._exe_ch.SetItems(cmds)
            if len(cmds):
                self._exe_ch.SetToolTipString(handler.GetCommand(cmds[0]))
            # auto enable upload stuff
            ucmds = uhandler.GetAliases()
            util.Log("[jaluino][info] Found %s commands: %s" % (uhandler.GetName(),ucmds))
            self._up_ch.SetItems(ucmds)
            if len(ucmds):
                self._up_ch.SetToolTipString(uhandler.GetCommand(ucmds[0]))


        # else if it's just hex related, enable only upload
        if not compile_enabled:
            if handler.GetName() != "Hex":
                util.Log("[jaluino][debug] Not HEX related, skip it")
                self._DisableUploadToolbar()
            else:
                upload_enabled = True
                cmds = handler.GetAliases()
                util.Log("[jaluino][info] Found %s commands: %s" % (handler.GetName(),cmds))
                # Set control states
                self._up_ch.SetItems(cmds)
                if len(cmds):
                    self._up_ch.SetToolTipString(handler.GetCommand(cmds[0]))


        if handler.GetName() != handlers.DEFAULT_HANDLER and len(self.GetFile()):
            self._EnableToolbar(compile_enabled,upload_enabled)
            if self._config['lang'] == self._config['prelang'] and len(csel):
                self._exe_ch.SetStringSelection(csel)
            else:
                csel = handler.GetDefault()
                self._exe_ch.SetStringSelection(csel)
            # deal with upload exec
            if len(ucsel):
                self._up_ch.SetStringSelection(ucsel)
            else:
                ucsel = uhandler.GetDefault()
                self._up_ch.SetStringSelection(ucsel)
            self._up_ch.SetToolTipString(uhandler.GetCommand(ucsel))
            self._exe_ch.SetToolTipString(handler.GetCommand(csel))
            self.GetControlBar().Layout()
        else:
            self._DisableToolbar()

    def _DisableCompileToolbar(self):
        for ctrl in (self._exe_ch,self._exe_btn):
            ctrl.Disable()

    def _DisableUploadToolbar(self):
        for ctrl in (self._up_ch,self._up_btn):
            ctrl.Disable()

    def _DisableToolbar(self):
        self._isready = False
        self._DisableCompileToolbar()
        self._DisableUploadToolbar()
        self._chFiles.Disable()
        self._chFiles.Clear()

    def _EnableCompileToolbar(self):
        for ctrl in (self._exe_ch,self._exe_btn):
            ctrl.Enable()

    def _EnableUploadToolbar(self):
        for ctrl in (self._up_ch,self._up_btn):
            ctrl.Enable()

    def _EnableToolbar(self,compile_enabled,upload_enabled):
        compile_enabled and self._EnableCompileToolbar()
        upload_enabled and self._EnableUploadToolbar()
        self._chFiles.Enable()
        self._isready = True

    def _PreProcess(self,fname):
        # Find and save the file if it is modified
        nb = self._mw.GetNotebook()
        for ctrl in nb.GetTextControls():
            tname = ctrl.GetFileName()
            if fname == tname:
                if ctrl.GetModify():
                    ctrl.SaveFile(tname)
                    break

        path, fname = os.path.split(fname)
        if wx.Platform == '__WXMSW__':
            fname = u"\"" + fname + u"\""
        else:
            fname = fname.replace(u' ', u'\\ ')
        
        return path,fname

    def Compile(self, fname, cmd, args, ftype):
        """Run the given file
        @param fname: File path
        @param cmd: Command to run on file
        @param args: Executable arguments
        @param ftype: File type id

        """
        path,fname = self._PreProcess(fname)
        handler = handlers.GetHandlerById(ftype)
        self._log("[jaluino][info] Running with cmd=%s, fname=%s, args=%s, path=%s, handlenv=%s" % (cmd,fname,args,path,handler.GetEnvironment()))
        self._compile_worker = eclib.ProcessThread(self._buffer,
                                           cmd, fname,
                                           args, path,
                                           handler.GetEnvironment())
        self._compile_worker.start()


    def Upload(self, fname, cmd, args, ftype):
        path,fname = self._PreProcess(fname)
        # if we got a .jal file, we need to check corresponding HEX file exists
        if not fname.endswith(".hex"):
            # first, lowercase
            for ext in (".hex",".HEX"):
                fhex = fname.replace(".jal",ext)
                if os.path.isfile(os.path.join(path,fhex)):
                    break
            else:
                self._buffer.AppendUpdate(_("Can't find generated HEX file from") + " '%s'\n" % fname)
                self._buffer.DoProcessExit(-9)
                return
        else:
            # user selected explicitly a HEX file ?
            fhex = fname
        handler = handlers.GetHandlerById(ftype)
        self._upload_worker = eclib.ProcessThread(self._buffer,
                                           cmd, fhex,
                                           args, path,
                                           handler.GetEnvironment())
        self._upload_worker.start()

    def StartStopCompile(self):
        if self._prefs.get('autoclear'):
            self._buffer.Clear()

        self.SetProcessRunning(not self._busy)
        if self._busy:
            util.Log("[jaluino][info] Start compile")
            handler = handlers.GetHandlerById(self._config['lang'])
            cmd = self.FindWindowById(ID_COMPILE_EXE).GetStringSelection()
            self._config['lcmd'] = cmd
            cmd = handler.GetCommand(cmd)
            args = []
            self._config['largs'] = args
            self.Compile(self._config['file'], cmd, args, self._config['lang'])
        else:
            util.Log("[jaluino][info] Abort compile")
            self._compile_worker.Abort()
            self._compile_worker = None

    def StartStopUpload(self):
        if self._prefs.get('autoclear'):
            self._buffer.Clear()

        self.SetProcessRunning(not self._busy)
        if self._busy:
            util.Log("[jaluino][info] Start upload")
            handler = handlers.GetHandlerByName("hex")
            cmd = self.FindWindowById(ID_UPLOAD_EXE).GetStringSelection()
            self._config['lcmd'] = cmd
            cmd = handler.GetCommand(cmd)
            # TODO: no args for now
            ##args = self.FindWindowById(ID_COMPILE_ARGS).GetValue().split()
            args = []
            self._config['largs'] = args
            self.Upload(self._config['file'], cmd, args, self._config['lang'])
        else:
            util.Log("[jaluino][info] Abort upload")
            self._upload_worker.Abort()
            self._upload_worker = None

    def SetFile(self, fname):
        """Set the script file that will be run
        @param fname: file path

        """
        # Set currently selected file
        self._config['file'] = fname
        self._chFiles.SetStringSelection(os.path.split(fname)[1])
        self.GetControlBar().Layout()

    def SetLangId(self, langid):
        """Set the language id value(s)
        @param langid: syntax.synglob lang id

        """
        self._config['prelang'] = self._config['lang']
        self._config['lang'] = langid

    def SetProcessRunning(self, running=True):
        """Set the state of the window into either process running mode
        or process not running mode.
        @keyword running: Is a process running or not

        """
        self._busy = running
        ##if self._compile_worker and self._compile_worker.isAlive():
        ##    origLabel = _("Compile")
        ##    actionID = ID_COMPILE
        ##elif self._upload_worker and self._upload_worker.isAlive():
        ##    origLabel = _("Upload")
        ##    actionID = ID_UPLOAD
        if self._config['lastactionid'] == ID_COMPILE:
            actionID = ID_COMPILE
            origLabel = _("Compile")
            origIcon = ed_glob.ID_BIN_FILE
        else:
            actionID = ID_UPLOAD
            origLabel = _("Upload")
            origIcon = ed_glob.ID_UP
            
        self._SetProcessRunning(actionID,origLabel,origIcon,running)

    def _SetProcessRunning(self,actionID,origLabel,origIcon,running):
        btn = self.FindWindowById(actionID)
        self._busy = running
        if running:
            self._config['last'] = self._config['file']
            self._config['lastlang'] = self._config['lang']
            self._config['cfile'] = self._config['file']
            self._config['clang'] = self._config['lang']
            abort = wx.ArtProvider.GetBitmap(str(ed_glob.ID_STOP), wx.ART_MENU)
            if abort.IsNull() or not abort.IsOk():
                abort = wx.ArtProvider.GetBitmap(wx.ART_ERROR,
                                                 wx.ART_MENU, (16, 16))
            btn.SetBitmap(abort)
            btn.SetLabel(_("Abort"))
        else:
            rbmp = wx.ArtProvider.GetBitmap(str(origIcon), wx.ART_MENU)
            if rbmp.IsNull() or not rbmp.IsOk():
                rbmp = None
            btn.SetBitmap(rbmp)
            btn.SetLabel(origLabel)
            # If the buffer was changed while this was running we should
            # update to the new buffer now that it has stopped.
            self.SetFile(self._config['cfile'])
            self.SetLangId(self._config['clang'])
            self.RefreshControlBar()

        self.GetControlBar().Layout()
        btn.Refresh()

    def SetupControlBar(self, ctrl):
        """Set the state of the controlbar based data found in the buffer
        passed in.
        @param ctrl: EdStc

        """
        fname = ctrl.GetFileName()
        lang_id = ctrl.GetLangId()
        self.SetControlBarState(fname, lang_id)

    def SetControlBarState(self, fname, lang_id):
        # Don't update the bars status if the buffer is busy
        if self._buffer.IsRunning():
            self._config['cfile'] = fname
            self._config['clang'] = lang_id
        # only react if this is about jal
        else:
            self.SetFile(fname)
            self.SetLangId(lang_id)

            # Refresh the control bars view
            self.RefreshControlBar()

    def UpdateBufferColors(self):
        """Update the buffers colors"""
        colors = dict()
        for color in ('defaultf', 'defaultb', 'errorf', 'errorb',
                      'infof', 'infob', 'warnf', 'warnb'):
            val = self._prefs.get(color, None)
            if val is not None:
                colors[color] = wx.Colour(*val)
            else:
                colors[color] = val

        self._buffer.SetDefaultColor(colors['defaultf'], colors['defaultb'])
        self._buffer.SetErrorColor(colors['errorf'], colors['errorb'])
        self._buffer.SetInfoColor(colors['infof'], colors['infob'])
        self._buffer.SetWarningColor(colors['warnf'], colors['warnb'])

    def UpdateCurrentFiles(self, lang_id):
        """Update the current set of open files that are of the same
        type.
        @param lang_id: Editra filetype id
        @postcondition: all open files that are of the same type are set
                        and stored in the file choice control.

        """
        self._fnames = list()
        for txt_ctrl in self._mw.GetNotebook().GetTextControls():
            if lang_id == txt_ctrl.GetLangId():
                self._fnames.append(txt_ctrl.GetFileName())

        items = [ os.path.basename(fname) for fname in self._fnames ]
        try:
            if len(u''.join(items)):
                self._chFiles.SetItems(items)
                if len(self._fnames):
                    self._chFiles.SetToolTipString(self._fnames[0])
        except TypeError:
            util.Log("[jaluino][err] UpdateCurrent Files: " + str(items))
            self._chFiles.SetItems([''])

#-----------------------------------------------------------------------------#

class OutputDisplay(eclib.OutputBuffer, eclib.ProcessBufferMixin):
    """Main output buffer display"""
    def __init__(self, parent):
        eclib.OutputBuffer.__init__(self, parent)
        eclib.ProcessBufferMixin.__init__(self)

        # Attributes
        self._mw = parent.GetMainWindow()
        self._cfile = ''
        self._prefs = dict()

        # Setup
        font = Profile_Get('FONT1', 'font', wx.Font(11, wx.FONTFAMILY_MODERN,
                                                    wx.FONTSTYLE_NORMAL,
                                                    wx.FONTWEIGHT_NORMAL))
        self.SetFont(font)

    def ApplyStyles(self, start, txt):
        """Apply any desired output formatting to the text in
        the buffer.
        @param start: Start position of new text
        @param txt: the new text that was added to the buffer

        """
        handler = self.GetCurrentHandler()
        style = handler.StyleText(self, start, txt)

        # Ring the bell if there was an error and option is enabled
        if style == handlers.STYLE_ERROR and self._prefs.get('errorbeep', False):
            wx.Bell()

    def DoFilterInput(self, txt):
        """Filter the incoming input
        @param txt: incoming text to filter

        """
        handler = self.GetCurrentHandler()
        return handler.FilterInput(txt)

    def DoHotSpotClicked(self, pos, line):
        """Pass hotspot click to the filetype handler for processing
        @param pos: click position
        @param line: line the click happened on
        @note: overridden from L{eclib.OutputBuffer}

        """
        fname, lang_id = self.GetParent().GetLastCompile()
        handler = handlers.GetHandlerById(lang_id)
        handler.HandleHotSpot(self._mw, self, line, fname)
        self.GetParent().SetupControlBar(GetTextBuffer(self._mw))

    def DoProcessError(self, code, excdata=None):
        """Handle notifications of when an error occurs in the process
        @param code: an OBP error code
        @keyword excdata: Exception string
        @return: None

        """
        if code == eclib.OPB_ERROR_INVALID_COMMAND:
            self.AppendUpdate(_("The requested command could not be executed.") + u"\n")

        # Log the raw exception data to the log as well
        #   2010-02-08: deactivate due to encoding error under windows
        #               (editra-plugins issue 138)
        #   2010-02-13: Guru Cody fixed this in Launch plugin, backport his fix
        if excdata is not None:
            try:
                excstr = str(excdata)
                if not ebmlib.IsUnicode(excstr):
                    excstr = ed_txt.DecodeString(excstr)
                util.Log(u"[jaluino][err] %s" % excdata)
            except UnicodeDecodeError:
                util.Log(u"[jaluino][err] error decoding log message string")

    def DoProcessExit(self, code=0):
        """Do all that is needed to be done after a process has exited"""
        self.AppendUpdate(">>> %s: %d%s" % (_("Exit Code"), code, os.linesep))
        self.Stop()
        self.GetParent().SetProcessRunning(False)

    def DoProcessStart(self, cmd=''):
        """Do any necessary preprocessing before a process is started"""
        self.GetParent().SetProcessRunning(True)
        self.AppendUpdate(">>> %s%s" % (cmd, os.linesep))

    def GetCurrentHandler(self):
        """Get the current filetype handler
        @return: L{handlers.FileTypeHandler} instance

        """
        lang_id = self.GetParent().GetLastCompile()[1]
        handler = handlers.GetHandlerById(lang_id)
        return handler

    def SetPrefs(self, prefs):
        """Set the jaluino prefs
        @param prefs: dict

        """
        self._prefs = prefs

#-----------------------------------------------------------------------------#
def GetLangIdFromMW(mainw):
    """Get the language id of the file in the current buffer
    in Editra's MainWindow.
    @param mainw: mainwindow instance

    """
    ctrl = GetTextBuffer(mainw)
    if hasattr(ctrl, 'GetLangId'):
        return ctrl.GetLangId()

def GetTextBuffer(mainw):
    """Get the current text buffer of the current window"""
    nb = mainw.GetNotebook()
    return nb.GetCurrentCtrl()
