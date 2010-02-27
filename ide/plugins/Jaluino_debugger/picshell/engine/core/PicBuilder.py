from picshell.engine.core.InstModel import InstModel
from picshell.engine.core.Inst import Inst
from picshell.engine.core import Mnemonic

#
# 14 bit Builder
#

class PicBuilder:
    
        
    def __init__(self):
        self.opcode = ["0000000000001000","0000000001100011","0000000001100100",
            "0000000000001001","000000010","000000000","00000111","00000101","00000001","00001001",
            "00000011","00001011","00001010","00001111","00000100","00001000","00000000","00001101",
            "00001100","00000010","00001110","00000110","00111001","00111000","00111010","0011111",
            "0011110","000100","000101","000110","000111","001100","001101","00100","00101"]
        
        self.opcodeModel = [0]*35
        self.opcodeModel[0] = InstModel(Mnemonic.RETURN,"RETURN",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[1] = InstModel(Mnemonic.SLEEP, "SLEEP", InstModel.TYPE_LITERAL, False)
        self.opcodeModel[2] = InstModel(Mnemonic.CLRWDT, "CLRWDT", InstModel.TYPE_LITERAL, False)   # to test
        self.opcodeModel[3] = InstModel(None, "RETFIE", InstModel.TYPE_LITERAL, False)  # interrupts are not supported for now
        self.opcodeModel[4] = InstModel(Mnemonic.CLRW, "CLRW", InstModel.TYPE_BYTE, False)        # don't do any thing for now...
        self.opcodeModel[5] = InstModel(Mnemonic.NOP, "NOP", InstModel.TYPE_BYTE, False)
        self.opcodeModel[6] = InstModel(Mnemonic.ADDWF, "ADDWF", InstModel.TYPE_BYTE)
        self.opcodeModel[7] = InstModel(Mnemonic.ANDWF, "ANDWF", InstModel.TYPE_BYTE)           # to test
        self.opcodeModel[8] = InstModel(Mnemonic.CLRF, "CLRF", InstModel.TYPE_BYTE)
        self.opcodeModel[9] = InstModel(Mnemonic.COMF, "COMF", InstModel.TYPE_BYTE)                      # to test
        self.opcodeModel[10] = InstModel( Mnemonic.DECF, "DECF", InstModel.TYPE_BYTE)           
        self.opcodeModel[11] = InstModel( Mnemonic.DECFSZ, "DECFSZ", InstModel.TYPE_BYTE)
        self.opcodeModel[12] = InstModel( Mnemonic.INCF, "INCF", InstModel.TYPE_BYTE)
        self.opcodeModel[13] = InstModel( Mnemonic.INCFSZ, "INCFSZ", InstModel.TYPE_BYTE)       # to test
        self.opcodeModel[14] = InstModel( Mnemonic.IORWF, "IORWF", InstModel.TYPE_BYTE)
        self.opcodeModel[15] = InstModel( Mnemonic.MOVF, "MOVF", InstModel.TYPE_BYTE)
        self.opcodeModel[16] = InstModel( Mnemonic.MOVWF, "MOVWF", InstModel.TYPE_BYTE)
        self.opcodeModel[17] = InstModel( Mnemonic.RLF, "RLF", InstModel.TYPE_BYTE)            
        self.opcodeModel[18] = InstModel(Mnemonic.RRF, "RRF", InstModel.TYPE_BYTE)            # to test
        self.opcodeModel[19] = InstModel( Mnemonic.SUBWF, "SUBWF", InstModel.TYPE_BYTE)
        self.opcodeModel[20] = InstModel( Mnemonic.SWAPF, "SWAPF", InstModel.TYPE_BYTE)
        self.opcodeModel[21] = InstModel(Mnemonic.XORWF, "XORWF", InstModel.TYPE_BYTE)           # to test
        self.opcodeModel[22] = InstModel( Mnemonic.ANDLW, "ANDLW", InstModel.TYPE_LITERAL)
        self.opcodeModel[23] = InstModel( Mnemonic.IORLW, "IORLW", InstModel.TYPE_LITERAL)         
        self.opcodeModel[24] = InstModel(Mnemonic.XORLW, "XORLW", InstModel.TYPE_LITERAL)          # to test
        self.opcodeModel[25] = InstModel( Mnemonic.ADDLW, "ADDLW", InstModel.TYPE_LITERAL)
        self.opcodeModel[26] = InstModel( Mnemonic.SUBLW, "SUBLW", InstModel.TYPE_LITERAL)          
        self.opcodeModel[27] = InstModel( Mnemonic.BCF, "BCF", InstModel.TYPE_BIT)
        self.opcodeModel[28] = InstModel( Mnemonic.BSF, "BSF", InstModel.TYPE_BIT)
        self.opcodeModel[29] = InstModel(Mnemonic.BTFSC, "BTFSC", InstModel.TYPE_BIT)
        self.opcodeModel[30] = InstModel( Mnemonic.BTFSS, "BTFSS", InstModel.TYPE_BIT)
        self.opcodeModel[31] = InstModel( Mnemonic.MOVLW, "MOVLW", InstModel.TYPE_LITERAL)
        self.opcodeModel[32] = InstModel( Mnemonic.RETLW, "RETLW", InstModel.TYPE_LITERAL)           
        self.opcodeModel[33] = InstModel( Mnemonic.CALL, "CALL", InstModel.TYPE_LITERAL)
        self.opcodeModel[34] = InstModel( Mnemonic.GOTO, "GOTO", InstModel.TYPE_LITERAL)        

    def _findOpCode(self,string):
        res = None
        for i in range(0,len(self.opcode)):
            key = self.opcode[i]
            if (string.startswith(key)):
                res = self.opcodeModel[i]
                break
        return res
    
    def _findOpCodeKey(self,string):
       res = ""
       for i in range(0,len(self.opcode)):
           key = self.opcode[i]
           if (string.startswith(key)):
               res = key
               break
       return res

    def buildInstructionList(self,code,lastAddress = 0):
        cpt = 0
        list = [0]*len(code) #Inst[0]*len(code)
        adresse = 0

        if (lastAddress == 0 ):
            lastAddress = len( code )

        bitTable = (254,253,251,247,239,223,191,127)
        for i in range(0,lastAddress):
        
            lineBin = code[i]
            if (lineBin != None):
                opcodeSignature = self._findOpCodeKey(lineBin)
                
                # According to datasheet, if prg eeprom has been written with garbage (or data)
                # PIC will see that has a NOP Instruction
                if (opcodeSignature ==""):
                    opcode = "0000000000000000" # NOP
                    opcodeSignature = "000000000"
                else :
                    opcode = lineBin
                data =opcode[opcode.index(opcodeSignature) + len(opcodeSignature):]
                op = self._findOpCode(opcode)
                bits = ""
                inst = Inst()
                inst.model = op
                inst.adresse = adresse
                adresse = adresse + 1
               
                if (op.type == InstModel.TYPE_BIT):
                    bits = data[0:3]
                    data = "000" + data[3:] # bit 7,8,9 a 0
                    inst.bit = int(bits,2)
                    inst.inv_bit = bitTable[inst.bit] # complement
                elif (op.type == InstModel.TYPE_BYTE):
                    if (data[0] == '0') :
                        inst.dest = Inst.DEST_W
                    elif (data[0] == '1'):
                        inst.dest =Inst.DEST_F
                    data = '0' + data[1:] # bit 7..0
                 #
                 # GOTO and CALL are the only two that can use k > 255
                 #
                if ("GOTO" == op.mnemonic) or ("CALL" == op.mnemonic) :
                    inst.value = int(data,2)
                else:
                    if (data !=""):
                        inst.value = int(data,2)  & 0xFF
                list[cpt] = inst
                cpt = cpt + 1
        return list
    
    
    
