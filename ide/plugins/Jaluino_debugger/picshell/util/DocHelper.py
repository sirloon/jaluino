from picshell.engine.core.Inst import Inst
from picshell.engine.util.Format import Format
def getAnnotationHelp(ano):
    help = "Syntax :\n  ;"+ano+" "
    if ano == "@watch":
        help+="address|variableName|token (label)\n"
        help+="Example :\n  ;"+ano+" PORTA test\n\n"
        help+="-- Purpose : realtime watch to an address or a veriable. value is displayed as decimal"
    elif ano == "@watch_bin":
        help+="address|variableName|token (label)\n"
        help+="Example :\n  ;"+ano+" PORTA test\n\n"
        help+="-- Purpose : realtime watch to an address or a veriable. value is displayed as binary"
    elif ano == "@watch_hex":
        help+="address|variableName|token (label)\n"
        help+="Example :\n  ;"+ano+" PORTA test\n\n"
        help+="-- Purpose : realtime watch to an address or a veriable. value is displayed as hexadecimal"

    elif ano == "@mpd":
        help+="label pin_xx\n"
        help+="or\n  var bit b1 is pin_xx ;"+ano+" label\n\n"
        help+="Example :\n  ;"+ano+" my_button pin_b0\n"
        help+="-- Purpose : Momentary Pull-Down button (button press produce a high value)"
    elif ano == "@mpu":
        help+="label pin_xx\n"
        help+="or\n  var bit b1 is pin_xx ;"+ano+" label\n\n"
        help+="Example :\n  ;"+ano+" my_button pin_b0\n"
        help+="-- Purpose : Momentary Pull-Up button (button press produce a low value)"
    elif ano == "@ppd":
        help+="label pin_xx\n"
        help+="or\n  var bit b1 is pin_xx ;"+ano+" label\n\n"
        help+="Example :\n  ;"+ano+" my_button pin_b0\n"
        help+="-- Purpose : Permanent Pull-Down button (button press produce a high value)"
    elif ano == "@ppu":
        help+="label pin_xx\n"
        help+="or\n  var bit b1 is pin_xx ;"+ano+" label\n\n"
        help+="Example :\n  ;"+ano+" my_button pin_b0\n"
        help+="-- Purpose : Permanent Pull-Up button (button press produce a low value)"
    elif ano == "@pot":
        help+="label pin_xx\n"
        help+="or\n  var bit b1 is pin_xx ;"+ano+" label\n\n"
        help+="Example :\n  ;"+ano+" my_button pin_b0\n"
        help+="-- Purpose : Potentiometer (for interaction with the Analog/Digital Converter)"
    #
    elif ano == "@lcd4bit":
        help+="address(,nb_char) (label)"
    elif ano == "@dual7seg":
        help+="address,resetBit,digit1Bit,digit2Bit (label)"
    elif ano == "@upDownCounter":
        help+="address,enable_bit,impulsion_bit,up_down_bit,max_value (label)\n"
        help+="for up_down_bit : up is high, down is low"
    elif ano == "@midiSender":
        help+="(take no parameter) "
    elif ano == "@asciiSender":
        help+="(take no parameter) "
    elif ano == "@byteSender":
        help+="(take no parameter) "
    elif ano == "@uartReceiver":
        help+="(take no parameter) "
    elif ano == "@asciiReceiver":
        help+="(take no parameter) "
        
    # debug
    elif ano == "@reg_filter":
        help+="expression\n"
        help+="Example :\n  ;@reg_filter b:30..35,h:40*2,50,51\n"
        
    elif ano == "@var_filter":
        help+="expression\n"
        help+="Example :  \n;@var_filter var1,h:var2"
        
    elif ano == "@no_debug_all":
        help+="(take no parameter) "
        
    elif ano == "@use_virtual_delay":
        help+="(take no parameter) \n"
        help+="-- For simulation optimization reason, tells Picshell to simulate delays in python rather than in assembler\n"
        help+="-- Only delay in files 'delay_any_mc.jal' and 'extradelay.jal' are optimized\n"
        help+="-- Optimization is achieved using a lib path trick which use 'fake' delay files.\n"
        
    elif ano == "@debug":
        help+="library\n"
        help+="or\n  include libray ;"+ano
    elif ano == "@no_debug":
        help+="library\n"
        help+="or\n  include libray ;"+ano
    
    elif ano == "@led" or ano.startswith("@led_"):
        help+="ADDRESS:bit (label)\n"
        help+="or\n  ;"+ano+" pin_xx (label)\n\n"
        help+="Example :\n\t;@led_red PORTB:5\n"
        help+="\t;@led_green 0x7:5 label\n"
        help+="\t;@led_blue pin_a0 label\n"
    elif ano == "@labelIn":
        help+="text\n"
        help+="\n -- put a label in the 'in' column"
        
    elif ano == "@labelOut":
        help+="text\n"
        help+="\n -- put a label in the 'out' column"
    
        
    print ano    
    return help


class AsmDocHelp :
    def __init__(self):
        pass
    @staticmethod
    def _commonBCF_BSF(help,inst,state):
        # AF FIXME, use address lookup from pic rather than format
        # AF FIXME help += "reg["+str(inst.value)+"] = "+Format.binfx(state.regRead(inst.value),inst.bit)+"\n"
        if Format.spAdrReg.has_key(inst.value):
            help+="reg["+str(inst.value)+"] is the "+Format.spAdrReg[inst.value]+" register\n"
            #status
            if (inst.value==3 and state.bank()==0):
                pass
            #status
            if (inst.value==10 and state.bank() == 0):
                if inst.bit == 3 or inst.bit == 4 :
                    help +="bit 4:3 of PCLATH are used to compute the whole address for CALL and GOTO Instruction\n"
                if inst.bit < 5 :
                    help +="bit 4:0 of PCLATH are used to compute the whole address when PCL is modified (COMPUTED GOTO)\n"        
        return help    
    
    @staticmethod
    def getAsmDescriptionHelp(inst,state):
        help = Format.formatInstruction(inst, 0, False)+"\n\n"
        if (inst.model.mnemonic == "BCF"):
            help += "Action : clearing bit : "+str(inst.bit)+" for register number "+str(inst.value)+" [bank="+str(state.bank())+"]\n\n";
            help += AsmDocHelp._commonBCF_BSF(help,inst,state)
        elif (inst.model.mnemonic == "BSF"):
            help += "Action : setting bit : "+str(inst.bit)+" for register number "+str(inst.value)+" [bank="+str(state.bank())+"]\n\n";
            help += AsmDocHelp._commonBCF_BSF(help,inst,state)
        elif (inst.model.mnemonic == "GOTO") or (inst.model.mnemonic == "CALL"):
            help+="address is computed as follow : \n"
            pclath43 = state.absreg(10);
            #pclath43="00011000" #for test
            pclath43 = Format.bin(pclath43)
            pclath43 = pclath43[3:5];
            help+="[PCLATH<4:3>][Opcode<10:0>]\n"
            help+="["+pclath43+"]["+Format.bin10(inst.value)+"]\n"
            help+= str(int(pclath43+Format.bin10(inst.value),2))+"\n"
            help+="\nThis help panel is still under constrution...\n\n"
        return help
    
    @staticmethod
    def getAsmBeforeExecutionHelp(inst,state):
        help ="Before : \n"
        if (inst.model.mnemonic == "RLF"):
            help+=""
        elif (inst.model.mnemonic == "SUBWF"):
            help+=""
        help+="\n"
        return help
    
    @staticmethod
    def getAsmAfterExecutionHelp(inst,state):
        help ="After : \n"
        if (inst.model.mnemonic == "RLF"):
            help+=""
        elif (inst.model.mnemonic == "SUBWF"):
            help+=""
        help+="\n"
        return help