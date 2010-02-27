from picshell.parser.JalV2Parser import JalV2Parser
from picshell.ui.Context import Context
from picshell.ui.edit.EditorUtil import EditorUtil
from picshell.ui.edit.FindDialog import FindDialog
from picshell.util import DocHelper
from wx import stc
from wx.lib import ogl
from wx.stc import EVT_STC_DOUBLECLICK
from wx.stc import STC_EOL_CRLF
from wx._gdi import STANDARD_CURSOR
from wx._gdi import HOURGLASS_CURSOR

from wx.stc import EVT_STC_CHANGE
from wx.stc import EVT_STC_SAVEPOINTREACHED
from wx._core import WXK_F12
from wx._core import WXK_F4

import os
import re
import wx

import picshell.icons.embedded_icons

#
# Editor for jal text
#
class JalEditor(stc.StyledTextCtrl):
    def __init__(self, parent, ID,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.SP_NOBORDER):
        
        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)
        
        if wx.Platform == '__WXMSW__':
            faces = { 'times': 'Times New Roman',
                      'mono' : 'Courier New',
                      'helv' : 'Arial',
                      'other': 'Comic Sans MS',
                      'size' : Context.FONTSIZE,
                      'size2': 8,
                     }
        else:
            faces = { 'times': 'Times',
                      'mono' : 'Courier',
                      'helv' : 'Helvetica',
                      'other': 'new century schoolbook',
                      'size' : Context.FONTSIZE,
                      'size2': 10,
                     }
        
        
        self.filename ="";
        self.uiManager = None
        self.parentTab = None
        self.func = set()
        self.keywords = ["while","for","loop","forever","using","block","alias",
                    "if","elsif","else","then","case","of",
                    "input","output","at","is","all_output","all_input",
                    "on","off","true","false","high","low",
                    "const","var","volatile","bit","byte","sbyte","word","sword","dword","sdword",
                    "asm","assembler","bank","page","local","pragma","interrupt","task","start","suspend","target","clock","include","end",
                    "procedure","function","return","fuses","exit","repeat","until"]        
        
        #self.annotation =["--@no_debug","--@mpu","--@watch","--@watch_bin","--@watch_hex","--@lcd4bit","--@upDownCounter","--@dual7seg"]
        self.annotation =["@reg_filter","@var_filter","@device","@assertNotEqual","@assertLess","@assertGreater","@assertEquals","@no_debug_all",
                          "@no_debug","@mpu","@mpd","@ppu","@ppd","@pot","@watch","@watch_bin",
                          "@watch_hex","@lcd4bit","@upDownCounter","@dual7seg","@uartReceiver","@asciiReceiver",
                          "@midiSender","@asciiSender","@byteSender", 
                          "@led","@led_red","@led_orange","@led_yellow","@led_green","@led_blue","@use_virtual_delay","@labelIn","@labelOut"
                          ,"@uartReceiver" # backward compatibility, receiver was incorectly spelled
                          ]
        
        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.SetLexer(stc.STC_LEX_MSSQL)
        self.SetKeyWords(0, " ".join(self.keywords))
        
        self.SetMarginWidth(0, 30);      
        self.SetMarginType(0, 1);        
        self.SetMarginWidth(2, 12)
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        
        self.SetMarginSensitive(2, True)
        self.Bind(stc.EVT_STC_MARGINCLICK, self.OnMarginClick)
     
        self.SetTabWidth(Context.TABSIZE)
        self.SetUseTabs( Context.USETABS )
        self.SetViewWhiteSpace(False)
        self.SetBufferedDraw(False)
        self.SetUseAntiAliasing(False)
        
        
        self.SetPrintMagnification (-3) # for print preview
        self.SetEOLMode(STC_EOL_CRLF)

        # Setup a margin to hold fold markers
        #self.SetFoldFlags(16)  ###  WHAT IS THIS VALUE?  WHAT ARE THE OTHER FLAGS?  DOES IT MATTER?
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyPressed)
        self.Bind(EVT_STC_DOUBLECLICK, self.OnDblClick)
        
        self.DragAcceptFiles(False)

        # Make some styles,  The lexer defines what each style is used for, we
        # just have to define what each style looks like.  This set is adapted from
        # Scintilla sample property files.

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
        self.StyleClearAll()  # Reset all to be like the default

        # Global default styles for all languages
        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_LINENUMBER,  "back:#C0C0C0,face:%(mono)s,size:%(size2)d" % faces)
        self.StyleSetSpec(stc.STC_STYLE_CONTROLCHAR, "face:%(other)s" % faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")

        self.StyleSetSpec(stc.STC_MSSQL_DEFAULT,     "fore:#000000,ace:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_MSSQL_LINE_COMMENT,     "fore:#309030,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_MSSQL_NUMBER,     "fore:#C00000,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_MSSQL_STATEMENT,     "fore:#000080,bold,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_MSSQL_STORED_PROCEDURE,     "fore:#400000,bold,face:%(mono)s,size:%(size)d" % faces)
        self.StyleSetSpec(stc.STC_MSSQL_VARIABLE,     "fore:#ff6000,bold,face:%(mono)s,size:%(size)d" % faces)

        self.StyleSetSpec(1, "back:#FF0000,face:%(mono)s,size:%(size)d" % faces)

    


        self.SetSelBackground(True,"#000080")
        self.SetSelForeground(True,"#FFFFFF")
        self.SetCaretLineBack("#E8F2FE")
        self.SetCaretLineVisible(1) 
        self.SetCaretWidth(2)
        self.SetTabIndents(True)
        
        self.IndicatorSetStyle(0, stc.STC_INDIC_SQUIGGLE)
        self.IndicatorSetForeground(0, wx.RED)
        self.IndicatorSetStyle(1, stc.STC_INDIC_SQUIGGLE)
        self.IndicatorSetForeground(1, "#C0C000")
        
        self.IndicatorSetStyle(2, stc.STC_INDIC_BOX)
        self.IndicatorSetForeground(2, "#FF4040")
      
        # register some images for use in the AutoComplete box.
        self.RegisterImage(1, picshell.icons.embedded_icons.keyword_icon.GetBitmap()) # keywords
        self.RegisterImage(2, wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, size=(16,16)))# includes
        self.RegisterImage(3, picshell.icons.embedded_icons.volatile_icon.GetBitmap())  # volatile
        self.RegisterImage(4, picshell.icons.embedded_icons.loc_method_icon.GetBitmap())  # func 
        self.RegisterImage(5, picshell.icons.embedded_icons.annotation_icon.GetBitmap())  # proc
        self.RegisterImage(6, picshell.icons.embedded_icons.loc_var_icon.GetBitmap())  # in file vars
        self.RegisterImage(7, picshell.icons.embedded_icons.none_icon.GetBitmap()) # none
        
        if wx.Platform == '__WXMSW__':
            self.Bind(wx.EVT_SIZE, self.OnSize)
    
        self.Bind(EVT_STC_CHANGE,self.modified)
        self.Bind(EVT_STC_SAVEPOINTREACHED,self.savePoint)
        
        
    def modified(self,event):
        try :
            whichPage = self.parentTab.GetSelection();
            if whichPage== Context.TAB_DEBUG:
                whichPage = Context.TAB_EDIT;
                
            pageName = self.parentTab.GetPageText(whichPage)
            if (not pageName.endswith("*")):
                    pageName += "*"
                    self.parentTab.SetPageText(whichPage,pageName)
        except : pass
                
    def savePoint(self,event):
       self.parentTab.SetPageText(self.parentTab.GetSelection(),self.filename)
            
    def OnSize(self,event):
        # remove marks on the right bar
        try :
            draw = self.uiManager.fixedMark
            dc =wx.ClientDC ( draw )
            draw.diagram.Clear(dc)
            draw.diagram.RemoveAllShapes()
        except : pass
        event.Skip()
        
    
    def markText(self,start,end):
        self.StartStyling(start, stc.STC_INDICS_MASK)
        self.SetStyling(end-start , stc.STC_INDIC2_MASK)
    
    def unMarkText(self,start,end):
        self.StartStyling(start, stc.STC_INDIC2_MASK)
        self.SetStyling(end-start , 0)
           
    def markLineError(self,line):
        end = self.GetLineEndPosition(line)
        start = end - len(self.GetLine(line))   
        self.StartStyling(start, stc.STC_INDIC1_MASK | stc.STC_INDIC0_MASK)
        self.SetStyling(len(self.GetLine(line)) , stc.STC_INDIC0_MASK)
    
    def markLineWarning(self,line):
        end = self.GetLineEndPosition(line)
        start = end - len(self.GetLine(line))   
        self.StartStyling(start, stc.STC_INDIC1_MASK | stc.STC_INDIC0_MASK)
        self.SetStyling(len(self.GetLine(line)) , stc.STC_INDIC1_MASK)
    
    def unMarkLine(self,line):
        end = self.GetLineEndPosition(line)
        start = end - len(self.GetLine(line))   
        self.StartStyling(start, stc.STC_INDIC1_MASK | stc.STC_INDIC0_MASK)
        self.SetStyling(len(self.GetLine(line)) , 0)
    
    def showOccurences(self):
        
        self.uiManager.top.SetCursor(HOURGLASS_CURSOR)
        sel =  self.GetTextRange(self.GetSelection()[0],self.GetSelection()[1])
        t = self.GetText()
        self.unMarkText(0,len(t))
        
        draw = self.uiManager.fixedMark
        dc =wx.ClientDC ( draw )
        draw.diagram.Clear(dc)
        draw.diagram.RemoveAllShapes()
        
        sizey =  draw.GetSize()[1] -16
        nbLine = self.GetLineCount()
        if nbLine < self.LinesOnScreen() :
            nbLine = self.LinesOnScreen()
        
        for i in range(0,len(t)) :
            
            oChar = ord(t[i].upper())
            if  (oChar >=65 and oChar<= 90) or (oChar >=48 and oChar<= 57) or oChar ==95 :
                i = i+1
            elif re.search("^\W"+sel+"\W",t[i:]) :
            #if t[i:].startswith(sel):
                self.markText(i+1,i+len(sel)+1)
                l = self.LineFromPosition(i)
                posy = float(l*sizey)/nbLine
                shape = ogl.RectangleShape(8,5)
                shape.SetBrush( wx.Brush ( "#FFFFC0" ))
                shape.SetDraggable(False)
                draw.diagram.AddShape(shape)
                shape.Show(True)
                shape.SetX(5)
                shape.SetY(int(posy))
        
        self.Colourise(0,-1)
        draw.diagram.Redraw(dc)    
        self.uiManager.top.SetCursor(STANDARD_CURSOR)    
    
    def OnDblClick(self,event):
        if wx.GetKeyState(wx.WXK_CONTROL) :
            self.showOccurences()
        elif (self.uiManager!= None):    
            self.uiManager.compileTab.SetSelection(2)
            sel =  self.GetTextRange(self.GetSelection()[0],self.GetSelection()[1])
            if sel.startswith("@"):
                sel = sel[1:]
            # is a picshell annotation ?
            if "@"+sel in self.annotation :
                comment = DocHelper.getAnnotationHelp("@"+sel)
            else :
                # try to find method comment in main file
                comment = EditorUtil.findMethodComment(self.GetText(), sel)
                if comment == None :
                    # try to find comment in included file
                    res = EditorUtil.searchCommentInAllIncludes(sel,self.GetText(),Context.libpath+";"+os.path.dirname(self.filename))
                    comment = res[1]
     
            # show comment if any
            if comment != None and self.uiManager != None:
                self.uiManager.helpText.SetText(comment)
            
    def toggleCommentSelectedLines(self):
        (start,stop) = self.GetSelection()
        lstart = self.LineFromPosition(start);
        lstop = self.LineFromPosition(stop);
        for line in range(lstart,lstop+1):
            pos = self.PositionFromLine(line)
            txt = self.GetLine(line)
            if txt.startswith("--"):
                self.SetCurrentPos(pos+2)
                self.DelLineLeft()
            else:
                if not (line == lstop and txt.strip() ==""):
                    self.InsertText(pos,"--")
                        
    def OnKeyPressed(self, event):
        key = event.GetKeyCode()
        
        self.unMarkLine(self.GetCurrentLine())
        if self.parentTab == None:
            return

        pageName = self.parentTab.GetPageText(self.parentTab.GetSelection())
        
        # ----------------------------------------------------------------------------------
        # Comment / decomment selection
        #
       
        if key == 27 :
            t = self.GetText()
            self.unMarkText(0,len(t))
            draw = self.uiManager.fixedMark
            dc =wx.ClientDC ( draw )
            draw.diagram.Clear(dc)
            draw.diagram.RemoveAllShapes()
            self.Colourise(0,-1)
            return 
        
       
        if key == 45 and  event.ControlDown(): # ctrl + -
            self.toggleCommentSelectedLines()
            
        # ----------------------------------------------------------------------------------
        # Type assist
        # Comlete structures 
        #
        if key == 32 and not event.ControlDown():
            
            if Context.completeStructure == "true" :
                pos = self.GetCurrentPos()
                lineTxt = self.GetCurLine()[0]
                indent =""
                for c in lineTxt:
                    if c not in [" ","\t"]:
                        break
                    else :
                        indent+= c
                
                # don't look in comment
                lastCom =  self.lastword(lineTxt.rstrip())
                lineTxt = lineTxt.replace("--",";")
                lineTxt = lineTxt.split(";")[0]
                last =  self.lastword(lineTxt.rstrip())
               
                
                if last == "if":
                    self.InsertText(pos," expr then\n"+indent+"\n"+indent+"end if");
                    self.SetSelection(pos+1,pos+5)
                    return
                elif last == "elsif":
                    self.InsertText(pos," expr then\n"+indent);
                    self.SetSelection(pos+1,pos+5)
                    return
                elif last == "while":
                    self.InsertText(pos," expr loop end loop");
                    self.SetSelection(pos+1,pos+5)
                    return 
                elif last == "repeat" :
                    self.InsertText(pos,"\n"+indent+"\n"+indent+"until expr");
                    self.SetSelection(pos+10,pos+14)
                    return
                elif last == "exit":
                    self.InsertText(pos," loop");
                    self.SetSelection(pos+5,pos+5)
                    return 
                elif last == "for" :
                    self.InsertText(pos," expr loop\n"+indent+"\n"+indent+"end loop");
                    self.SetSelection(pos+1,pos+5)
                    return 
                elif last == "case" :
                    self.InsertText(pos," expr of\n"+indent+"\n"+indent+"end case");
                    self.SetSelection(pos+1,pos+5)
                    return            
                elif last == "procedure":
                    self.InsertText(pos," name() is \n"+indent+"\n"+indent+"end procedure\n");
                    self.SetSelection(pos+1,pos+5)
                    return
                elif last == "function":
                    self.InsertText(pos," name() return byte is \n"+indent+"\n"+indent+"end function\n");
                    self.SetSelection(pos+1,pos+5)
                    return
                elif last == "task" :
                    self.InsertText(pos," name () is\n"+indent+"\n"+indent+"end task");
                    self.SetSelection(pos+1,pos+5)
                    return
                elif last == "forever":
                    self.InsertText(pos," loop\n\t\n"+indent+"end loop\n");
                    self.SetSelection(pos+7,pos+7)
                    return
                #
                # Annotations
                #    
                elif lastCom == "@mpd" or lastCom == "@mpu" or lastCom == "@ppd" or lastCom == "@ppu" or lastCom == "@pot":
                    if lineTxt.strip().startswith("var "):
                        self.InsertText(pos," label");
                        self.SetSelection(pos+1,pos+6)   
                        return 
                    else :
                        self.InsertText(pos," label pin_"); 
                        self.SetSelection(pos+1,pos+6)
                        return   
                elif lastCom == "@watch" or lastCom == "@watch_bin" or lastCom == "@watch_dec" :
                    self.InsertText(pos," ADDRESS [label]");
                    self.SetSelection(pos+1,pos+8)   
                    return
                elif lastCom == "@led" or lastCom.startswith ("@led_") :
                    self.InsertText(pos," pin_ [label]");
                    self.SetSelection(pos+1,pos+5)   
                    return
                elif lastCom == "@upDownCounter" :
                    self.InsertText(pos," ADDRESS,enable_bit,impulsion_bit,up_down_bit,max_value [label]");
                    self.SetSelection(pos+1,pos+8)   
                    return
                elif lastCom == "@lcd4bit" :
                    self.InsertText(pos," ADDRESS,16 [label]");
                    self.SetSelection(pos+1,pos+8)   
                    return
                elif lastCom == "@dual7seg" :
                    self.InsertText(pos," ADDRESS,resetBit,digit1_Bit,digit2_Bit [label]");
                    self.SetSelection(pos+1,pos+8)   
                    return
                
                elif lastCom == "@reg_filter" or lastCom == "@var_filter":
                    self.InsertText(pos," expression");
                    self.SetSelection(pos+1,pos+11)   
                    return
                elif lastCom == "@dual7seg" :
                    self.InsertText(pos," ADDRESS,resetBit,digit1_Bit,digit2_Bit [label]");
                    self.SetSelection(pos+1,pos+8)   
                    return
                
                elif lastCom == "@labelIn" :
                    self.InsertText(pos," text");
                    self.SetSelection(pos+1,pos+5)   
                    return
                elif lastCom == "@labelOut" :
                    self.InsertText(pos," text");
                    self.SetSelection(pos+1,pos+5)   
                    return
            
                
        # ----------------------------------------------------------------------------------
        # Find finc/proc declaration
        #
        if key == 72 and event.ControlDown(): #  ctrl + h
            self.locateSelectionDeclaration()
            return
                        
        # ----------------------------------------------------------------------------------
        # code formating
        #
        elif key == 70 and event.ControlDown() and event.ShiftDown(): # shift + ctrl + f
            self.formatCode()
                
        # ----------------------------------------------------------------------------------
        # Save
        #
        elif key == 83 and event.ControlDown(): # ctrl + s
           top = Context.top
           top.OnSave(event)
           return
       
            
         
        # ----------------------------------------------------------------------------------
        # search prev
        #
        elif (wx.WXK_F3 == key and event.ShiftDown()) or key == 74 and event.ControlDown(): # ctrl + j or shfit F3: search prev
            self.findPrev()

        #
        # search next
        #
        elif (wx.WXK_F3 == key )or(key == 75 and event.ControlDown() ): # ctrl + k or F3 : search next
            self.findNext()

        # ----------------------------------------------------------------------------------
        # Find / replace
        #
        elif key == 70 and event.ControlDown(): # ctrl + f : find
            dlg = FindDialog(self, -1, "Find/Replace",style = wx.DEFAULT_DIALOG_STYLE)
            dlg.CenterOnScreen()
            dlg.Show()
        
        # ----------------------------------------------------------------------------------
        # Auto completion
        #
        elif key == 32 and event.ControlDown():# ctrl space - auto completion
            kw = []            
            text = self.GetText()
            upperText = text[0:self.GetCurrentPos()]
            lasttext = self.lastword(upperText)
            
            localv = JalV2Parser.findLocalVar(upperText.upper())
            const = JalV2Parser.findConst(upperText.upper())
          
            globalv = []
            (funcs,procs,globalVars) = JalV2Parser.parse(upperText.split("\n"));
            for each in globalVars:
                globalv.append(each.name)
            
            sf = funcs.keys()
            sf.sort()
            sp = procs.keys()
            sp.sort()
            
            # visible vars
            vars = list(set(localv).union(set(globalv)))
            vars.sort()
           
            kw += const
            kw += vars
            kw += sf
            kw += sp
            kw += self.keywords
            kw += self.annotation
            
            lineToCaret = self.lineToCaret();
            lineToCaret = lineToCaret.strip()
            text = self.lastword(text)
            
            volatile = []
            methods = []
            libs = EditorUtil.findAllLibs(Context.libpath+";"+os.path.dirname(self.filename))
            includes = EditorUtil.findAllIncludes(self.GetText(),Context.libpath)
            
            libs = list(set(libs)) # ensure unique names
            
            
            volatile =set()
            methods = set()
            for inc in includes:
                volatile = volatile.union(EditorUtil.findInFile(inc+".jal",Context.libpath,"volatile",3))
                methods = methods.union(EditorUtil.findInFileStartswith(inc+".jal",Context.libpath+";"+os.path.dirname(self.filename),"procedure",1))
                methods = methods.union(EditorUtil.findInFileStartswith(inc+".jal",Context.libpath+";"+os.path.dirname(self.filename),"function",1))
            volatile = list(volatile)
            volatile.sort()  
            kw += volatile
            
            methods = list(methods)
            methods.sort()
            kw += methods
            
            # 1 keywords
            # 2 includes
            # 3 volatile
            # 4 func 
            # 5 proc
            # 6 in file vars
            # 7 asm opcode
            # special cases
            
            if (lineToCaret.endswith("--") or lineToCaret.endswith(";")):
                kw = self.annotation
                
            if ("INCLUDE" in lineToCaret.upper() or  lineToCaret.endswith("@no_debug") or  lineToCaret.endswith("@debug")) :
                kw = libs+["@no_debug","@debug"] 
            
            if ("INCLUDE" in lineToCaret.upper()) and ((lineToCaret.endswith("--") or lineToCaret.endswith(";"))):
                kw = ["@no_debug","@debug"]
            
            if (lineToCaret.startswith(";@no_debug")):
                kw = libs
            if (lineToCaret.startswith(";@debug")):
                kw = libs
                
            if (lineToCaret.endswith("end")):
                kw = ["procedure","function","if","loop","block","case","task","assembler"]
            if (lineToCaret.endswith("var")):
                kw = ["bit","byte","sbyte","word","sword","dword","sdword","volatile"]
            
            if (lineToCaret.endswith("_direction =")):
                kw = ["input","output","all_input","all_output"]
            if ("const" in lineToCaret or "volatile" in lineToCaret):
                kw = ["bit","byte","sbyte","word","sword","dword","sdword"]
            if ("asm" in lineToCaret):
                kw = ["ADDLW","ADDWF","ANDLW","ANDWF","BCF","BSF","BTFSC","BTFSS","CALL","CLRF","CLRW","CLRWDT","COMF","DECF","DECFSZ","GOTO","INCF","INCFSZ","IORLW","IORWF","MOVF","MOVLW","MOVWF","NOP","RETFIE","RETLW","RETURN","RLF","RRF","SLEEP","SUBLW","SUBWF","SWAPF","XORLW","XORWF","local"]
                kw += volatile
            
            kwtoshow = []
            for i in range(len(kw)):
                if (kw[i].upper().startswith(lasttext.upper())):
                    if kw[i] in self.keywords:
                        kwtoshow.append(kw[i] + "?1")
                    elif kw[i] in volatile:
                        kwtoshow.append(kw[i] + "?3")
                    elif kw[i] in funcs.keys() or kw[i] in procs.keys() or kw[i] in methods:
                        kwtoshow.append(kw[i] + "?4")
                    elif kw[i] in self.annotation:
                        kwtoshow.append(kw[i] + "?5")
                    elif kw[i] in localv+globalv:
                        kwtoshow.append(kw[i] + "?6")  
                    elif kw[i] in libs:
                        kwtoshow.append(kw[i] + "?2")
                    else: 
                        kwtoshow.append(kw[i] + "?7") 
            
            if len(kwtoshow) > 0:
                self.AutoCompSetIgnoreCase(True)  # so this needs to match
                self.AutoCompSetDropRestOfWord(True)
                self.AutoCompSetChooseSingle(True)        
                self.AutoCompShow(len(lasttext), " ".join(kwtoshow))
              
        # ----------------------------------------------------------------------------------
        # Enter key (block completion and indentation management
        #
        if key == 13 and not event.ControlDown(): # on [enter] key 
            if not self.AutoCompActive() :
                
                if Context.completeStructure == "true" :
                    pos = self.GetCurrentPos()
                    lineTxt = self.GetCurLine()[0]
                    indent =""
                    for c in lineTxt:
                        if c not in [" ","\t"]:
                            break
                        else :
                            indent+= c
                    
                    # don't look in comment
                    lineTxt = lineTxt.replace("--",";")
                    lineTxt = lineTxt.split(";")[0]
                    last =  self.lastword(lineTxt.rstrip())
                    
                    # some auto complete
                    if last == "assembler" :
                        self.InsertText(pos,"\n"+indent+"end assembler");
                    elif last == "block" :
                        self.InsertText(pos,"\n"+indent+"end block");
                
                
                # get same indentation as curent line
                pos = self.GetCurrentPos()
                line = self.GetCurrentLine()
                if line > 0 :
                    if self.GetText()[pos-1] != "\n" :
                        indent = ""
                        prevLineTxt = self.GetLine(line);
                        for c in prevLineTxt:
                            if c not in [" ","\t"]:
                                break
                            else :
                                indent+= c
                        size = len(indent);
                        self.InsertText(pos,"\n"+indent)
                        self.SetSelection(pos+size+1,pos+size+1)
                        return        
        
        event.Skip()
    
    def lastword(self,texte):
        res = ""
        for i in range (len(texte)-1,-1,-1):
            if (texte[i] not in [" ","\t","\n",".",")","(","-",";",","]):
                res = texte[i]+res
            else:
                break;
        return res
    
    def lineToCaret(self):
        end = self.GetCurrentPos()
        text = self.GetText()[:end]
        res = ""
        for i in range (len(text)-1,-1,-1):
            if (text[i] not in ["\n"]):
                res = text[i]+res
            else:
                break;
        return res
    #click on margin
    def OnMarginClick(self, evt):
        # fold and unfold as needed
        lineClicked = self.LineFromPosition(evt.GetPosition())
        if evt.GetMargin() == 2:
           # print lineClicked
           pass
       
    def _findNext(self,what):
        l = len(what)
        self.SetSelection(-1, self.GetCurrentPos());
        self.SearchAnchor()
        res = self.SearchNext(0,what);
        if (res != -1) :
            self.SetSelection(self.GetCurrentPos(),self.GetCurrentPos()+l);
        else :
            self.SetCurrentPos(0)
            self.SetSelection(0, 0);
            self.SearchAnchor()
            res = self.SearchNext(0,what);
            if (res != -1) :
                self.SetSelection(self.GetCurrentPos(),self.GetCurrentPos()+l);
        
    def locateSelectionDeclaration(self):
        sel =  self.GetTextRange(self.GetSelection()[0],self.GetSelection()[1])
        if sel != "":
            
            # -------------------------------------------------------------
            # include ?
            text = self.GetCurLine()[0]
            if (text.upper().startswith("INCLUDE")):
                filename = text.split(" ")[1].strip()
                libpath = Context.libpath
                libs = libpath.split(";")
                mainPath = os.path.dirname(self.uiManager.mainEditor.filename)
                libs.append(mainPath)
                for lib in libs:
                    filenameFull=lib+"\\"+filename+".jal"
                    if os.path.exists(filenameFull):
                        pageName = self.uiManager.browserEditor.parentTab.GetPageText(Context.TAB_BROWSER)
                        if not pageName.endswith("*"):
                            self.uiManager.openEditor(2,filename=filenameFull);
                            self.uiManager.tab.SetSelection(Context.TAB_BROWSER)
                            
            #---------------------------------------------------------------------    
            # Method ?
            # search current text
            line = EditorUtil.findMethod(self.GetText(), sel)
            if line != None :
                self.GotoLine(int(line))
                self.SetCurrentPos(self.GetLineEndPosition(int(line)))
                
            else :
                # search in included files
                res = EditorUtil.searchInAllIncludes(sel,self.GetText(),Context.libpath+";"+os.path.dirname(self.filename))
                filename = res[1]
                line = res[2]
                if (filename != None) and (line != None) :
                    self.uiManager.openEditor(Context.TAB_BROWSER, filename)
                    self.uiManager.tab.SetSelection(Context.TAB_BROWSER)
                    self.uiManager.browserEditor.GotoLine(int(line))
                    self.uiManager.browserEditor.SetCurrentPos(self.uiManager.browserEditor.GetLineEndPosition(int(line)))
                    self.uiManager.browserEditor.SetFocus()
                    
    def formatCode(self):
        # format the source code
        
        text = self.GetText().split("\n")
        self.SetText("");
        level = 0
        res = ""
        
        for lg in text:
            
            lg = lg.strip()
            ulg = lg.upper()
            ulg = ulg.split("--")[0]
            ulg = ulg.strip()
            
            if ulg.startswith("END ") :
                level -=1
            if ulg.startswith("ELSE") :
                level -=1
            if ulg.startswith("ELSIF") :
                level -=1

            tabIdent = ""
            
            for iTab in range ( 0, Context.TABSIZE ) :
                tabIdent = tabIdent + " "
                
            tab = level * tabIdent
            
            res += tab+lg+"\n"
            if ulg.startswith("PROCEDURE ") or \
                ulg.startswith("FUNCTION ") or \
                ulg.endswith("THEN") or \
                (ulg.endswith("BLOCK") and not "END" in ulg) or \
                ulg.startswith("BLOCK ") or \
                ulg.startswith("ELSE") or \
                ulg.startswith("FOREVER ") or \
                ulg.startswith("FOR ") or \
                (ulg.startswith("CASE " )and not "END" in ulg) or \
                (ulg.startswith("WHILE ") and not "END" in ulg):
                level +=1
            if level < 0:
                level = 0
        self.SetText(res)  
    
    def findNext(self):
        sel = self.GetTextRange(self.GetSelection()[0],self.GetSelection()[1])
        self._findNext(sel)
    def findPrev(self):
        sel = self.GetTextRange(self.GetSelection()[0],self.GetSelection()[1])
        l = len(sel)
        self.SetCurrentPos(self.GetCurrentPos()-l);
        self.SearchAnchor()
        res = self.SearchPrev(0,sel);
        if (res != -1) :
            self.SetSelection(self.GetCurrentPos(),self.GetCurrentPos()+l);
        else :
            self.SetCurrentPos(self.GetTextLength())
            self.SetSelection(self.GetTextLength(),self.GetTextLength())
            self.SearchAnchor()
            self.SearchPrev(0,sel);
