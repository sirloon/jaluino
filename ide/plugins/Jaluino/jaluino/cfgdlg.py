# -*- coding: utf-8 -*-
###############################################################################
# Name: cfgdlg.py                                                             #
# Purpose: Configuration Dialog                                               #
# Author: Cody Precord <cprecord@editra.org>                                  #
# Adapted by: Sebastien Lelong <sebastien.lelong@gmail.com>
# Copyright: (c) 2008 Cody Precord <staff@editra.org>                         #
# License: wxWindows License                                                  #
###############################################################################

"""Jaluino Configuration Dialog"""

#-----------------------------------------------------------------------------#
# Imports
import sys, os
import subprocess
import cPickle
import wx
import wx.lib.filebrowsebutton
import wx.lib.mixins.listctrl as listmix
import cStringIO
import zlib


# Editra Libraries
import eclib
import util
import ed_glob
import ed_msg
from profiler import Profile_Get, Profile_Set


# placeholder for import
handlers = None

#-----------------------------------------------------------------------------#
# Globals

# Profile Key
JALUINO_PREFS = 'Jaluino.Prefs'

# General Panel
ID_LANGUAGE = wx.NewId()
ID_EXECUTABLES = wx.NewId()

# Serial/USB Panel
ID_AVAIL_PORTS_CHOICE = wx.NewId()
ID_AVAIL_PORTS = wx.NewId()
ID_CUSTOM_PORT_CHOICE = wx.NewId()
ID_CUSTOM_PORT = wx.NewId()
ID_AVAIL_SPEEDS_CHOICE = wx.NewId()
ID_AVAIL_SPEEDS = wx.NewId()
ID_CUSTOM_SPEED_CHOICE = wx.NewId()
ID_CUSTOM_SPEED = wx.NewId()

# Misc Panel
ID_AUTOCLEAR = wx.NewId()
ID_ERROR_BEEP = wx.NewId()
ID_GENERATE_API = wx.NewId()
ID_CHOOSE_TPL = wx.NewId()
ID_TPL_OVERWRITE = wx.NewId()

# Environment panel
ID_JALUINO_ROOT = wx.NewId()
ID_JALLIB_REPOS = wx.NewId()
ID_JALLIB_JALV2 = wx.NewId()
ID_JALUINO_BIN = wx.NewId()
ID_JALLIB_PYPATH = wx.NewId()
ID_PYTHON_EXEC = wx.NewId()
ID_JALUINO_LAUNCH_FILE = wx.NewId()

# Color Buttons
ID_DEF_BACK = wx.NewId()
ID_DEF_FORE = wx.NewId()
ID_INFO_BACK = wx.NewId()
ID_INFO_FORE = wx.NewId()
ID_ERR_BACK = wx.NewId()
ID_ERR_FORE = wx.NewId()
ID_WARN_BACK = wx.NewId()
ID_WARN_FORE = wx.NewId()

COLOR_MAP = { ID_DEF_BACK : 'defaultb', ID_DEF_FORE : 'defaultf',
              ID_ERR_BACK : 'errorb',   ID_ERR_FORE : 'errorf',
              ID_INFO_BACK : 'infob',   ID_INFO_FORE : 'infof',
              ID_WARN_BACK : 'warnb',   ID_WARN_FORE : 'warnf'}

# Message Types
EDMSG_JALUINO_CFG_EXIT = ed_msg.EDMSG_ALL + ('jaluino', 'cfg', 'exit')


_ = wx.GetTranslation
#-----------------------------------------------------------------------------#

def GetMinusData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2< \xcc\xc1\x06$\
\xc3Jc\x9e\x03)\x96b'\xcf\x10\x0e \xa8\xe1H\xe9\x00\xf2\x9d<]\x1cC4&&\xa7\
\xa4$\xa5)\xb0\x1aL\\RU\x90\x95\xe0\xf8,\xc6\xaa\xf0\xcf\xffr\x13\xd69\x87\
\xb8x\xaaVM\xea\x890\xf512N\x9e\xb1v\xf5\xe9\x05\xdc\xc2;jf:\x96\xdf\xd2\x14\
a\x96pO\xda\xc0\xc4\xa0\xf4\x8a\xab\xcau\xe2|\x1d\xa0i\x0c\x9e\xae~.\xeb\x9c\
\x12\x9a\x00Ij($" )

def GetMinusBitmap():
    stream = cStringIO.StringIO(GetMinusData())
    return wx.BitmapFromImage(wx.ImageFromStream(stream))

#----------------------------------------------------------------------
def GetPlusData():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2< \xcc\xc1\x06$\
\xc3Jc\x9e\x03)\x96b'\xcf\x10\x0e \xa8\xe1H\xe9\x00\xf2{<]\x1cC4&&'Hp\x1c\
\xd8\xb9\xcf\xe6U\xfd\xefi\xbb\xffo\xf44J\x14L\xae\xde\x97+yx\xd3\xe9\xfc\
\x8d\xb3\xda|\x99\x99g\x1b07\x1b\xd8k\x87\xf1\xea\x18\x1c{\xaa\xec\xfe\xaf>%\
!\xf9A\xda\xef\x03\x06\xf67{\x1f\x1e\xf8\xf9\x98g\xf9\xb9\xf9\xbf\xfe\xbf~\
\xad\xcf\x96'h\xca\xe6\xcck\xe8&2\xb7\x8e\x87\xe7\xbfdAB\xfb\xbf\xe0\x88\xbf\
\xcc\xcc\x7f.\xcbH\xfc{\xfd(\xa0\xe5*\xff\xfd\xff\x06\x06\x1f\xfe\xffh\xbaj\
\xf2f^ZB\xc2\x83\xe4\xc3\xef2o13<r\xd5y\xc0\xb9\xc2\xfa\x0e\xd0]\x0c\x9e\xae\
~.\xeb\x9c\x12\x9a\x00\xcf9S\xc6" )

def GetPlusBitmap():
    stream = cStringIO.StringIO(GetPlusData())
    return wx.BitmapFromImage(wx.ImageFromStream(stream))

#----------------------------------------------------------------------

class ConfigDialog(wx.Frame):
    """Configuration dialog for configuring what executables are available
    for a filetype and what the preferred one is.

    """
    def __init__(self, parent, ftype=0):
        """Create the ConfigDialog
        @param parent: The parent window
        @keyword: The filetype to set

        """
        # Depends on Launch
        import launch.handlers as handlersmod
        global handlers
        handlers = handlersmod

        wx.Frame.__init__(self, parent, title=_("Jaluino Configuration"))

        # Layout
        util.SetWindowIcon(self)
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        # Register with app
        wx.GetApp().RegisterWindow(repr(self), self)

    def __DoLayout(self):
        """Layout the dialog"""
        sizer = wx.BoxSizer(wx.VERTICAL)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        panel = wx.Panel(self)
        noteb = ConfigNotebook(panel)
        hsizer.AddMany([((5, 5), 0), (noteb, 1, wx.EXPAND), ((5, 5), 0)])
        vsizer.AddMany([((5, 5), 0), (hsizer, 1, wx.EXPAND), ((10, 10), 0)])
        panel.SetSizer(vsizer)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.SetInitialSize()
        self.SetMinSize((550, 345))

    def OnClose(self, evt):
        """Unregister the window when its closed"""
        wx.GetApp().UnRegisterWindow(repr(self))
        evt.Skip()

#-----------------------------------------------------------------------------#

class ConfigNotebook(wx.Notebook):
    """Notebook for holding config pages"""
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent)

        # Make sure config has been initialized
        prefs = Profile_Get(JALUINO_PREFS, default=None)
        if prefs is None:
            buff = eclib.OutputBuffer(self)
            buff.Hide()
            Profile_Set(JALUINO_PREFS,
                        dict(autoclear=False,
                             errorbeep=False,
                             defaultf=buff.GetDefaultForeground().Get(),
                             defaultb=buff.GetDefaultBackground().Get(),
                             errorf=buff.GetErrorForeground().Get(),
                             errorb=buff.GetErrorBackground().Get(),
                             infof=buff.GetInfoForeground().Get(),
                             infob=buff.GetInfoBackground().Get(),
                             warnf=buff.GetWarningForeground().Get(),
                             warnb=buff.GetWarningBackground().Get(),
                             jaltpl=None,
                             jaltplow=None,
                        ))
            buff.Destroy()

        # Setup
        self.AddPage(ConfigPanel(self), _("General"))
        self.AddPage(SerialUSBPanel(self), _("Serial/USB"))
        self.AddPage(EnvironmentPanel(self), _("Environment"))
        self.AddPage(MiscPanel(self), _("Misc"))

    def __del__(self):
        ed_msg.PostMessage(EDMSG_JALUINO_CFG_EXIT)

#-----------------------------------------------------------------------------#

class ConfigPanel(wx.Panel):
    """Configuration panel that holds the controls for configuration"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Depends on Launch
        import launch.handlers as handlersmod
        global handlers
        handlers = handlersmod

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(wx.EVT_CHOICE, self.OnChoice)
        self.Bind(wx.EVT_LIST_END_LABEL_EDIT, self.OnEndEdit)

    def __DoLayout(self):
        """Layout the controls"""
        msizer = wx.BoxSizer(wx.VERTICAL)

        lsizer = wx.BoxSizer(wx.HORIZONTAL)
        ftype = wx.GetApp().GetCurrentBuffer().GetLangId()
        ftype = handlers.GetHandlerById(ftype).GetName()
        htypes = GetHandlerTypes()
        lang_ch = wx.Choice(self, ID_LANGUAGE, choices=htypes)
        if ftype != handlers.DEFAULT_HANDLER:
            lang_ch.SetStringSelection(ftype)
        else:
            lang_ch.SetStringSelection(htypes[0])

        lsizer.AddMany([(wx.StaticText(self, label=_("File Type") + ":"), 0,
                         wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                        (lang_ch, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)])

        # Main area
        sbox = wx.StaticBox(self, label=_("Executables"))
        boxsz = wx.StaticBoxSizer(sbox, wx.VERTICAL)

        # Default exe
        dsizer = wx.BoxSizer(wx.HORIZONTAL)
        chandler = handlers.GetHandlerByName(lang_ch.GetStringSelection())
        cmds = chandler.GetAliases()
        def_ch = wx.Choice(self, wx.ID_DEFAULT, choices=cmds)
        if chandler.GetName() != handlers.DEFAULT_HANDLER:
            def_ch.SetStringSelection(chandler.GetDefault())
        elif len(cmds):
            def_ch.SetStringSelection(cmds[0])
        else:
            pass

        dsizer.AddMany([(wx.StaticText(self, label=_("Default") + ":"), 0,
                         wx.ALIGN_CENTER_VERTICAL), ((5, 5), 0),
                        (def_ch, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL)])

        # Executables List
        exelist = CommandListCtrl(self, ID_EXECUTABLES,
                                  style=wx.LC_EDIT_LABELS|\
                                        wx.BORDER|wx.LC_REPORT|\
                                        wx.LC_SINGLE_SEL)
#        exelist.SetToolTipString(_("Click on an item to edit"))
#        exelist.InsertColumn(0, _("Alias"))
#        exelist.InsertColumn(1, _("Executable Commands"))
        self.SetListItems(chandler.GetCommands())
        addbtn = wx.BitmapButton(self, wx.ID_ADD, GetPlusBitmap())
        addbtn.SetToolTipString(_("Add a new executable"))
        delbtn = wx.BitmapButton(self, wx.ID_REMOVE, GetMinusBitmap())
        delbtn.SetToolTipString(_("Remove selection from list"))
        btnsz = wx.BoxSizer(wx.HORIZONTAL)
        btnsz.AddMany([(addbtn, 0), ((2, 2), 0), (delbtn, 0)])

        # Box Sizer Layout
        boxsz.AddMany([((5, 5), 0), (dsizer, 0, wx.ALIGN_CENTER|wx.EXPAND),
                       ((5, 5), 0), (wx.StaticLine(self), 0, wx.EXPAND),
                       ((8, 8), 0), (exelist, 1, wx.EXPAND), ((5, 5), 0),
                       (btnsz, 0, wx.ALIGN_LEFT)])

        # Setup the main sizer
        msizer.AddMany([((10, 10), 0), (lsizer, 0, wx.EXPAND),
                        ((10, 10), 0), (wx.StaticLine(self), 0, wx.EXPAND),
                        ((10, 10), 0),
                        (boxsz, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL),
                        ((10, 10), 0)])

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([((8, 8), 0), (msizer, 1, wx.EXPAND), ((8, 8), 0)])
        self.SetSizer(hsizer)
        self.SetAutoLayout(True)

    def __DoUpdateHandler(self, handler):
        exes = self.GetListItems()
        handler.SetCommands(exes)
        def_ch = self.FindWindowById(wx.ID_DEFAULT)
        def_ch.SetItems(handler.GetAliases())
        def_ch.SetStringSelection(handler.GetDefault())

    def GetCurrentHandler(self):
        """Get the currently selected file type handler
        @return: handlers.FileTypeHandler

        """
        ftype = self.FindWindowById(ID_LANGUAGE).GetStringSelection()
        return handlers.GetHandlerByName(ftype)

    def GetListItems(self):
        """Get all the values from the list control
        return: tuple (alias, cmd)

        """
        item_id = -1
        exes = list()
        elist = self.FindWindowById(ID_EXECUTABLES)
        for item in xrange(elist.GetItemCount()):
            item_id = elist.GetNextItem(item_id)
            if item_id == -1:
                break
            val = (elist.GetItem(item_id, 0).GetText(),
                   elist.GetItem(item_id, 1).GetText())
            exes.append(val)
        return exes

    def OnButton(self, evt):
        """Handle the add and remove button events
        @param evt: wxButtonEvent

        """
        e_id = evt.GetId()
        elist = self.FindWindowById(ID_EXECUTABLES)
        if e_id == wx.ID_ADD:
            elist.Append([_("**Alias**"), _("**New Value**")])
        elif e_id == wx.ID_REMOVE:
            item = -1
            items = []
            while True:
                item = elist.GetNextItem(item, wx.LIST_NEXT_ALL,
                                         wx.LIST_STATE_SELECTED)
                if item == -1:
                    break
                items.append(item)

            for item in reversed(sorted(items)):
                elist.DeleteItem(item)

            wx.CallAfter(self.__DoUpdateHandler, self.GetCurrentHandler())

        else:
            evt.Skip()

    def OnChoice(self, evt):
        """Handle the choice selection events"""
        e_id = evt.GetId()
        e_obj = evt.GetEventObject()
        e_val = e_obj.GetStringSelection()
        if e_id == ID_LANGUAGE:
            handler = handlers.GetHandlerByName(e_val)
            elist = self.FindWindowById(ID_EXECUTABLES)
            elist.DeleteAllItems()
            def_ch = self.FindWindowById(wx.ID_DEFAULT)
            def_ch.SetItems(handler.GetAliases())
            def_ch.SetStringSelection(handler.GetDefault())
            self.SetListItems(handler.GetCommands())
        elif e_id == wx.ID_DEFAULT:
            handler = self.GetCurrentHandler()
            handler.SetDefault((e_val, handler.GetCommand(e_val)))
        else:
            evt.Skip()

    def OnEndEdit(self, evt):
        """Store the new list values after the editing of a
        label has finished.
        @param evt: wxEVT_LIST_END_LABEL_EDIT
        @note: values in list are set until after this handler has finished

        """
        handler = self.GetCurrentHandler()
        if handler.GetName() != handlers.DEFAULT_HANDLER:
            exes = self.GetListItems()
            idx = evt.GetIndex()
            col = evt.GetColumn()
            nval = evt.GetLabel()
            if len(exes) >= idx:
                # Update an existing item
                if col == 0:
                    exes[idx] = (nval, exes[idx][1])
                else:
                    exes[idx] = (exes[idx][0], nval)
            else:
                # Add a new item
                # This should not happen
                if col == 0:
                    exes.append((nval, nval))
                else:
                    exes.append((nval, nval))

            # Store the new values
            handler.SetCommands(exes)
            def_ch = self.FindWindowById(wx.ID_DEFAULT)
            def_ch.SetItems(handler.GetAliases())
            def_ch.SetStringSelection(handler.GetDefault())

    def SetListItems(self, items):
        """Set the items that are in the list control
        @param items: list of tuples (alias, cmd)

        """
        elist = self.FindWindowById(ID_EXECUTABLES)
        for exe in items:
            elist.Append(exe)

#-----------------------------------------------------------------------------#

class MiscPanel(wx.Panel):
    """Misc settings panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # Attributes
        self.tpl = None     # template chooser
        self.tplow = None   # overwrite existing templates

        # Layout
        self.__DoLayout()

        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_BUTTON, self.OnButton)
        self.Bind(eclib.EVT_COLORSETTER, self.OnColor)

    def __DoLayout(self):
        """Layout the controls"""
        msizer = wx.BoxSizer(wx.VERTICAL)
        actbox = wx.StaticBox(self, label=_("Actions"))
        actboxsz = wx.StaticBoxSizer(actbox, wx.VERTICAL)
        libbox = wx.StaticBox(self, label=_("Autocompletion"))
        libboxsz = wx.StaticBoxSizer(libbox, wx.VERTICAL)
        tplbox = wx.StaticBox(self, label=_("Jalv2 templates"))
        tplboxsz = wx.StaticBoxSizer(tplbox, wx.VERTICAL)
        sbox = wx.StaticBox(self, label=_("Text Colors"))
        boxsz = wx.StaticBoxSizer(sbox, wx.VERTICAL)

        # Jaluino Config
        cfg = Profile_Get(JALUINO_PREFS, default=dict())

        # Actions Configuration
        clear_cb = wx.CheckBox(self, ID_AUTOCLEAR,
                               _("Automatically clear buffer between runs"))
        clear_cb.SetValue(cfg.get('autoclear', False))
        error_cb = wx.CheckBox(self, ID_ERROR_BEEP,
                               _("Audible feedback when errors are detected"))
        error_cb.SetValue(cfg.get('errorbeep', False))
        gen_api_btn = wx.Button(self,ID_GENERATE_API,_("Re-discover JAL libraries"))

        # Colors
        colors = dict()
        for btn in COLOR_MAP.iteritems():
            cbtn = eclib.ColorSetter(self, btn[0], color=cfg.get(btn[1]))
            colors[btn[0]] = cbtn

        flexg = wx.FlexGridSizer(5, 5, 5, 5)
        flexg.AddGrowableCol(1, 1)
        flexg.AddGrowableCol(3, 1)
        flexg.AddMany([# First Row
                       ((5, 5), 0), ((5, 5), 1),
                       (wx.StaticText(self, label=_("Foreground")), 0,
                        wx.ALIGN_CENTER),
                       ((5, 5), 1),
                       (wx.StaticText(self, label=_("Background")), 0,
                        wx.ALIGN_CENTER),
                       # Second Row
                       (wx.StaticText(self, label=_("Plain Text") + u":"), 0,
                        wx.ALIGN_CENTER_VERTICAL),
                       ((5, 5), 1),
                       (colors[ID_DEF_FORE], 0, wx.EXPAND),
                       ((5, 5), 1),
                       (colors[ID_DEF_BACK], 0, wx.EXPAND),
                       # Third Row
                       (wx.StaticText(self, label=_("Error Text") + u":"), 0,
                        wx.ALIGN_CENTER_VERTICAL),
                       ((5, 5), 1),
                       (colors[ID_ERR_FORE], 0, wx.EXPAND),
                       ((5, 5), 1),
                       (colors[ID_ERR_BACK], 0, wx.EXPAND),
                       # Fourth Row
                       (wx.StaticText(self, label=_("Info Text") + u":"), 0,
                        wx.ALIGN_CENTER_VERTICAL),
                       ((5, 5), 1),
                       (colors[ID_INFO_FORE], 0, wx.EXPAND),
                       ((5, 5), 1),
                       (colors[ID_INFO_BACK], 0, wx.EXPAND),
                       # Fifth Row
                       (wx.StaticText(self, label=_("Warning Text") + u":"), 0,
                        wx.ALIGN_CENTER_VERTICAL),
                       ((5, 5), 1),
                       (colors[ID_WARN_FORE], 0, wx.EXPAND),
                       ((5, 5), 1),
                       (colors[ID_WARN_BACK], 0, wx.EXPAND)])
        boxsz.Add(flexg, 0, wx.EXPAND)

        
        libboxsz.AddMany([(wx.StaticText(self, label=_("Re-discover JAL libraries in order to rebuild autocompletion cache")), 0,wx.ALIGN_CENTER_VERTICAL|wx.EXPAND),
                          (gen_api_btn, 0,wx.EXPAND)])

        actboxsz.AddMany([((5, 5), 0), (clear_cb, 0),
                          ((5, 5), 0), (error_cb, 0)])

        topBox = wx.BoxSizer(wx.HORIZONTAL)
        default_tpl = os.path.join(ed_glob.CONFIG['CACHE_DIR'],"snippets.py")
        self.tpl = wx.lib.filebrowsebutton.FileBrowseButton(self,ID_CHOOSE_TPL,labelText="File containing templates",
                                                      initialValue=cfg.get("jaltpl") or default_tpl,
                                                      changeCallback=self.OnTemplateSelected)
        topBox.Add(self.tpl,1,wx.EXPAND)
        self.tpltxt = wx.StaticText(self, label="")
        self.tpltxt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        self.tplow = wx.CheckBox(self, ID_TPL_OVERWRITE,
                               _("Overwrite existing templates if named the same"))
        self.tplow.SetValue(cfg.get('jaltplow', False))
        tplboxsz.AddMany([(topBox, 1,wx.EXPAND),(self.tplow,1,wx.EXPAND),((5,5),0),(self.tpltxt,0)])
        # check if codetemplater, on which jalv2 template is based, is installed
        # and enabled. If so, load templates to give feedback to users and make
        # sure template file is safe
        try:
            import codetemplater
            pm = wx.GetApp().GetPluginManager()
            ct = pm[codetemplater.CodeTemplater]
            if not ct:
                self.tpltxt.SetForegroundColour(wx.RED)
                self.tpltxt.SetLabel(_("CodeTemplater plugin is installed but not enabled. Please enable it from 'Plugin Manager' menu"))
            else:
                if self.tpl.GetValue():
                    self.LoadTemplates()
        except ImportError:
            self.tpltxt.SetForegroundColour(wx.RED)
            self.tpltxt.SetLabel(_("CodeTemplater plugin doesn't seem to be installed, templates can't be loaded without it"))

        # Layout
        msizer.AddMany([((5, 5), 0),
                        (actboxsz,0,wx.EXPAND),
                        (libboxsz,0,wx.EXPAND),
                        (tplboxsz,0,wx.EXPAND),
                        ((10, 10), 0),
                        (boxsz, 1, wx.EXPAND)])

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([((5, 5), 0), (msizer, 1, wx.EXPAND), ((5, 5), 0)])
        self.SetSizer(hsizer)

    def LoadTemplates(self):
        try:
            import codetemplater
            pm = wx.GetApp().GetPluginManager()
            ct = pm[codetemplater.CodeTemplater]
            assert ct != None, "CodeTemplater plugin should be defined"
            import jalutil
            tpls = jalutil.MergeCodeTemplates(file(self.tpl.GetValue()),overwrite=self.tplow.GetValue())
            ct.templates = tpls
            self.tpltxt.SetForegroundColour(wx.BLACK)
            self.tpltxt.SetLabel("Template(s) loaded")
        except Exception,e:
            self.tpltxt.SetForegroundColour(wx.RED)
            self.tpltxt.SetLabel((_("Error while loading templates: ") + str(e)))

    def OnCheck(self, evt):
        """Handle checkbox events"""
        e_id = evt.GetId()
        e_val = evt.GetEventObject().GetValue()
        cfg = Profile_Get(JALUINO_PREFS, default=dict())
        if e_id == ID_AUTOCLEAR:
            cfg['autoclear'] = e_val
        elif e_id == ID_ERROR_BEEP:
            cfg['errorbeep'] = e_val
        elif e_id == ID_TPL_OVERWRITE:
            cfg['jaltplow'] = e_val
        else:
            evt.Skip()

    def OnColor(self, evt):
        """Handle color change events"""
        e_id = evt.GetId()
        color = COLOR_MAP.get(e_id, None)
        if color is not None:
            Profile_Get(JALUINO_PREFS)[color] = evt.GetValue().Get()
        else:
            evt.Skip()

    def OnButton(self, evt):
        # import here, as jalcomp imports cfgldg imports jalcomp...
        # baaah...
        import jalcomp
        incapi = jalcomp.GetIncludeAPIFile()
        try:
            os.unlink(incapi)
        except OSError,e:
            util.Log("[jaluino][warn] Unable to delete file '%s': %s" % (incapi,e))

        mb = wx.MessageBox(_("You need to restart editor in order discover all JAL libraries"),
                           _("Restart needed"))
        
    def OnTemplateSelected(self,evt):
        jaltpl = self.tpl.GetValue()
        # save selected template file in profile
        cfg = Profile_Get(JALUINO_PREFS, default=dict())
        cfg['jaltpl'] = jaltpl
        import jalutil
        util.Log("[jaluino][info] Merging templates from file '%s'" % jaltpl)
        self.LoadTemplates()


#-----------------------------------------------------------------------------#

class SerialUSBPanel(wx.Panel):
    """Serial settings panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # Layout
        self.__DoLayout()
        # Event Handlers
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.Bind(wx.EVT_COMBOBOX, self.OnCombo)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnRadio)
        self.Bind(wx.EVT_TEXT, self.OnText)
        self.Bind(eclib.EVT_COLORSETTER, self.OnColor)

    def GetAvailablePorts(self):
        # Actions Configuration
        import serial
        serports = {}
        for i in range(20): # more than 20 serial ports ? C'mon...
            try:
                s = serial.Serial(i)
                serports[s.portstr] = s.port
            except serial.SerialException:
                continue
        return serports

    def GetAvailableBaudrates(self):    
        # can we detect this ?
        bds = [110,300,600,1200,2400,4800,9600,14400,19200,38400,
               56000,57600,115200,128000,256000]
        return bds

    def __DoLayout(self):
        """Layout the controls"""

        ##usbbox = wx.StaticBox(self, label=_("USB Configuration"))
        ##usbboxsz = wx.StaticBoxSizer(usbbox, wx.VERTICAL)
        cfg = Profile_Get(JALUINO_PREFS, default=dict())

        msizer = wx.BoxSizer(wx.VERTICAL)

        # Serial port configuration
        try:
            import serial

            serialportbox = wx.StaticBox(self, label=_("Serial Port"))
            serialportboxsz = wx.StaticBoxSizer(serialportbox, wx.VERTICAL)
            txt = wx.StaticText(self, label=_("Select an available serial port or, if not detected,\nenter your own serial port:"),style=wx.ALIGN_LEFT)
            txt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
            serialportboxsz.Add(txt)
            serports = self.GetAvailablePorts()
            portbox = wx.ComboBox(self,ID_AVAIL_PORTS,_("Choose a port"),
                                  (0, 0), (150, -1),choices=sorted(serports.keys()))
            cfg.get("serial.port.available") and portbox.SetValue(cfg["serial.port.available"])
            avail_ports = wx.RadioButton(self,ID_AVAIL_PORTS_CHOICE,style=wx.RB_GROUP)
            # defaulting for radios is tricky, as event (thus config storage) is only triggered
            # when first radio is 
            availsizer = wx.BoxSizer(wx.HORIZONTAL)
            availsizer.Add(avail_ports)
            availsizer.Add(portbox)
            serialportboxsz.Add(availsizer)
            custsizer = wx.BoxSizer(wx.HORIZONTAL)
            custom_port = wx.RadioButton(self,ID_CUSTOM_PORT_CHOICE)
            custom = wx.TextCtrl(self, ID_CUSTOM_PORT,u"",(0,0),(200,-1))
            if cfg.get('serial.port.custom'):
                custom.SetValue(cfg['serial.port.custom'])
            else:
                custom.SetValue(_("Enter your own port"))
            custsizer.Add(custom_port)
            custsizer.Add(custom)
            serialportboxsz.Add(custsizer)
            # restore config
            if cfg.get("serial.port.choice","available") == "available":
                avail_ports.SetValue(True)
                custom_port.SetValue(False)
            else:
                avail_ports.SetValue(False)
                custom_port.SetValue(True)

            # Serial baudrate configuration
            serialspeedbox = wx.StaticBox(self, label=_("Serial Speed"))
            serialspeedboxsz = wx.StaticBoxSizer(serialspeedbox, wx.VERTICAL)
            txt = wx.StaticText(self, label=_("Select an available serial baudrate (speed) or\nenter your own baudrate value:"),style=wx.ALIGN_LEFT)
            txt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
            serialspeedboxsz.Add(txt)
            serbds = self.GetAvailableBaudrates()
            speedbox = wx.ComboBox(self,ID_AVAIL_SPEEDS,_("Choose a baudrate"),
                                  (0, 0), (150, -1),choices=map(unicode,serbds))
            cfg.get('serial.baudrate.available') and speedbox.SetValue(cfg['serial.baudrate.available'])
            avail_speeds = wx.RadioButton(self,ID_AVAIL_SPEEDS_CHOICE,style=wx.RB_GROUP)
            availsizer = wx.BoxSizer(wx.HORIZONTAL)
            availsizer.Add(avail_speeds)
            availsizer.Add(speedbox)
            serialspeedboxsz.Add(availsizer)
            custsizer = wx.BoxSizer(wx.HORIZONTAL)
            custom_speed = wx.RadioButton(self,ID_CUSTOM_SPEED_CHOICE)
            custom = wx.TextCtrl(self, ID_CUSTOM_SPEED,u"",(0,0),(200,-1))
            if cfg.get('serial.baudrate.custom'):
                custom.SetValue(cfg['serial.baudrate.custom'])
            else:
                custom.SetValue(_("Enter your own baudrate"))
            custsizer.Add(custom_speed)
            custsizer.Add(custom)
            serialspeedboxsz.Add(custsizer)
            # restore config
            if cfg.get("serial.baudrate.choice","available") == "available":
                avail_speeds.SetValue(True)
                custom_speed.SetValue(False)
            else:
                avail_speeds.SetValue(False)
                custom_speed.SetValue(True)

            msizer.AddMany([(serialportboxsz, 1, wx.EXPAND),(serialspeedboxsz, 1, wx.EXPAND)])

        except ImportError,e:
            noserial = wx.StaticText(self,-1,_("Python serial module is not installed, you can download it from:\n\nhttp://pyserial.sourceforge.net\n\n"))
            noserial.SetForegroundColour(wx.RED)
            noserial2 = wx.StaticText(self,-1,_("Error was:\n%s\n\n" % e))
            # here we're guessing which Python version Editra is using. Should be sync'ed with install.py...
            pyver = ".".join(map(str,sys.version_info[:2]))
            noserial3 = wx.StaticText(self,-1,_("You need install pyserial for python %s" % pyver))
            msizer.Add(noserial)
            msizer.Add(noserial2)
            msizer.Add(noserial3)
            
            
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([(msizer, 1, wx.EXPAND)])
        self.SetSizer(hsizer)

    def OnCheck(self, evt):
        """Handle checkbox events"""
        e_id = evt.GetId()
        e_val = evt.GetEventObject().GetValue()
        cfg = Profile_Get(JALUINO_PREFS, default=dict())
        if e_id == ID_AUTOCLEAR:
            cfg['autoclear'] = e_val
        elif e_id == ID_ERROR_BEEP:
            cfg['errorbeep'] = e_val
        else:
            evt.Skip()

    def OnCombo(self, evt):
        e_id = evt.GetId()
        e_val = evt.GetEventObject().GetValue()
        cfg = Profile_Get(JALUINO_PREFS, default=dict())
        if e_id == ID_AVAIL_PORTS:
            cfg['serial.port.available'] = e_val
        elif e_id == ID_AVAIL_SPEEDS:
            cfg['serial.baudrate.available'] = e_val
        else:
            evt.Skip()

    def OnRadio(self, evt):
        e_id = evt.GetId()
        e_val = evt.GetEventObject().GetValue()
        cfg = Profile_Get(JALUINO_PREFS, default=dict())

        if e_id == ID_AVAIL_PORTS_CHOICE:
            cfg['serial.port.choice'] = "available"
        if e_id == ID_CUSTOM_PORT_CHOICE:
            cfg['serial.port.choice'] = "custom"

        elif e_id == ID_AVAIL_SPEEDS_CHOICE:
            cfg['serial.baudrate.choice'] = "available"
        elif e_id == ID_CUSTOM_SPEED_CHOICE:
            cfg['serial.baudrate.choice'] = "custom"

        else:
            evt.Skip()

    def OnText(self, evt):
        e_id = evt.GetId()
        e_val = evt.GetEventObject().GetValue()
        cfg = Profile_Get(JALUINO_PREFS, default=dict())
        if e_id == ID_CUSTOM_PORT:
            cfg['serial.port.custom'] = e_val
        elif e_id == ID_CUSTOM_SPEED:
            cfg['serial.baudrate.custom'] = e_val
        else:
            evt.Skip()

    def OnColor(self, evt):
        """Handle color change events"""
        e_id = evt.GetId()
        color = COLOR_MAP.get(e_id, None)
        if color is not None:
            Profile_Get(JALUINO_PREFS)[color] = evt.GetValue().Get()
        else:
            evt.Skip()


class EnvironmentPanel(wx.Panel):
    """Environment (lib, compiler paths, ...) panel"""
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.__DoLayout()

        self.Bind(wx.EVT_TEXT, self.OnText)

    def __DoLayout(self):
        import jalutil
        cfg = jalutil.GetJaluinoPrefs()

        msizer = wx.BoxSizer(wx.VERTICAL)

        sboxsz = wx.BoxSizer(wx.VERTICAL)

        msg = _("Installation directory (JALUINO_ROOT):")
        txt = wx.StaticText(self, label=msg,style=wx.ALIGN_LEFT)
        txt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        sboxsz.Add(txt)
        instdir = wx.TextCtrl(self, ID_JALUINO_ROOT,u"",(0,0),(450,-1))
        instdir.SetValue(cfg.get("JALUINO_ROOT",""))
        sboxsz.Add(instdir)

        msg = _("Jalv2 compiler executable (JALLIB_JALV2):")
        txt = wx.StaticText(self, label=msg,style=wx.ALIGN_LEFT)
        txt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        sboxsz.Add(txt)
        jalv2 = wx.TextCtrl(self, ID_JALLIB_JALV2,u"",(0,0),(450,-1))
        jalv2.SetValue(cfg.get("JALLIB_JALV2",""))
        sboxsz.Add(jalv2)

        msg = _("Specify where JAL libraries can be found, one directory per line.\nSub-directories are considered, recursively (JALLIB_REPOS)")
        txt = wx.StaticText(self, label=msg,style=wx.ALIGN_LEFT)
        txt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        sboxsz.Add(txt)
        libs = wx.TextCtrl(self, ID_JALLIB_REPOS,u"",style=wx.TE_MULTILINE)
        libs.SetValue("\n".join(cfg.get("JALLIB_REPOS","").split(os.pathsep)))
        sboxsz.Add(libs,1,wx.EXPAND)

        msg = _("Specify where jallib.py library can be found\nand other python libraries to include (JALLIB_PYPATH):")
        txt = wx.StaticText(self, label=msg,style=wx.ALIGN_LEFT)
        txt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        sboxsz.Add(txt)
        execs = wx.TextCtrl(self, ID_JALLIB_PYPATH,u"",style=wx.TE_MULTILINE,)
        execs.SetValue("\n".join(cfg.get("JALLIB_PYPATH","").split(os.pathsep)))
        sboxsz.Add(execs,1,wx.EXPAND)

        msg = _("Specify where executables (compiler wrappers, uploaders, etc...) can be found (JALUINO_BIN):")
        txt = wx.StaticText(self, label=msg,style=wx.ALIGN_LEFT)
        txt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        sboxsz.Add(txt)
        execs = wx.TextCtrl(self, ID_JALUINO_BIN,u"",(0,0),(450,-1))
        execs.SetValue("\n".join(cfg.get("JALUINO_BIN","").split(os.pathsep)))
        sboxsz.Add(execs)

        msg = _("Python executable (PYTHON_EXEC):")
        txt = wx.StaticText(self, label=msg,style=wx.ALIGN_LEFT)
        txt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        sboxsz.Add(txt)
        pyexec = wx.TextCtrl(self, ID_PYTHON_EXEC,u"",(0,0),(400,-1))
        pyexec.SetValue(cfg.get("PYTHON_EXEC",""))
        sboxsz.Add(pyexec)

        msg = _("XML filename containing Jaluino commands (JALUINO_LAUNCH_FILE):")
        txt = wx.StaticText(self, label=msg,style=wx.ALIGN_LEFT)
        txt.SetFont(wx.Font(8,wx.NORMAL,wx.NORMAL,wx.NORMAL))
        sboxsz.Add(txt)
        cmdfn = wx.TextCtrl(self, ID_JALUINO_LAUNCH_FILE,u"",(0,0),(200,-1))
        cmdfn.SetValue(cfg.get("JALUINO_LAUNCH_FILE",""))
        sboxsz.Add(cmdfn)

        # Layout
        msizer.AddMany([((5, 5), 0),
                        (sboxsz, 1, wx.EXPAND)])
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.AddMany([((5, 5), 0), (msizer, 1, wx.EXPAND), ((5, 5), 0)])
        self.SetSizer(hsizer)

    def OnText(self, evt):
        e_id = evt.GetId()
        e_val = evt.GetEventObject().GetValue()
        cfg = Profile_Get(JALUINO_PREFS, default=dict())
        if e_id == ID_JALUINO_ROOT:
            cfg['JALUINO_ROOT'] = e_val
        elif e_id == ID_JALLIB_JALV2:
            cfg['JALLIB_JALV2'] = e_val
        elif e_id == ID_JALLIB_REPOS:
            cfg['JALLIB_REPOS'] = os.pathsep.join(e_val.splitlines())
        elif e_id == ID_JALUINO_BIN:
            cfg['JALUINO_BIN'] = e_val
        elif e_id == ID_JALLIB_PYPATH:
            cfg['JALLIB_PYPATH'] = os.pathsep.join(e_val.splitlines())
        elif e_id == ID_PYTHON_EXEC:
            cfg['PYTHON_EXEC'] = e_val
        elif e_id == ID_JALUINO_LAUNCH_FILE:
            cfg['JALUINO_LAUNCH_FILE'] = e_val
        else:
            evt.Skip()


#-----------------------------------------------------------------------------#
ID_BROWSE = wx.NewId()

class CommandListCtrl(listmix.ListCtrlAutoWidthMixin,
                      listmix.TextEditMixin,
                      eclib.ListRowHighlighter,
#                      listmix.CheckListCtrlMixin,
                      wx.ListCtrl):
    """Auto-width adjusting list for showing editing the commands"""
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
#        listmix.CheckListCtrlMixin.__init__(self)
        eclib.ListRowHighlighter.__init__(self)

        # Attributes
        self._menu = None
        self._cindex = -1

        # Setup
        self.SetToolTipString(_("Click on an item to edit"))
#        pcol = _("Dir")
#        self.InsertColumn(0, pcol)
        self.InsertColumn(0, _("Alias"))
        self.InsertColumn(1, _("Executable Commands"))
#        self.SetColumnWidth(0, self.GetTextExtent(pcol)[0] + 5)

        listmix.TextEditMixin.__init__(self)

        # Event Handlers
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnContextClick)
        self.Bind(wx.EVT_MENU, self.OnMenu, id=ID_BROWSE)

    def OnContextClick(self, evt):
        """Handle right clicks"""
        if not self.GetSelectedItemCount():
            evt.Skip()
            return

        if self._menu is None:
            # Lazy init of menu
            self._menu = wx.Menu()
            self._menu.Append(ID_BROWSE, _("Browse"))

        self._cindex = evt.GetIndex()
        self.PopupMenu(self._menu)

    def OnMenu(self, evt):
        """Handle Menu events"""
        e_id = evt.GetId()
        if e_id == ID_BROWSE:
            dlg = wx.FileDialog(self, _("Choose and executable"))
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                if self._cindex >= 0:
                    self.SetStringItem(self._cindex, 1, path)
                    levt = wx.ListEvent(wx.wxEVT_COMMAND_LIST_END_LABEL_EDIT,
                                        self.GetId())
                    # HACK set the member variables directly...
                    levt.m_itemIndex = self._cindex
                    levt.m_col = 1
                    levt.SetString(path)
                    wx.PostEvent(self.GetParent(), levt)
        else:
            evt.Skip()


def GetHandlerTypes():
    jalh = handlers.GetHandlerByName("Jalv2")
    hexh = handlers.GetHandlerByName("Hex")
    rlist = list()
    for h in (jalh,hexh):
        rlist.append(h.GetName().title())
    return sorted(rlist)
