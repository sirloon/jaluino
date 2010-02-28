from picshell.engine.hex.HexReader import HexReader
from picshell.engine.core.pics import PicFactory
from picshell.engine.core.pics import PIC_UNKOWN
from picshell.engine.core.pics import PIC_12
from picshell.engine.core.pics import PIC_14
from picshell.engine.core.pics import PIC_16
from picshell.engine.core.State import State
from picshell.engine.core.State_PIC16 import State_PIC16


import time

class PicEngine:
    
    def __init__(self,pic,progCode, adrDelay=None, lastAddress=0):
        self.pic = pic
        if self.pic.cpu_type == PIC_16:
           self.state = State_PIC16( self.pic )
        else:
           self.state = State( self.pic )
    	  
        self.monitors = ()

        # self.hash = {}
        
        if (lastAddress == 0 ):
            self.lastAddress = len( progCode )
        else:
            self.lastAddress = lastAddress
        

        self.nbExecuted = 0
        
        #self.state = state
        self.state.readProgramMem = self.readProgramMem
        self.state.writeProgramMem = self.writeProgramMem
        self.adrDelay = adrDelay # hash of delay [in fraction of sec] per address (address is the key)
        
        self.programMem = progCode 
                
        self.instructionList = self.state.getBuilder().buildInstructionList(self.programMem, self.lastAddress + 1)  # array of Inst[]
        
        self.hexfilename = ""
        self.skipList =[0]*self.state.code_size
        
        for i in range(0,len(self.skipList)):
            self.skipList[i] = None
        # so that the UI can register its self to be notified when code change
        self.programMemUpdatedCallBack = None 
    
    def readProgramMem(self,adr, is16Bit = False ):
        try :
            dataL = int(self.programMem[adr],2)&0xFF # 8 bit 
            if is16Bit :
               dataH = (int(self.programMem[adr],2)>>8)&0xFF # 8bit
            else:
               dataH = (int(self.programMem[adr],2)>>8)&0x3F # 8bit
        except :
            print "PicEngine.readProgramMem : Invalide program memory location : "+str(adr)
        return (dataH,dataL)

    def writeProgramMem(self,adr,data):
        try :
            bin = data
            for j in range (16,len(data),-1):
                bin = "0" + bin
            self.programMem[adr] = str(bin)
        except :
            print "PicEngine.writeProgramMem : Invalide program memory location : "+str(adr)
        if adr<= self.lastAddress:
            self.instructionList = self.state.getBuilder().buildInstructionList(self.programMem)
        if self.programMemUpdatedCallBack != None:
            self.programMemUpdatedCallBack(data,adr,self.lastAddress,self.instructionList)
         
    def runForEver(self):
        while(True):
            self.runNext()
        
    
    def runXInstr(self,nbinst):
        while(True):
             if (self.nbExecuted >= nbinst):
                 break
             self.runNext()                 
        return self.nbExecuted+" instructions reached... breaking !"
   
    def runTillAddress(self,address):
        while(True):
            currentPC = self.state.pc        
            self.runNext()    
            if (currentPC >= (address)):
                break
        return "Address "+str(address)+" reached... breaking !"
    
    
    def getCurInst(self):
        return self.instructionList[self.state.pc]
       
    def runNext(self):
        
        inst = self.instructionList[self.state.pc]
        
        
        
        if (self.adrDelay != None) :
            if self.adrDelay.has_key(self.state.pc):
                # print "VIRTUAL DELAY %d " % self.state.pc
                time.sleep(self.adrDelay[self.state.pc])
            
        self.nbExecuted = self.nbExecuted+1

        code = inst.model.code
        # stat info
        #if inst.model.mnemonic in self.hash:
        #    self.hash[inst.model.mnemonic] = self.hash[inst.model.mnemonic] + 1  
        #else:
        #    self.hash[inst.model.mnemonic] = 1
        for monitor in self.monitors:
            monitor.executeBefore(self,inst)
        if (code != None) :
            #
            # Mnemonic code execution
            #
            if (code(self.state,inst) == False):
                self.state.incPc()
        else:
            print inst.model.mnemonic+" not implemented yet."
        for monitor in self.monitors:
            monitor.executeAfter(self,inst)
        
        return self.state.pc
    
    def runTillAddressIn(self,address):
            adr = 0
            doNext = True
            while(doNext):
                adr = self.runNext()    
                for i in range (0,len(address)):
                    if (adr == (address[i])):
                        doNext = False
                        break
            return adr
        
    #
    # adrDelay is used to map a delay array indexed by address to the simulator.
    # callBack is called if the code change (through programing eeprom), useful to update an UI
    @staticmethod
    def newInstance(picName,hexFileName,callBack=None,adrDelay=None):

        # print "CREATING PIC " + picName  
        
        pic = PicFactory( "pic_" + picName )
                       
        reader = HexReader( pic.code_size )
        
        # AF TODO CHECK BYTE/WORD SIZE
        code = [0]*pic.code_size

        lastAddress = reader.readData(hexFileName, code)
        emu = PicEngine(pic,code, adrDelay,lastAddress)
        emu.programMemUpdatedCallBack = callBack
        emu.lastAddress = lastAddress
        emu.hexfilename = hexFileName
        return emu

    def varValue(self,adr,type):
        type = type.upper()
        if type == "WORD":
            type = "BYTE*2"
        elif type == "DWORD":
            type = "BYTE*4"
        elif type == "BIT":
            pass
        elif type == "SBYTE":
            type = "SBYTE*1"
        elif type == "SWORD":
           type="SBYTE*2"
        elif type == "SDWORD":
            type="SBYTE*4"
            
        if "*" in type:
            parts = type.split("*")
            num = int(parts[1]) 
            format = "%02X" * num
            params = []
            for i in range (num-1,-1,-1):
                params.append(self.state.absreg(adr+i))
            word = format % tuple(params)
            wordVal = int (word,16)
            if parts[0] == "SBYTE":
                sign = self.state.absreg(adr+num-1) >> 7
                wordVal = int (word,16)
                if sign > 0:
                    #neg
                    max = pow(2,num*8)
                    wordVal = max - wordVal
                    wordVal *= -1
            
            val = wordVal
        else:
            val = self.state.absreg(adr)
        return val
