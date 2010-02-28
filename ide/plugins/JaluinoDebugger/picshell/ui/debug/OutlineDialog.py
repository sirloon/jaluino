from picshell.ui.Context import Context
import  wx
class OutlineDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title,uiManager, size=(400,200), pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):
        self.uiManager = None
        self.tab = None
        self.editor = None
        
        self.types = None
        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.search = wx.TextCtrl(self, -1, "")
        self.search.Bind(wx.EVT_KEY_UP, self.OnOutlineSearch)
        sizer.Add(self.search, 0, wx.EXPAND)
        self.list =  wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL)
        self.list.SetBackgroundColour("#ffffe1")
        self.list.InsertColumn(0, '')
        self.list.SetColumnWidth(0, 200)
        #self.list.InsertColumn(1, '')
        #self.list.SetColumnWidth(1, 50)
        
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnListSelected)
        self.list.Bind(wx.EVT_LEFT_DCLICK, self.OnListDCLICK)
        self.list.Bind(wx.EVT_KEY_DOWN, self.OnListKey)
        
        
        
        sizer.Add(self.list, -1, wx.EXPAND)
        
        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)
        btnsizer = wx.StdDialogButtonSizer()
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)
       
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()
        
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.SetSizer(sizer)
        self.uiManager = uiManager
        #sizer.Fit(self)
    def OnListSelected(self,event):
        item = self.list.GetItem(self.list.GetFirstSelected(),0)
        itemKey = item.GetText().strip()
        self.pos = self.items[itemKey]
        
    def OnListDCLICK(self,event):
        item = self.list.GetItem(self.list.GetFirstSelected(),0)
        itemKey = item.GetText().strip()
        self.pos = self.items[itemKey]

        if (self.editor != None) :
            self.editor.GotoLine(self.pos)
        elif self.tab == Context.TAB_DEBUG :    
            self.uiManager.listLang.SetFocus()
            self.uiManager.listLang.Focus(self.pos)
            self.uiManager.listLang.Select(self.pos,True)
            self.uiManager.listLang.EnsureVisible(self.pos)
        self.Close()
    
    def OnListKey(self,event):
        key = event.GetKeyCode()
        if key == 13 :
            self.OnListDCLICK(event)
        else :
            event.Skip();
        
        
                
        
    def setItems(self,items):
        self.items = items["items"]
        self.types = items["types"]
        i = 0
        for item in self.items.keys():
            self.list.InsertStringItem(i,item)
            if (self.types != None) and self.types.has_key(item):
                self.list.SetStringItem(i,1,  self.types[item]);
                #print str(i)+" "+item+" "+self.types[item]
            i += 1
            
    def OnOutlineSearch(self,event):
        key = event.GetKeyCode()

        if key == wx.WXK_DOWN:
            self.list.SetFocus()
            self.list.Select(0)
            self.list.Focus(0)
            self.list.EnsureVisible(0)
            self.OnListSelected(event)
            
        else:    
            what = self.search.GetValue() 
            self.updateOutline(what)
            if (self.list.GetItemCount()==1):
                self.list.Select(0, True)
                self.list.EnsureVisible(0)
                self.OnListSelected(event)

    def updateOutline(self,what):
        self.list.DeleteAllItems()
        if what.startswith("*"):
            i = 0
            for item in self.items.keys():
                if what[1:].upper() in item.upper() :
                   self.list.InsertStringItem(i,item)
                   if self.types != None and self.types.has_key(item):
                       self.list.SetStringItem(i,1,  self.types[item]);
                   i += 1
        else:
            i = 0
            for item in self.items.keys():
                if item.upper().startswith(what.upper()) :
                    self.list.InsertStringItem(i,item)
                    if self.types != None and self.types.has_key(item):
                        self.list.SetStringItem(i,1,  self.types[item]);
                    i += 1


        
