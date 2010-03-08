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
import os, sys
import re
import types as pytypes
import subprocess
import wx
import wx.stc
import zipfile, StringIO

# Local Imports
import cfgdlg
import jalcomp
import jalutil

# Editra Libraries
import ed_glob
import ebmlib
import ed_mdlg
import ed_txt
import util
from profiler import Profile_Get, Profile_Set
import ed_msg
import eclib
import syntax.synglob as synglob
import syntax.syntax as syntax
from ed_menu import EdMenuBar, EdMenu

try:
    import jallib
    HAS_JALLIB = True
except ImportError:
    HAS_JALLIB = False

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

ID_OPEN_LIBRARY = wx.NewId()
ID_JSG_VALIDATE = wx.NewId()
ID_OPEN_DEPS = wx.NewId()
ID_CLOSE_DEPS = wx.NewId()
ID_BACKUP = wx.NewId()

# Profile Settings Key
JALUINO_KEY = 'Jaluino.Config'

# Custom Messages
MSG_COMPILE = ('jaluino', 'compile')
MSG_UPLOAD = ('jaluino', 'upload')
MSG_VALIDATE = ('jaluino', 'validate')
MSG_OPEN_DEPS = ('jaluino', 'opendeps')
MSG_CLOSE_DEPS = ('jaluino', 'closedeps')
MSG_BACKUP = ('jaluino', 'backup')
MSG_SETTINGS = ('jaluino', 'settings')

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

        try:
            import codebrowser
            self.codebrowser = codebrowser
            import codebrowser.tagload
            codebrowser.tagload.LOAD_MAP[synglob.ID_LANG_JAL] = "jaluino.jalbrowser"
        except ImportError:
            msg = _("[jaluino][warn] CodeBrowser plugin is missing. If not required, it can make you life easier...")
            self._log(msg)

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
        self._hexfinder = re.compile('^("?)(.*)\.hex("?)$',re.IGNORECASE)   # on win, " encloses filename

        # Setup
        self.__DoLayout()

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

        # Menu
        ##EnableJaluinoMenu(self._mw)

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
        ed_msg.Subscribe(self.OnValidateMsg, MSG_VALIDATE)
        ed_msg.Subscribe(self.OnOpenDependenciesMsg, MSG_OPEN_DEPS)
        ed_msg.Subscribe(self.OnCloseDependenciesMsg, MSG_CLOSE_DEPS)
        ed_msg.Subscribe(self.OnBackupMsg, MSG_BACKUP)
        ed_msg.Subscribe(self.OnSettingsMsg, MSG_SETTINGS)
        ed_msg.Subscribe(self.OnContextMessage,ed_msg.EDMSG_UI_STC_CONTEXT_MENU)
        ed_msg.Subscribe(self.OnTabContextMessage,ed_msg.EDMSG_UI_NB_TABMENU)
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
        ed_msg.Unsubscribe(self.OnValidateMsg)
        ed_msg.Unsubscribe(self.OnOpenDependenciesMsg)
        ed_msg.Unsubscribe(self.OnCloseDependenciesMsg)
        ed_msg.Unsubscribe(self.OnSettingsMsg)
        ed_msg.Unsubscribe(self.OnContextMessage)
        ed_msg.Unsubscribe(self.OnTabContextMessage)
        ed_msg.UnRegisterCallback(self._CanLaunch)
        ed_msg.UnRegisterCallback(self._CanReLaunch)
        ##EnableJaluinoMenu(self._mw,False)
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
        self._exe_ch.SetToolTipString(_("Compilation Command"))
        ctrlbar.AddControl(self._exe_ch, wx.ALIGN_LEFT)

        # Upload exe
        ctrlbar.AddControl(wx.StaticText(ctrlbar, label=_("Upload") + ":"),
                           wx.ALIGN_LEFT)
        self._up_ch = wx.Choice(ctrlbar, ID_UPLOAD_EXE)
        self._up_ch.SetToolTipString(_("Upload Command"))
        ctrlbar.AddControl(self._up_ch, wx.ALIGN_LEFT)

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
        # Don't check if maindow is active, to enable tab context menu. 
        # (I can't understand why it's needed, but... if things go crazy,
        # there might be something to look here
        return self._isready

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
            self.OnSettings()
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
        elif e_id == ID_UPLOAD_EXE:
            e_obj = evt.GetEventObject()
            uhandler = handlers.GetHandlerByName("hex")
            cmd = e_obj.GetStringSelection()
            e_obj.SetToolTipString(uhandler.GetCommand(cmd))
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
        # normalize serial/usb values
        cfg = Profile_Get(cfgdlg.JALUINO_PREFS, default={})
        if cfg.get("serial.port.choice","available") == "available":
            cfg['serial.port'] = cfg.get("serial.port.available")
        else:
            cfg['serial.port'] = cfg.get("serial.port.custom")
        if cfg.get("serial.baudrate.choice","available") == "available":
            cfg['serial.baudrate'] = cfg.get("serial.baudrate.available")
        else:
            cfg['serial.baudrate'] = cfg.get("serial.baudrate.custom")
        Profile_Set(cfgdlg.JALUINO_PREFS,cfg)

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
        ##ctx = msg.GetContext()
        ##zetab = elf._mw._mpane.GetNotebook().GetPage(xxx)

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
        # TODO enable/disable menu items when jalv2 related or not

    def OnCompileMsg(self, msg):
        """Run or abort a launch process if this is the current 
        jaluino window.
        """
        if self.CanLaunch():
            shelf = self._mw.GetShelf()
            shelf.RaiseWindow(self)
            self.StartStopCompile()

    def OnUploadMsg(self, msg):
        if self.CanLaunch():
            shelf = self._mw.GetShelf()
            shelf.RaiseWindow(self)
            self.StartStopUpload()

    def OnValidateMsg(self, msg):
        buff = GetTextBuffer(self._mw)
        self.OnValidate(buff)

    def OnOpenDependenciesMsg(self,msg):
        buff = GetTextBuffer(self._mw)
        self.OnOpenDependencies(buff)
        
    def OnCloseDependenciesMsg(self,msg):
        buff = GetTextBuffer(self._mw)
        self.OnCloseDependencies(buff)

    def OnBackupMsg(self,msg):
        buff = GetTextBuffer(self._mw)
        self.OnBackup(buff)

    def OnSettingsMsg(self,msg):
        self.OnSettings()

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
            util.Log("[jaluino][err] Something is wrong, ID language JAL and HEX can't be found")
            self._DisableToolbar()
            return

        handler = handlers.GetHandlerById(self._config['lang'])
        uhandler = handlers.GetHandlerByName("hex")
        csel = self._exe_ch.GetStringSelection()
        ucsel = self._up_ch.GetStringSelection()

        compile_enabled = False
        upload_enabled = False
        # if jalv2 relared, enable compile + upload
        # and enable/disable Jaluino menu (not triggered by HEX related files)
        if handler.GetName() != "Jalv2":
            util.Log("[jaluino][debug] Not jalv2 related, skip it")
            self._DisableCompileToolbar()
            EnableJaluinoMenu(self._mw,False)
        else:
            EnableJaluinoMenu(self._mw)
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

        # restore indentation from default (because not jalv2 related, since
        # compile is disabled)
        cbuffer = self._mw.GetNotebook().GetCurrentCtrl()
        cbuffer.SetIndent(Profile_Get('INDENTWIDTH', 'int'))
        cbuffer.SetUseTabs(Profile_Get('USETABS'))

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

        # force indentation to 3 spaces (since compile is enable, 
        # this means it's jalv2 related...)
        cbuffer = self._mw.GetNotebook().GetCurrentCtrl()
        cbuffer.SetIndent(3)
        cbuffer.SetUseTabs(False)

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

    def GetEnv(self,handenv):
        #cfg = Profile_Get(cfgdlg.JALUINO_PREFS, default={})
        cfg = jalutil.GetJaluinoPrefs()
        handenv.update(cfg)
        # adjust path with JALUINO_BIN
        path = handenv.get("PATH","")
        path = path + os.pathsep + os.pathsep.join([cfg.get('JALUINO_BIN',""),os.path.dirname(cfg.get('JALLIB_JALV2',""))])
        handenv['PATH'] = path
        return handenv

    def GetMainFile(self):
        # in case none selection, main is '', idx is -1...
        main = self._chFiles.GetStringSelection()
        idx = self._chFiles.GetSelection()
        if not main or idx < 0:
            return self._config['file']
        try:
            # look at fnames to have full path. even if tab is moved, order is the same
            # so we should get the correct index
            abspath = self._fnames[idx]
            if not abspath.endswith(main):
                raise ValueError("Absolute path '%s' isn't related to '%s'..." % (abspath,main))
            main = abspath
        except Exception,e:
            # failed to get correct path, back to original behavior
            util.Log("[jaluino][info] Couldn't find absolute path for '%s': %s" % (main,e))
            main = self._config['file']
        
        return main

    def Compile(self, fname, cmd, args, ftype):
        """Run the given file
        @param fname: File path
        @param cmd: Command to run on file
        @param args: Executable arguments
        @param ftype: File type id

        """
        path,fname = self._PreProcess(fname)
        handler = handlers.GetHandlerById(ftype)

        # Potentially enrich/format registered command with configuration values
        try:
            env = self.GetEnv(handler.GetEnvironment())
            cmd = cmd % env
        except (KeyError,TypeError,ValueError),e:
            self._log("[jaluino][err] Unable to format command because: %s" % e)
            wx.MessageBox(_("Something wrong happened\nDid you setup preferences correctly ?\n\nError was: %s" % e),
                               _("Restart needed"))

        self._log("[jaluino][info] Compiling with cmd=%s, fname=%s, args=%s, path=%s, env=%s" % (cmd,fname,args,path,env))
        self._compile_worker = eclib.ProcessThread(self._buffer,cmd,fname,args,path,env,use_shell=False)
        self._compile_worker.start()


    def Upload(self, fname, cmd, args, ftype):
        # if we got a .jal file, we need to check corresponding HEX file exists
        if not self._hexfinder.match(fname):
            # first, lowercase
            for ext in (".hex",".HEX"):
                fhex = fname.replace(".jal",ext)
                if os.path.isfile(fhex):
                    break
            else:
                self._buffer.AppendUpdate("Can't find generated HEX file from '%s'\n" % fname)
                self._buffer.DoProcessExit(-9)
                return
        else:
            # user selected explicitly a HEX file ?
            fhex = fname

        handler = handlers.GetHandlerById(ftype)

        path,fhex = self._PreProcess(fhex)

        # Potentially enrich/format registered command with configuration values
        try:
            # complete with Jaluino specific variables and  global env. vars
            env = self.GetEnv(handler.GetEnvironment())
            cmd = cmd % env
        except (KeyError,TypeError,ValueError),e:
            self._log("[jaluino][err] Unable to format command because: %s" % e)
            wx.MessageBox(_("Something wrong happened\nDid you setup preferences correctly ?\n\nError was: %s" % e),
                               _("Restart needed"))

        self._log("[jaluino][info] Uploading with cmd=%s, fname=%s, args=%s, path=%s, env=%s" % (cmd,fname,args,path,env))
        self._upload_worker = eclib.ProcessThread(self._buffer,cmd,fhex,args,path,env,use_shell=False)
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
            tocompile = self.GetMainFile()
            self.Compile(tocompile, cmd, args, self._config['lang'])
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
            args = []
            self._config['largs'] = args
            toupload = self.GetMainFile()
            self.Upload(toupload, cmd, args, self._config['lang'])
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

        if ( ( len(fname) > 4 ) and ( fname[len(fname)-4:].lower() == ".jal" ) ):
            util.Log("[jaluino][debug] SetFile, is a JALV2 file :%s:" % fname)
            for txt_ctrl in self._mw.GetNotebook().GetTextControls():
                txt_ctrl.IsActiveJalFile = False
                util.Log("[jaluino][debug] SetActiveJALFileName to False for file :%s:" % txt_ctrl.GetFileName())
                if txt_ctrl.GetFileName() == fname :
                    txt_ctrl.IsActiveJalFile = True
                    util.Log("[jaluino][debug] SetActiveJALFileName to True for file :%s:" % txt_ctrl.GetFileName())
        else:
            util.Log("[jaluino][debug] SetFile, not a JALV2 file :%s:" % fname)
                
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
                
            # txt_ctrl.IsActiveJalFile = False
            
        items = [ os.path.basename(fname) for fname in self._fnames ]
        prev = self._chFiles.GetStringSelection()
        try:
            if len(u''.join(items)):
                self._chFiles.SetItems(items)
                if len(self._fnames):
                    self._chFiles.SetToolTipString(self._fnames[0])
            self._chFiles.SetStringSelection(prev)
        except TypeError:
            util.Log("[jaluino][err] UpdateCurrent Files: " + str(items))
            self._chFiles.SetItems([''])

    def OnTabContextMessage(self,msg):
        data = msg.GetData()
        menu = data.GetMenu()
        page = data.GetUserData('page')
        if page.GetLangId() != synglob.ID_LANG_JAL:
            return
        menu.AppendSeparator()
        BuildFileRelatedMenu(self._mw,menu)

    def OnContextMessage(self,msg):
        data = msg.GetData()
        buff = data.GetUserData('buffer')
        # is it even jalv2 related ?
        if buff.GetLangId() != synglob.ID_LANG_JAL:
            return

        # Do we have a decent completer ?
        comp = buff.GetCompleter()
        if not isinstance(comp,jalcomp.Completer):
            return

        menu = data.GetMenu()
        menu.AppendSeparator()

        txt = buff.GetSelectedText()
        # View <symbolname> code
        for command in comp._registered_symbol.keys():
            if comp._registered_symbol[command].has_key(txt.lower()):
                menu_item = menu.Append(ID_OPEN_LIBRARY,_("View") + u" " + txt + u" " + _("code"))
                data.AddHandler(ID_OPEN_LIBRARY,self.OnOpenLibrary)

    def OnOpenLibrary(self,buff,event_obj):
        chars = buff.GetSelectedText()
        comp = buff.GetCompleter()
        for command in comp._registered_symbol.keys():
            apis = comp.GetAPIs(chars,command)
            if len(apis) > 1:
                util.Log(u"[jaluino][warn] More than one API definition for %s (found %s)" % (chars,len(apis)))
            if apis:
                # fow now, only consider first definition
                api = apis[0]
                # HACK: because this is called from within a buffer, and because OpenLibrary may switch
                # to an existing tab if file already opened, we need to use wx.CallLater() because Cody
                # said: "switching context to the new buffer before the event loop as exiting the handling
                # of the context menu in the other buffer [may cause troubles]"
                # wx.CallAfter() will ensure this will be called after the event loop has processed 
                # the context menu
                if command == "include":
                    wx.CallAfter(self.OpenLibrary,chars)
                else:
                    _,_,libfile,line,_ = api
                    wx.CallAfter(self.OpenLibrary,libfile,line)
 
    def GetLibraryPath(self,libname):
        jalfile = "%s.jal" % libname
        path = jalcomp.JALLIBS.get(jalfile)
        return path

    def OpenLibrary(self,libname,line=0):
        # deactivate history when loading dependency
        fhist = Profile_Get('FHIST_LVL')
        try:
            Profile_Set('FHIST_LVL', 0)
            path = self.GetLibraryPath(libname)
            nb = self.GetMainWindow().GetNotebook()
            if not path and libname:
                # maybe it's file path, not a libname ?
                path = os.path.exists(libname) and libname
            if path:
                nb.OpenPage(ebmlib.GetPathName(path),
                                    ebmlib.GetFileName(path),quiet=True)
                nb.GoCurrentPage()
            # we may stay in current buffer, still need to move to a line
            if line:
                page = nb.GetCurrentPage()
                page.GotoLine(line)
        finally:
            # restore previous settting
            Profile_Set('FHIST_LVL', fhist)

    def CloseLibrary(self,libname):
        nb = self.GetMainWindow().GetNotebook()
        path = self.GetLibraryPath(libname)
        nb.GotoPage(path)
        # this won't close modified tabs because there's a "*" in label
        label = nb.GetCurrentPage().GetTabLabel()
        if path and label == os.path.basename(path):
            # this means we've found the page
            nb.GoCurrentPage()
            nb.ClosePage()

    def OnValidate(self,buff,event_obj=None):
        jalfile = buff.GetFileName()
        if not jalfile:
            self._buffer.AppendUpdate(u">>> No JAL file to validate..\n")
            self._buffer._OutputBuffer__FlushBuffer()
            return
        self._PreProcess(jalfile)
        # set last lang/fname, so Editra can find file handler (highlight output)
        self._config['last'] = jalfile
        self._config['lastlang'] = synglob.ID_LANG_JAL
        self._buffer.AppendUpdate(_(">>> Checking") + u" " + jalfile  + u"\n")
        jallib.validate(jalfile)

        jalfile = os.path.basename(jalfile)
        self._buffer.AppendUpdate("%d errors found\n" % len(jallib.errors))
        if jallib.errors:
            for err in jallib.errors:
                self._buffer.AppendUpdate(u"\tERROR: %s:%s\n" % (jalfile,err))

        self._buffer.AppendUpdate("%d warnings found\n" % len(jallib.errors))
        if jallib.warnings:
            for warn in jallib.warnings:
                self._buffer.AppendUpdate(u"\twarning: %s:%s\n" % (jalfile,err))

        if jallib.errors or jallib.warnings:
            self._buffer.AppendUpdate(u"\n%s:1: is not JSG compliant !\n\n" % jalfile)
        else:
            self._buffer.AppendUpdate(u"\n%s is JSG compliant :)\n\n" % jalfile)

        # HACK: calling a private method...
        self._buffer._OutputBuffer__FlushBuffer()

    def IdentidyDependencies(self,api):
        deps = []
        for libname in api['include']:
            path = self.GetLibraryPath(libname['name'])
            if path:
                deps.append((libname['name'],path))
                api = jallib.api_parse([path]).values()[0]
                deps.extend(self.IdentidyDependencies(api))
        return deps

    def OpenDependencies(self,api,close=False):
        deps = self.IdentidyDependencies(api)
        if close:
            func = self.CloseLibrary
        else:
            func = self.OpenLibrary
        for libname,path in deps:
            func(libname)
        
    def OnOpenDependencies(self,buff,event_obj=None):
        try:
            # EdEditorView
            txt = buff.GetText().splitlines()
        except AttributeError:
            # EdPages
            txt = buff.GetCurrentPage().GetText().splitlines()
        api = jallib.api_parse_content(txt,strict=False)
        self.OpenDependencies(api)

    def OnCloseDependencies(self,buff,event_obj=None):
        txt = buff.GetText().splitlines()
        api = jallib.api_parse_content(txt,strict=False)
        self.OpenDependencies(api,close=True)

    def OnBackup(self,buff,event_obj=None):
        backup = []
        # first save current file
        jalfile = buff.GetFileName()
        self._PreProcess(jalfile)
        backup.append(jalfile.encode(sys.getfilesystemencoding()))
        # explore dependencies
        txt = buff.GetText().splitlines()
        api = jallib.api_parse_content(txt,strict=False)
        deps = self.IdentidyDependencies(api)
        backup.extend([dep[1].encode(sys.getfilesystemencoding()) for dep in deps])
        # include compiler
        jalv2 = jalutil.GetJaluinoPrefs().get("JALLIB_JALV2")
        if jalv2:
            backup.append(jalv2.encode(sys.getfilesystemencoding()))

        [util.Log(u"[jaluino][warn] Include '%s' in backup" % os.path.basename(f)) for f in backup]
        zipstr = ZIPDumper(backup)

        zipfn = os.path.basename(jalfile).replace(".jal",".zip")
        # partially from ed_main.OnSaveAs()
        nb = self.GetMainWindow().GetNotebook()
        ctrl = nb.GetCurrentCtrl()
        dlg = wx.FileDialog(self, _("Choose a Save Location"),
                            os.path.dirname(jalfile),
                            zipfn,
                            u''.join(syntax.GenFileFilters()),
                            wx.SAVE | wx.OVERWRITE_PROMPT)

        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            fname = os.path.basename(path)
            dlg.Destroy()
            try:
                fout = file(path,"wb")
                fout.write(zipstr)
                fout.close()
                self.GetMainWindow().PushStatusText(_("Saved File As: %s") % fname, ed_glob.SB_INFO)
            except Exception,e:
                ed_mdlg.SaveErrorDlg(self,fname,e)
                self.GetMainWindow().PushStatusText(_("ERROR: Failed to save %s") % fname, ed_glob.SB_INFO)
        else:
            dlg.Destroy()
        
        
    def OnSettings(self):
        app = wx.GetApp()
        win = app.GetWindowInstance(cfgdlg.ConfigDialog)
        if win is None:
            config = cfgdlg.ConfigDialog(self._mw)
            config.CentreOnParent()
            config.Show()
        else:
            win.Raise()



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
                util.Log(u"[jaluino][err] %s" % excstr)
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
        if not isinstance(cmd,pytypes.UnicodeType):
            cmd = u' '.join(cmd)
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

    def Clear(self):
        super(OutputDisplay,self).Clear()

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


def ZIPDumper(filelist):
    buff = StringIO.StringIO()
    zip = zipfile.ZipFile(buff,"w")
    for f in filelist:
        zip.write(f,os.path.basename(f))
    zip.close()
    buff.seek(0)
    return buff.read()


def GetCompileMenu(mainw,menu):
    compile = wx.MenuItem(menu,ID_COMPILE_LAUNCH,_("Compile") + EdMenuBar.keybinder.GetBinding(ID_COMPILE_LAUNCH))
    bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_BIN_FILE), wx.ART_MENU)
    if not bmp.IsNull():
        compile.SetBitmap(bmp)
    mainw.AddMenuHandler(ID_COMPILE_LAUNCH, OnCompile)
    return compile

def GetUploadMenu(mainw,menu):
    upload = wx.MenuItem(menu,ID_UPLOAD_LAUNCH, _("Upload") + EdMenuBar.keybinder.GetBinding(ID_UPLOAD_LAUNCH))
    bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_UP), wx.ART_MENU)
    if not bmp.IsNull():
        upload.SetBitmap(bmp)
    mainw.AddMenuHandler(ID_UPLOAD_LAUNCH, OnUpload)
    return upload

def GetValidateMenu(mainw,menu):
    validate = wx.MenuItem(menu,ID_JSG_VALIDATE, _("Validate") + EdMenuBar.keybinder.GetBinding(ID_JSG_VALIDATE))
    bmp = wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_MENU)
    if not bmp.IsNull():
        validate.SetBitmap(bmp)
    mainw.AddMenuHandler(ID_JSG_VALIDATE, OnValidate)
    return validate

def GetOpenDepsMenu(mainw,menu):
    opendeps = wx.MenuItem(menu,ID_OPEN_DEPS, _("Open dependencies") + EdMenuBar.keybinder.GetBinding(ID_OPEN_DEPS))
    bmp = wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_MENU)
    if not bmp.IsNull():
        opendeps.SetBitmap(bmp)
    mainw.AddMenuHandler(ID_OPEN_DEPS, OnOpenDependencies)
    return opendeps

def GetCloseDepsMenu(mainw,menu):
    closedeps = wx.MenuItem(menu,ID_CLOSE_DEPS, _("Close dependencies") + EdMenuBar.keybinder.GetBinding(ID_CLOSE_DEPS))
    bmp = wx.ArtProvider.GetBitmap(wx.ART_DEL_BOOKMARK, wx.ART_MENU)
    if not bmp.IsNull():
        closedeps.SetBitmap(bmp)
    mainw.AddMenuHandler(ID_CLOSE_DEPS, OnCloseDependencies)
    return closedeps

def GetBackupMenu(mainw,menu):
    backup = wx.MenuItem(menu,ID_BACKUP, _("Backup project") + EdMenuBar.keybinder.GetBinding(ID_BACKUP))
    bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_HARDDISK), wx.ART_MENU)
    if not bmp.IsNull():
        backup.SetBitmap(bmp)
    mainw.AddMenuHandler(ID_BACKUP, OnBackup)
    return backup

def GetSettingsMenu(mainw,menu):
    pref = wx.MenuItem(menu,ID_SETTINGS, _("Settings") + EdMenuBar.keybinder.GetBinding(ID_SETTINGS))
    bmp = wx.ArtProvider.GetBitmap(str(ed_glob.ID_PREF), wx.ART_MENU)
    if not bmp.IsNull():
        pref.SetBitmap(bmp)
    mainw.AddMenuHandler(ID_SETTINGS, OnSettings)
    return pref

def BuildFileRelatedMenu(mainw,menu):
    menu.AppendItem(GetCompileMenu(mainw,menu))
    menu.AppendItem(GetUploadMenu(mainw,menu))
    if HAS_JALLIB:
        menu.AppendSeparator()
        menu.AppendItem(GetValidateMenu(mainw,menu))
        menu.AppendSeparator()
        menu.AppendItem(GetOpenDepsMenu(mainw,menu))
        menu.AppendItem(GetCloseDepsMenu(mainw,menu))
        menu.AppendSeparator()
        menu.AppendItem(GetBackupMenu(mainw,menu))


def GetMenu(mainw):
    menu = EdMenu()
    BuildFileRelatedMenu(mainw,menu)
    menu.AppendSeparator()
    menu.AppendItem(GetSettingsMenu(mainw,menu))
    return menu

def EnableJaluinoMenu(mainw,enable=True):
    # Enable Jaluino menu content
    bar = mainw.GetMenuBar()
    ml = [menu for menu,label in bar.GetMenus() if label == _("Jaluino")]
    if ml:
        menu = ml[0]
        [menu.Enable(m.GetId(),enable) for m in menu.GetMenuItems()]
    else:
        util.Log("[jaluino][warn] Unable to find Jaluino menu, can't %s it" % enable and "enable" or "disable")

def OnCompile(evt):
    """Handle the Run Script menu event and dispatch it to the currently
    active Jaluino panel

    """
    ed_msg.PostMessage(MSG_COMPILE)

def OnUpload(evt):
    """Handle the Run Last Script menu event and dispatch it to the currently
    active Launch panel

    """
    ed_msg.PostMessage(MSG_UPLOAD)

def OnValidate(evt):
    ed_msg.PostMessage(MSG_VALIDATE)

def OnOpenDependencies(evt):
    ed_msg.PostMessage(MSG_OPEN_DEPS)

def OnCloseDependencies(evt):
    ed_msg.PostMessage(MSG_CLOSE_DEPS)

def OnBackup(evt):
    ed_msg.PostMessage(MSG_BACKUP)

def OnSettings(evt):
    ed_msg.PostMessage(MSG_SETTINGS)

