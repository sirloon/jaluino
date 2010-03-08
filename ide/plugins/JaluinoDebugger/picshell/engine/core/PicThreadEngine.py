import threading
import time
import wx

class PicThreadEngine (threading.Thread):
    
    
    def __init__(self,emu,unitTestCallBack=None):
        threading.Thread.__init__(self)
        self._stopevent = threading.Event( )
        self.runTillAddress = []
        self.callback = None
        self.emu = emu
        self.currentAdress = 0
        self.stopped = True
        self.unitTestCallBack = unitTestCallBack
    
    def run(self) :
        self.stopped = False
        self.currentAdress = 0
        
        if self.runTillAddress != None:
            while not self._stopevent.isSet(): 
               # time.sleep(0)    
               wx.Yield()
    
               self.currentAdress = self.emu.runNext()
               # print "run next addr : "+str(self.currentAdress)+ " len is " + str( len (self.runTillAddress) )
               
               #unit testing ?
               if self.unitTestCallBack != None :
                    self.unitTestCallBack(self.currentAdress)
               
               
               #if self.currentAdress >= len (self.runTillAddress):
               if False:
                   # seems to be a hudge problem...
                   print "This address is not reachable : "+str(self.currentAdress)+ " len is " + str( len (self.runTillAddress) )
                   self.currentAdress = 0
                   self.emu.state.pc = 0
                   self.runTillAddress = None
                   break
                  
               else:
                   if (self.runTillAddress.has_key(self.currentAdress) ):
                       self.runTillAddress = None
                       break
                   
        self.stop()   
        self.stopped = True
        self.callback(self.currentAdress)
        
    
    def stop(self):
        self._stopevent.set( )
        #print "Thread stops"


