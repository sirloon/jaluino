# Address monitor

from picshell.engine.util.Format import Format
from picshell.engine.util import BitUtil

import  wx.lib.newevent
import wx

class LCD :

    # http://www.doc.ic.ac.uk/~ih/doc/lcd/initiali.html
    # http://www.myke.com/lcd.htm
   
    # Taken from bert's lcd jal lib
    #    
    #clear_display       = 0b_0000_0001
    #return_home         = 0b_0000_0010   
    #display_onoff       = 0b_0000_1000
    #   
    #cursor_shift_right  = 0b_0001_0100
    #cursor_shift_left   = 0b_0001_0000
    #display_shift_right = 0b_0001_1100
    #display_shift_left  = 0b_0001_1000
    #   
    #set_CGRAM_address   = 0b_0100_0000  + 6 bits address
    #set_DDRAM_address   = 0b_1000_0000  + 7 bits address
   
   
    #
    # HD44780 4 bits, 2x16 impl.
    #
    
    debug = False
       
    def __init__(self,name, address,nbChar=16):
       
        self.address = Format.toNumber(address)
        self.ui = None
        self.name = name
        self.reset()
        self.nb_char = nbChar
        self.type = "LCD"
   
    def reset(self):
        self.isData = False
        self.oldValue = 0
        self.oldClkValue = 0
        self.text = [0]*256;
        for i in range(0,len(self.text)):
            self.text[i] = " "
        self.indexText = 0;
        self.hi = -1;
        self.initted = False
        self.cptInitSeq = 0;
        for i in range(0,len(self.text)):
            self.text[i]=ord(' ')
        # let's say that value = None -> clear value
        wx.CallAfter(self.UpdateUI, None )
            
    def execute(self,value):
       #
       # A faire : determiner data ou cmd que lorsque je recois le HI
       #
        if self.debug:
           print "LCD execute %02X" % value       
        if (self.initted):
            if self.debug:
               print Format.binf(value)+" - 0x%X" %(value & 0x3F)
            if (BitUtil.isSet(value,5) ) and BitUtil.isClear(self.oldValue,5): # clock enable
                if self.debug:
                   print "---------------------------------------Clock"
                if (self.isData) :    # DATA
                    if (self.hi != -1) :

                        ascii = self.hi + (value&0xF)
                        
                        if self.debug:    
                           print "----------------->low_data:"+str(value)
                           print chr(ascii),
                           print "offset : "+str(int(self.indexText/0x40)*self.nb_char),
                           print "index  : "+str(self.indexText)
                           print "------->ASCII : "+str(ascii)

                        self.text[(self.indexText%0x40)+ int(self.indexText/0x40)*self.nb_char] = ascii
                        out ="";
                        
                        for i in range (0,self.nb_char*4):
                            c = self.text[i];
                            if (ord(' ')==c):
                                c=ord('-')
                            
                            out = out+""+chr(c);
                            
                            if self.debug:    
                                print "------->"+chr(c)
                            if (i%self.nb_char==self.nb_char-1):
                                out += "\n";

                        wx.CallAfter(self.UpdateUI, out )
                        
                        self.indexText +=1 # TODO : should depend on config.
                        self.hi = -1;
                    else: # hi data
                        self.isData = BitUtil.isSet(value,4)
                        self.hi = value&0XF;
                        if self.debug:                            
                            print "----------------->hi_data:"+str(self.hi)
                        self.hi <<=4;
                   
                else:  # COMMAND
                    if (self.hi != -1):
                        if self.debug:    
                            print "----------------->low_cmd:"+str(value)
                        whole = self.hi + (value&0xF)
                        self.hi = -1
                        if (whole == 1):
                            # let's say that value = None -> clear value
                            wx.CallAfter(self.UpdateUI, None )
                            
                        if ((whole&0x80)>0):
                            # position :
                            self.indexText = whole&0x7F;
                    else:
                        self.hi = value&0XF;
                        self.hi <<=4;
                        self.isData = self.isData = BitUtil.isSet(value,4)
                        if self.debug:    
                            print "----------------->hi_cmd:"+str(self.hi)
            
        else: # not initted yet
            if self.debug:
                print Format.binf(value)+" - 0x%X" %(value & 0x3F)
            if (BitUtil.isSet(value,5) ) and BitUtil.isClear(self.oldValue,5):
                if self.debug:
                    print "---------------------------------------Clock (not inited)"    
                if ((value&0x3F) == 0x23):
                    self.cptInitSeq+=1
                    if self.debug:    
                        print "======================Init LCD"
                else:
                    if self.debug:    
                        print " self.cptInitSeq %d" % self.cptInitSeq 
                        print " value %02X " % (value&0x3F)
                    if (self.cptInitSeq>=2):
                        if ((value&0x3F) == 0x22):
                            self.initted = True;
                            if self.debug:    
                                print "===============LCD INITED"
        self.oldValue = value
                            
    def UpdateUI(self,value):
       if ( self.ui != None ):
           self.ui.Clear() 
           if value != None :
               self.ui.AppendText( value )

    def CreateUI(self,parent, psizer ):
        self.ui = wx.TextCtrl(parent,size=(12*int(self.nb_char), 90),style=wx.TE_MULTILINE)
        self.ui.SetBackgroundColour("black")
        self.ui.SetForegroundColour("#40C040")
        self.ui.SetFont(wx.Font(10, wx.MODERN, wx.NORMAL, wx.BOLD))
        psizer.Add(self.ui)
