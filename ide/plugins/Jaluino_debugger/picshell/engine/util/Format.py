from picshell.engine.core.Inst import Inst
from picshell.engine.core.InstModel import InstModel
# 16F877/876 Formater
class Format:
    spAdrReg = {
                0x00:'INDF',
                0x01:'TMR0',
                0x02:'PCL',
                0x03:'STATUS',
                0x04:'FSR',
                0x05:'PORTA',
                0x06:'PORTB',
                0x07:'PORTC',
                0x08:'PORTD',
                0x09:'PORTE',
                0x0A:'PCLATH',
                0x0B:'INTCON',
                0x0C:'PIR1',
                0x0D:'PIR2',
                0x0E:'TMR1L',
                0x0F:'TMR1H',
                0x10:'T1CON',
                0x11:'TMR2',
                0x12:'T2CON',
                0x13:'SSPBUF',
                0x14:'SSPCON',
                0x15:'CCPR1L',
                0x16:'CCPR1H',
                0x17:'CCP1CON',
                0x18:'RCSTA',
                0x19:'TXREG',
                0x1A:'RCREG',
                0x1B:'CCPR2L',
                0x1C:'CCPR2H',
                0x1D:'CCP2CON',
                0x1E:'ADRESH',
                0x1F:'ADCON0',
                0x81:'OPTION_REG',
                0x85:'TRISA',
                0x86:'TRISB',
                0x87:'TRISC',
                0x88:'TRISD',
                0x89:'TRISE',
                0x8C:'PIE1',
                0x8D:'PIE2',
                0x8E:'PCON',
                0x91:'SSPCON2',
                0x92:'PR2',
                0x93:'SSPADD',
                0x94:'SSPSTAT',
                0x98:'TXSTA',
                0x99:'SPBRG',
                0x9E:'ADRESL',
                0x9F:'ADCON1'} 
       
    spReg = {'INDF':0x00,
            'TMR0':0x01,
            'PCL':0x02,
            'STATUS':0x03,
            'FSR':0x04,
            'PORTA':0x05,
            'PORTB':0x06,
            'PORTC':0x07,
            'PORTD':0x08,
            'PORTE':0x09,
            'PCLATH':0x0A,
            'INTCON':0x0B,
            'PIR1':0x0C,
            'PIR2':0x0D,
            'TMR1L':0x0E,
            'TMR1H':0x0F,
            'T1CON':0x10,
            'TMR2':0x11,
            'T2CON':0x12,
            'SSPBUF':0x13,
            'SSPCON':0x14,
            'CCPR1L':0x15,
            'CCPR1H':0x16,
            'CCP1CON':0x17,
            'RCSTA':0x18,
            'TXREG':0x19,
            'RCREG':0x1A,
            'CCPR2L':0x1B,
            'CCPR2H':0x1C,
            'CCP2CON':0x1D,
            'ADRESH':0x1E,
            'ADCON0':0x1F,
            'OPTION_REG':0x81,
            'TRISA':0x85,
            'TRISB':0x86,
            'TRISC':0x87,
            'TRISD':0x88,
            'TRISE':0x89,
            'PIE1':0x8C,
            'PIE2':0x8D,
            'PCON':0x8E,
            'SSPCON2':0x91,
            'PR2':0x92,
            'SSPADD':0x93,
            'SSPSTAT':0x94,
            'TXSTA':0x98,
            'SPBRG':0x99,
            'ADRESL':0x9E,
            'ADCON1':0x9F}
    
    def dumpInstructionListTillAddress(self,instructionList,address):
        for i in range(0,address+1):
            inst = instructionList[i]
            self.dumpInstruction(inst)
            
        
    @staticmethod
    def dumpInstruction(inst):
        print(Format.formatInstruction(inst, 0, False))
        
    @staticmethod
    def formatInstruction(inst,level,hex):
        adresse = ""
        if (hex):
            adresse = "0x%04X" % inst.adresse
            
        else:
            adresse =  "%d" % inst.adresse 
            
        length = len(adresse)
        for i in range (6,length, -1):
            adresse = " " + adresse
            
        res = adresse + " "
        res = res + Format.formatInstructionWithoutAddress(inst,level,hex)
        return res
    
    @staticmethod
    def formatInstructionWithoutAddress(inst,level,hex):
        res = ""
        for i in range (0,level):
            res = res + "|  "

        res = res + inst.model.mnemonic
        
        res += " "
        l = len(res)
        for i in range (10,l,-1):
            res += " "
        if (inst.model.hasData):
            if (hex):
                if (inst.value > 0xFF):
                    res = res +"0x%X" % inst.value
                else:
                    res = res +"0x%02X" % inst.value
                
            else: 
                res = res +"%d" % inst.value


            
            if (InstModel.TYPE_BIT == inst.model.type):
                res = res +", %d" % inst.bit
            if (InstModel.TYPE_A_BIT == inst.model.type):
                res = res +", %d" % inst.bit

            if (inst.model.mnemonic != "NOP"):
            	if (Inst.DEST_F == inst.dest):
            		res += ", f"
            	elif (Inst.DEST_W == inst.dest):
            		res += ", w"
            if (InstModel.TYPE_LITERAL_FF_12 == inst.model.type):
            	ff = inst.dest - Inst.DEST_FSR_0	     
            	res += ", %d" % ff 

            if (Inst.ACCESS_RAM == inst.access):
                res += ", ACCESS"
            elif (Inst.ACCESS_BSR == inst.access):
                res += ", BANKED"

        # end data data
        
        l = len (res)
        for i in range(30,l,-1):
            res = res + " "
       
        return res
    
    
    @staticmethod
    def bin(n):
        res = ''
        while n != 0: n, res = n >> 1, `n & 1` + res
        bin = res
        # pad with leading 0
        for j in range (8,len(res),-1):
            bin = "0" + bin
        return bin.replace("L","")
    @staticmethod
    def binf(n):
        res1 = Format.bin(n)
        res =""
        if len(res1) != 8 :
            for i in range(0,len(res1)):
                    res += res1[i]
        else:
            for i in range(0,len(res1)):
                res += res1[i]
                if ((i % 4)==3) and i<(len(res1)-1) :
                    res += "_"
        return res
    @staticmethod
    def bin10(n):
        res = ''
        while n != 0: n, res = n >> 1, `n & 1` + res
        bin = res
        # pad with leading 0
        for j in range (10,len(res),-1):
            bin = "0" + bin
        return bin.replace("L","")
    
    # explain
    
    @staticmethod
    def binfx(n,bit):
        res1 = Format.bin(n)
        res =""
        bit = 7-bit
        for i in range(0,len(res1)):
          
            if i == int(bit):
                res+="["
                
            res += res1[i]
            if i == bit:
                res+="]"
        
        return res
    
    @staticmethod
    def toNumber(str,varAdrMapping=None):
        if str == None :
            return 0
        if str =="" :
            return 0
        if (str.upper().startswith("0X")):
            return int(str,16)
        elif (str.upper().startswith("B")):
            return int(str[1:],2)
        else:
            try:
                 num = int(str)
            except :
                num = str 
                #is this a token like PORTA ?
                if str.upper() in Format.spReg:
                    num = Format.spReg[str.upper()]
                elif varAdrMapping !=None:
                    varKey = "v_"+str
                    if varKey in varAdrMapping :
                        num = varAdrMapping[varKey]
                    
                    #print "WARNING : toNumber failed on "+str+" so 0 will be used." 
            return num 
   