from picshell.engine.core.InstModel import InstModel
from picshell.engine.core.Inst import Inst
from picshell.engine.core import Mnemonic

#
# PIC 16 bit Builder
#

class PicBuilder_PIC16:
    
        
    def __init__(self):
        self.opcode = [       
			"0000000000000000",    # 0  NOP
			"0000000000000011",    # 1  SLEEP
			"0000000000000100",    # 2  CLRWDT
			"0000000000000101",    # 3  PUSH
			"0000000000000110",    # 4  POP
			"0000000000000111",    # 5  DAW
			"0000000000001000",    # 6  TBLRD*
			"0000000000001001",    # 7  TBLRD*+
			"0000000000001010",    # 8  TBLRD*-
			"0000000000001011",    # 9  TBLRD+*
			"0000000000001100",    # 10 TBLWT*
			"0000000000001101",    # 11 TBLWT*+
			"0000000000001110",    # 12 TBLWT*-
			"0000000000001111",    # 13 TBLWT+*
			"0000000000010100",    # 14 CALLW
			"0000000011111111",    # 15 RESET
			"000000000001000",     # 16 RETFIE
			"000000000001001",     # 17 RETURN
			"000000010000",        # 18 MOVLB
			"1110100011",          # 19 ADDULNK
			"1110100111",          # 20 SUBULNK
			"1110111000",    		  # 21 LFSR
			"111010110",           # 22 MOVSF
			"111010111",           # 23 MOVSS
			"11100000",            # 24 BZ
			"11100001",            # 25 BNZ
			"11100010",            # 26 BC
			"11100011",            # 27 BNC
			"11100100",            # 28 BOV
			"11100101",            # 29 BNOV
			"11100110",            # 30 BN
			"11100111",            # 31 BNN
			"11101000",            # 32 ADDFSR
			"11101001",            # 33 SUBFSR
			"11101010",            # 34 PUSHL
			"11101111",            # 35 GOTO
			"00001000",            # 36 SUBLW
			"00001001",            # 37 IORLW
			"00001010",            # 38 XORLW
			"00001011",            # 39 ANDLW
			"00001100",            # 40 RETLW
			"00001101",            # 41 MULLW
			"00001110",            # 42 MOVLW
			"00001111",            # 43 ADDLW
			"1110110",             # 44 CALL
			"0110000",             # 45 CPFSLT
			"0110001",             # 46 CPFSEQ
			"0110010",             # 47 CPFSGT
			"0110011",             # 48 TSTFSZ
			"0110100",             # 49 SETF
			"0110101",             # 50 CLRF
			"0110110",             # 51 NEGF
			"0110111",             # 52 MOVWF
			"0000001",             # 53 MULWF
			"000001",              # 54 DECF
			"000100",              # 55 IORWF
			"000101",              # 56 ANDWF
			"000110",              # 57 XORWF
			"000111",              # 58 COMF
			"001000",              # 59 ADDWFC
			"001001",              # 60 ADDWF
			"001010",              # 61 INCF
			"001011",              # 62 DECFSZ
			"001100",              # 63 RRCF
			"001101",              # 64 RLCF
			"001110",              # 65 SWAPF
			"001111",              # 66 INCFSZ
			"010000",              # 67 RRNCF
			"010001",              # 68 RLNCF
			"010010",              # 69 INFSNZ
			"010011",              # 70 DCFSNZ
			"010100",              # 71 MOVF
			"010101",              # 72 SUBFWB
			"010110",              # 73 SUBWFB
			"010111",              # 74 SUBWF
			"11010",               # 75 BRA
			"11011",               # 76 RCALL
			"0111",                # 77 BTG
			"1000",                # 78 BSF
			"1001",                # 79 BCF
			"1010",                # 80 BTFSS
			"1011",                # 81 BTFSC
			"1100",                # 82 MOVFF
			"1111"                 # 83 2nd WORDS, translate to NOP
			]
        
        self.opcodeModel = [0]*84

        self.opcodeModel[ 0] = InstModel(Mnemonic.NOP,"NOP",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[ 1] = InstModel(Mnemonic.SLEEP,"SLEEP",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[ 2] = InstModel(Mnemonic.CLRWDT,"CLRWDT",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[ 3] = InstModel(None,"PUSH*",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[ 4] = InstModel(None,"POP",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[ 5] = InstModel(None,"DAW",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[ 6] = InstModel(Mnemonic.TBLRD,"TBLRD*",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[ 7] = InstModel(Mnemonic.TBLRD_POSTI,"TBLRD*+",InstModel.TYPE_LITERAL,False )
        self.opcodeModel[ 8] = InstModel(Mnemonic.TBLRD_POSTD,"TBLRD*-",InstModel.TYPE_LITERAL,False )
        self.opcodeModel[ 9] = InstModel(Mnemonic.TBLRD_PREI,"TBLRD+*",InstModel.TYPE_LITERAL,False )
        self.opcodeModel[10] = InstModel(Mnemonic.TBLWT,"TBLWT*",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[11] = InstModel(Mnemonic.TBLWT_POSTI,"TBLWT*+",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[12] = InstModel(Mnemonic.TBLRD_POSTD,"TBLWT*-",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[13] = InstModel(Mnemonic.TBLRD_PREI,"TBLWT+*",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[14] = InstModel(None,"CALLW",InstModel.TYPE_LITERAL)
        self.opcodeModel[15] = InstModel(None,"RESET",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[16] = InstModel(None,"RETFIE",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[17] = InstModel(Mnemonic.RETURN,"RETURN",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[18] = InstModel(Mnemonic.MOVLB,"MOVLB",InstModel.TYPE_LITERAL)
        self.opcodeModel[19] = InstModel(None,"ADDUNLK",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[20] = InstModel(None,"SUBUNLK",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[21] = InstModel(Mnemonic.LFSR,"LFSR",InstModel.TYPE_LITERAL_FF_12 )
        self.opcodeModel[22] = InstModel(None,"MOVSF",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[23] = InstModel(None,"MOVSS",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[24] = InstModel(None,"BZ",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[25] = InstModel(None,"BNZ",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[26] = InstModel(None,"BC",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[27] = InstModel(None,"BNC",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[28] = InstModel(None,"BOV",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[29] = InstModel(None,"BNOV",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[30] = InstModel(None,"BN",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[31] = InstModel(None,"BNN",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[32] = InstModel(None,"ADDFSR",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[33] = InstModel(None,"SUBFSR",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[34] = InstModel(None,"PUSHL",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[35] = InstModel(Mnemonic.GOTO,"GOTO",InstModel.TYPE_LITERAL_20)
        self.opcodeModel[36] = InstModel(Mnemonic.SUBLW,"SUBLW",InstModel.TYPE_LITERAL)
        self.opcodeModel[37] = InstModel(Mnemonic.IORLW,"IORLW",InstModel.TYPE_LITERAL)
        self.opcodeModel[38] = InstModel(Mnemonic.XORLW,"XORLW",InstModel.TYPE_LITERAL)
        self.opcodeModel[39] = InstModel(Mnemonic.ANDLW,"ANDLW",InstModel.TYPE_LITERAL)
        self.opcodeModel[40] = InstModel(Mnemonic.RETLW,"RETLW",InstModel.TYPE_LITERAL)
        self.opcodeModel[41] = InstModel(None,"MULLW",InstModel.TYPE_LITERAL)
        self.opcodeModel[42] = InstModel(Mnemonic.MOVLW,"MOVLW",InstModel.TYPE_LITERAL)
        self.opcodeModel[43] = InstModel(Mnemonic.ADDLW,"ADDLW",InstModel.TYPE_LITERAL)
        self.opcodeModel[44] = InstModel(Mnemonic.CALL,"CALL",InstModel.TYPE_LITERAL_S_20)
        self.opcodeModel[45] = InstModel(Mnemonic.CPFSLT,"CPFSLT",InstModel.TYPE_A_BYTE)
        self.opcodeModel[46] = InstModel(Mnemonic.CPFSEQ,"CPFSEQ",InstModel.TYPE_A_BYTE)
        self.opcodeModel[47] = InstModel(Mnemonic.CPFSGT,"CPFSGT",InstModel.TYPE_A_BYTE)
        self.opcodeModel[48] = InstModel(None,"TSTFSZ",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[49] = InstModel(Mnemonic.SETF,"SETF",InstModel.TYPE_A_BYTE)
        self.opcodeModel[50] = InstModel(Mnemonic.CLRF,"CLRF",InstModel.TYPE_A_BYTE)
        self.opcodeModel[51] = InstModel(Mnemonic.NEGF,"NEGF",InstModel.TYPE_A_BYTE)
        self.opcodeModel[52] = InstModel(Mnemonic.MOVWF,"MOVWF",InstModel.TYPE_A_BYTE)
        self.opcodeModel[53] = InstModel(None,"MULWF",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[54] = InstModel(Mnemonic.DECF16,"DECF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[55] = InstModel(Mnemonic.IORWF,"IORWF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[56] = InstModel(Mnemonic.ANDWF,"ADNWF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[57] = InstModel(Mnemonic.XORWF,"XORWF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[58] = InstModel(Mnemonic.COMF,"COMF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[59] = InstModel(Mnemonic.ADDWFC,"ADDWFC",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[60] = InstModel(Mnemonic.ADDWF,"ADDWF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[61] = InstModel(Mnemonic.INCF16,"INCF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[62] = InstModel(Mnemonic.DECFSZ,"DECFSZ",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[63] = InstModel(Mnemonic.RRCF,"RRCF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[64] = InstModel(Mnemonic.RLCF,"RLCF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[65] = InstModel(Mnemonic.SWAPF,"SWAPF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[66] = InstModel(Mnemonic.INCFSZ,"INCFSZ",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[67] = InstModel(Mnemonic.RRNCF,"RRNCF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[68] = InstModel(Mnemonic.RLNCF,"RLNCF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[69] = InstModel(Mnemonic.INCFNSZ,"INFSNZ",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[70] = InstModel(Mnemonic.DCFSNZ,"DCFSNZ",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[71] = InstModel(Mnemonic.MOVF,"MOVF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[72] = InstModel(Mnemonic.SUBFWB,"SUBFWB",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[73] = InstModel(Mnemonic.SUBWFB,"SUBWFB",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[74] = InstModel(Mnemonic.SUBWF,"SUBWF",InstModel.TYPE_DA_BYTE)
        self.opcodeModel[75] = InstModel(None,"BRA",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[76] = InstModel(None,"RCAKK",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[77] = InstModel(None,"BTG",InstModel.TYPE_A_BIT)
        self.opcodeModel[78] = InstModel(Mnemonic.BSF,"BSF",InstModel.TYPE_A_BIT)
        self.opcodeModel[79] = InstModel(Mnemonic.BCF,"BCF",InstModel.TYPE_A_BIT)
        self.opcodeModel[80] = InstModel(Mnemonic.BTFSS,"BTFSS",InstModel.TYPE_A_BIT)
        self.opcodeModel[81] = InstModel(Mnemonic.BTFSC,"BTFSC",InstModel.TYPE_A_BIT)
        self.opcodeModel[82] = InstModel(None,"MOVFF",InstModel.TYPE_LITERAL,False)
        self.opcodeModel[83] = InstModel(Mnemonic.NNOP,"NOP*",InstModel.TYPE_LITERAL,False)

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

    def buildInstructionList(self,code, lastAddress = 0):
        cpt = 0
        list = [0]*len(code) #Inst[0]*len(code)
        adresse = 0
        
        if (lastAddress == 0 ):
            lastAddress = len( code )
        
        bitTable = (254,253,251,247,239,223,191,127)
        for i in range(0,lastAddress):
        
            lineBin = code[i]
            
            #if ( i < 50 ) :
            #print "DECODE " + "%06X" % i + " " + lineBin        

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
               
                if (op.type == InstModel.TYPE_A_BIT):
                    bits = data[0:3]
                    
                    if (data[3] == '0') :
                        inst.access = Inst.ACCESS_RAM
                    elif (data[3] == '1'):
                        inst.access = Inst.ACCESS_BSR

                    data = data[4:] # bit 7,8,9 a 0
                    inst.bit = int(bits,2)
                    inst.inv_bit = bitTable[inst.bit] # complement
                    inst.value = int(data,2)  & 0xFF

                elif (op.type == InstModel.TYPE_BYTE):
                    if (data[0] == '0') :
                        inst.dest = Inst.DEST_W
                    elif (data[0] == '1'):
                        inst.dest =Inst.DEST_F
                    data = '0' + data[4:] # bit 7..0
                elif (op.type == InstModel.TYPE_A_BYTE):
                    if (data[0] == '0') :
                        inst.access = Inst.ACCESS_RAM
                    elif (data[0] == '1'):
                        inst.access = Inst.ACCESS_BSR
                    data = data[1:]
                    inst.value = int(data,2)  & 0xFF
                elif (op.type == InstModel.TYPE_DA_BYTE):
                    if (data[0] == '0') :
                        inst.dest = Inst.DEST_W
                    elif (data[0] == '1'):
                        inst.dest =Inst.DEST_F
                    if (data[1] == '0') :
                        inst.access = Inst.ACCESS_RAM
                    elif (data[1] == '1'):
                        inst.access = Inst.ACCESS_BSR
                    data = data[2:]
                    inst.value = int(data,2)  & 0xFF
                    # print "DA_INST VALUE %02X" % inst.value

                elif (op.type == InstModel.TYPE_LITERAL_FF_12):
                   next_code = code[ i +1 ]
                   ff = data[ 0:2 ]

                   #print "LITERAL_FF_12 " +  data + " " +  next_code + " ff " + ff
                   
                   lit12 = data[ 2: ] + next_code[8:]
                   
                   #print "LITERAL_12 " +  lit12
                   
                   lit_int = int(lit12,2)
                   ff_int = int(ff,2)


                   inst.dest = ff_int + Inst.DEST_FSR_0
                   inst.value = lit_int
                   # print "LITERAL_12 isnt.dest %d " % inst.dest + " inst.value %04X" % inst.value

                elif (op.type == InstModel.TYPE_LITERAL_20):
                   next_code = code[ i +1 ]

                   #print "LITERAL_20_l " +  data
                   #print "LITERAL_20_h " +  next_code
                   lit20_addr = next_code[4:] + data
                   
                   #print "LITERAL_20 " +  lit20_addr
                   jump_location = int(lit20_addr,2) * 2
                   #print "LITERAL_20 next value " +  "%04X" % jump_location + " %d" % inst.adresse + " %06x" % inst.adresse
                   inst.value = jump_location	                
                    
                elif (op.type == InstModel.TYPE_LITERAL_S_20):
                   next_code = code[ i +1 ]

                   #print "LITERAL_S_20_l " +  data[1:]
                   #print "LITERAL_S_20_h " +  next_code
                   lit20_addr = next_code[4:] + data[1:]
                   
                   #print "LITERAL_S_20 " +  lit20_addr
                   jump_location = int(lit20_addr,2) * 2
                   #print "LITERAL_S_20 next value " +  "%04X" % jump_location + " %d" % inst.adresse + " %06x" % inst.adresse
                   inst.value = jump_location	                
                else:					
                    if (data !=""):
                        inst.value = int(data,2)  & 0xFF
                
                list[cpt] = inst
                cpt = cpt + 1
        return list
