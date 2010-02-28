from picshell.engine.util.Format import Format
from picshell.engine.util import BitUtil
from picshell.engine.core.Inst import Inst


#
# 14 and 16 bit Mnemonic set
#

# http://p.may.chez-alice.fr/instructions2.html

def ADDLW( st, inst):
    
    # get source registers
    src1 = inst.value 
    src2 = st.getW()
    
    # calculate result
    new_value = src1 + src2


    # write result before status update
    st.setW( new_value & 0xFF ) 

    # update status flags
    st.SetStatusForAdd( new_value, src1, src2 )
    
    st.Cycles(1)
    
    return False

def ADDWF(st, inst):
    pclModified = False
    
    # get source registers
    src1 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    src2 = st.getW()
    
    # calculate result
    new_value = src1 + src2


    # write result before status update
    if ( inst.dest == Inst.DEST_W ):
        st.setW( new_value & 0xFF ) 
    elif (inst.dest == Inst.DEST_F) :
        pclModified = st.regWrite(inst.value, ( new_value & 0xFF ), inst.access == Inst.ACCESS_RAM )

    # update status flags
    st.SetStatusForAdd( new_value, src1, src2 )

    st.Cycles(1)
    
    return pclModified
 

def ADDWFC(st, inst):
    pclModified = False
    
    # get source registers
    src1 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    src2 = st.getW()
    
    # calculate result
    if st.getC() :
       new_value = src1 + src2 + 1
    else:
       new_value = src1 + src2


    # write result before status update
    if ( inst.dest == Inst.DEST_W ):
        st.setW( new_value & 0xFF ) 
    elif (inst.dest == Inst.DEST_F) :
        pclModified = st.regWrite(inst.value, ( new_value & 0xFF ), inst.access == Inst.ACCESS_RAM )

    # update status flags
    st.SetStatusForAdd( new_value, src1, src2 )

    st.Cycles(1)
    
    return pclModified
 

def ANDLW( st,  inst):
    k = inst.value
    w = st.getW() & k
    w=w&255
    st.setW(w)
    st.SetStatusNZ( w )
    st.Cycles(1)
    return False
 
def BCF( st,  inst) :
    newVal = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) & inst.inv_bit   
    st.Cycles(1)
    return  st.regWrite(inst.value, newVal, inst.access == Inst.ACCESS_RAM )

def BSF( st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    bit = 1
    bit = bit << inst.bit
    val = val | bit
    pclModified = st.regWrite(inst.value,val, inst.access == Inst.ACCESS_RAM )
    st.Cycles(1)
    return pclModified

def BTFSC(  st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    bval = inst.bit
    # print "BTFSC %02X" % val + " bit %02X", bval
    if (BitUtil.isClear(val, bval)):
        st.incPc() # skip next
        st.Cycles(2)
    else:
        st.Cycles(1)
        
    return False

def BTFSS( st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    bval = inst.bit
    	
    # print "BTFSS val %02X" % val + " bval %d " % bval
    if (BitUtil.isSet(val, bval)):
        # print "BTFSS skip"
        st.incPc() # skip next
        st.Cycles(2)
    else:
        st.Cycles(1)
    return False

def CALL( st,  inst):
    st.pushStack()
    #print "call %08X" % inst.value
    st.changePcForCallGoto(inst.value)
    st.Cycles(2)
    return True


def CLRF( st,  inst):
    pclModified = st.regWrite(inst.value, 0, inst.access == Inst.ACCESS_RAM )
    st.setZ(True)
    st.Cycles(1)
    return pclModified


def DECF( st,  inst):
    pclModified = False
    
    # get source registers
    src1 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    src2 = 1
    
    # calculate result
    new_value = src1 - src2


    # write result before status update
    if ( inst.dest == Inst.DEST_W ):
        st.setW( new_value & 0xFF ) 
    elif (inst.dest == Inst.DEST_F) :
        pclModified = st.regWrite(inst.value, ( new_value & 0xFF ), inst.access == Inst.ACCESS_RAM )

    # update status flags
    st.setZ( new_value == 0 )
    
    st.Cycles(1)
    return pclModified
 
def DECF16( st,  inst):
    pclModified = False
    
    # get source registers
    src1 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    src2 = 1
    
    # calculate result
    new_value = src1 - src2


    # write result before status update
    if ( inst.dest == Inst.DEST_W ):
        st.setW( new_value & 0xFF ) 
    elif (inst.dest == Inst.DEST_F) :
        pclModified = st.regWrite(inst.value, ( new_value & 0xFF ), inst.access == Inst.ACCESS_RAM )

    # update status flags
    st.SetStatusForSubtract( new_value, src1, src2 )
    
    st.Cycles(1)
    return pclModified


    
def DECFSZ( st,  inst):
    val = (st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) - 1) & 0xff
    pclModified = st.regWrite(inst.value, val, inst.access == Inst.ACCESS_RAM )
    if (val == 0):
        st.incPc()
        st.Cycles(2)
    else:
        st.Cycles(1)
                
    return pclModified

def DCFSNZ( st,  inst):
    val = (st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) - 1) & 0xff
    pclModified = st.regWrite(inst.value, val, inst.access == Inst.ACCESS_RAM )
    if (val != 0):
        st.incPc()
    st.Cycles(1)
    return pclModified

    
def GOTO( st,  inst):
    st.changePcForCallGoto(inst.value)
    st.Cycles(2)
    return True
    

def INCF( st,  inst):
    pclModified = False
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    res = val + 1
    res = res & 0xff # convert to unsigned byte
    st.setZ((res == 0))
    
    if (inst.dest == Inst.DEST_W):
        st.setW(res) 
    elif (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    st.Cycles(1)
    return pclModified
 
def INCF16( st,  inst):
    pclModified = False
    
    # get source registers
    src1 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    src2 = 1
    
    # calculate result
    new_value = src1 + src2

    # write result before status update
    if ( inst.dest == Inst.DEST_W ):
        st.setW( new_value & 0xFF ) 
    elif (inst.dest == Inst.DEST_F) :
        pclModified = st.regWrite(inst.value, ( new_value & 0xFF ), inst.access == Inst.ACCESS_RAM )

    # update status flags
    st.SetStatusForAdd( new_value, src1, src2 )
    st.Cycles(1)
    
    return pclModified

    
def IORLW( st,  inst):
    k = inst.value
    w = st.getW() | k
    w = w&0xff
    st.SetStatusNZ( w )
    st.setW(w)
    st.Cycles(1)
    return False

    
def IORWF( st,  inst):
    pclModified = False
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    res = st.getW() | val
    res = res & 0xff # convert to unsigned byte
    
    if (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    elif (inst.dest == Inst.DEST_W):
        st.setW(res)
        
    st.SetStatusNZ( res )
    st.Cycles(1)

    return pclModified

    
def MOVF( st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    
    st.SetStatusNZ( val )

    if (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    elif (inst.dest == Inst.DEST_W):
       st.setW(val)
    st.Cycles(1)
    return False

    
def MOVLB( st,  inst):
    st.SetBank(inst.value)
    st.Cycles(1)
    return False

    
def MOVLW( st,  inst):
    st.setW(inst.value)
    st.Cycles(1)
    return False


def MOVWF( st,  inst):
    pclModified = st.regWrite(inst.value,st.getW(), inst.access == Inst.ACCESS_RAM )
    st.Cycles(1)
    return pclModified


def NOP(st,inst):
    st.Cycles(1)
    return False

def NNOP(st,inst):
    st.Cycles(0)
    return False
    
def RETLW( st,  inst):
    pc = st.popStack()
    st.setW(inst.value)
    st.setPc(pc)
    st.Cycles(2)
    return False


def RETURN( st,  inst):
    pc = st.popStack()
    st.setPc(pc)
    st.Cycles(2)
    return False

    
def RLF( st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    res = (val&0xFF)<<1
    pclModified = False
    saveCarry = st.getC()
    st.setC((res > 255))
    res = res & 0xff # convert to unsigned byte
    if(saveCarry):
        res |=1
    
    if (inst.dest == Inst.DEST_W):
        st.setW(res)
    elif (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    st.Cycles(1)
    return pclModified

def RLCF( st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    res = (val&0xFF)<<1
    pclModified = False
    saveCarry = st.getC()
    st.setC((res > 255))
    res = res & 0xff # convert to unsigned byte
    if(saveCarry):
        res |=1
    if (inst.dest == Inst.DEST_W):
        st.setW(res)
    elif (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    
    st.SetStatusNZ( res )
    
    st.Cycles(1)
    return pclModified

def RLNCF( st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    res = (val&0xFF)<<1

    pclModified = False

    res = res & 0xff # convert to unsigned byte

    if (inst.dest == Inst.DEST_W):
        st.setW(res)
    elif (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    
    st.SetStatusNZ( res )
    
    st.Cycles(1)
    return pclModified
        
    
def SLEEP( st,  inst):
    st.Cycles(1)
    return False

    
def SUBLW( st,  inst):
    pclModified = False
    
    # get source registers
    src1 = inst.value
    src2 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    
    # calculate result
    new_value = src1 - src2

    # write result before status update
    st.setW( new_value & 0xFF ) 

    # update status flags
    st.SetStatusForSubtract( new_value, src1, src2 )
    
    st.Cycles(1)
    return pclModified
 
    
def SUBWF( st,  inst):
    pclModified = False
    
    # get source registers
    src1 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    src2 = st.getW()
    
    # calculate result
    new_value = src1 - src2


    # write result before status update
    if ( inst.dest == Inst.DEST_W ):
        st.setW( new_value & 0xFF ) 
    elif (inst.dest == Inst.DEST_F) :
        pclModified = st.regWrite(inst.value, ( new_value & 0xFF ), inst.access == Inst.ACCESS_RAM )

    # update status flags
    st.SetStatusForSubtract( new_value, src1, src2 )
    
    st.Cycles(1)
    return pclModified
 

def SUBWFB( st,  inst):

    pclModified = False
    
    # get source registers
    src1 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    src2 = st.getW()
    
    # calculate result
    if ( st.getC() == 0 ):
	    new_value = src1 - src2 - 1
    else:
	    new_value = src1 - src2

    # write result before status update
    if ( inst.dest == Inst.DEST_W ):
        st.setW( new_value & 0xFF ) 
    elif (inst.dest == Inst.DEST_F) :
        pclModified = st.regWrite(inst.value, ( new_value & 0xFF ), inst.access == Inst.ACCESS_RAM )

    # update status flags
    st.SetStatusForSubtract( new_value, src1, src2 )
    
    st.Cycles(1)
    return pclModified



def SUBFWB( st,  inst):

    pclModified = False
    
    # get source registers
    src1 = st.getW()
    src2 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    
    # calculate result
    if ( st.getC() == 0 ):
	    new_value = src1 - src2 - 1
    else:
	    new_value = src1 - src2

    # write result before status update
    if ( inst.dest == Inst.DEST_W ):
        st.setW( new_value & 0xFF ) 
    elif (inst.dest == Inst.DEST_F) :
        pclModified = st.regWrite(inst.value, ( new_value & 0xFF ), inst.access == Inst.ACCESS_RAM )

    # update status flags
    st.SetStatusForSubtract( new_value, src1, src2 )
    
    st.Cycles(1)
    return pclModified

def SWAPF( st,  inst):
    pclModified = False
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    lowbits = val & 0X0F
    highbits = val & 0XF0
    lowbits = lowbits << 4
    highbits = highbits >> 4
    if (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, lowbits + highbits, inst.access == Inst.ACCESS_RAM )
    elif (inst.dest == Inst.DEST_W) :
        st.setW(lowbits + highbits)
    st.Cycles(1)
    return pclModified
        
    
def CLRWDT( st,  inst):
    st.Cycles(1)
    return False
    
    
def CLRW( st,  inst):
    st.setW(0)
    st.setZ(True)
    st.Cycles(1)
    return False
   
    
def ANDWF( st,  inst):
    pclModified = False
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    res = st.getW() & val
    res = res & 0xff # convert to unsigned byte
    
    if (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    elif (inst.dest == Inst.DEST_W):
        st.setW(res)

    st.SetStatusNZ( res )

    st.Cycles(1)
    return pclModified   
   
    
def COMF( st,  inst):
    pclModified = False
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    res =  val ^0xFF # do the comp (each byte are inverted)
    res = res & 0xff # convert to unsigned byte
    
    if (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    elif (inst.dest == Inst.DEST_W):
        st.setW(res)

    st.SetStatusNZ( res)

    st.Cycles(1)
    return pclModified   
   
    
    
def INCFSZ( st,  inst):
    pclModified = False
    val = (st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) + 1) & 0xff
    if (inst.dest == Inst.DEST_W):
        st.setW(val) 
    elif (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, val, inst.access == Inst.ACCESS_RAM )
    
    if (val == 0):
        st.incPc()
        st.Cycles(2)
    else:
        st.Cycles(1)
    return pclModified

def INCFNSZ( st,  inst):
    pclModified = False
    val = (st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) + 1) & 0xff
    if (inst.dest == Inst.DEST_W):
        st.setW(val) 
    elif (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, val, inst.access == Inst.ACCESS_RAM )
    
    if (val != 0):
        st.incPc()
    st.Cycles(1)
    return pclModified

    
def RRF( st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    nextCarry = val & 1
    res = val>>1
    if (st.getC()):
         res |=128 # bit 7
    if(nextCarry>0):
        st.setC(True)
    else:
        st.setC(False)
    pclModified = False
    res = res & 0xff # convert to unsigned byte
    if (inst.dest == Inst.DEST_W):
        st.setW(res)
    elif (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    st.Cycles(1)
    return pclModified
    
def RRCF( st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    nextCarry = val & 1
    res = val>>1
    if (st.getC()):
         res |=128 # bit 7
    if(nextCarry>0):
        st.setC(True)
    else:
        st.setC(False)
    pclModified = False
    res = res & 0xff # convert to unsigned byte
    if (inst.dest == Inst.DEST_W):
        st.setW(res)
    elif (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    
    st.SetStatusNZ( res )
    st.Cycles(1)
    return pclModified

def RRNCF( st,  inst):
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    nextCarry = val & 1
    res = val>>1

    pclModified = False

    res = res & 0xff # convert to unsigned byte
    if (inst.dest == Inst.DEST_W):
        st.setW(res)
    elif (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    
    st.SetStatusNZ( res )
    st.Cycles(1)
    return pclModified
    
    
def XORLW( st,  inst):
    k = inst.value
    w = st.getW() ^ k

    st.SetStatusNZ( w )

    w = w&255
    st.setW(w&0xFF)
    st.Cycles(1)
    return False

    
def XORWF( st,  inst):
    pclModified = False
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    res = st.getW() ^ val
    # print "XOR W %02X " % st.getW() + " with %02X " %  val + " result %02X " % res 
    res = res & 0xff # convert to unsigned byte
    
    st.SetStatusNZ( res )
    
    if (inst.dest == Inst.DEST_F):
        pclModified = st.regWrite(inst.value, res, inst.access == Inst.ACCESS_RAM )
    elif (inst.dest == Inst.DEST_W):
        st.setW(res)
    st.Cycles(1)
    return pclModified

def TBLRD( st,  inst):
	tablat = st.GetTabLat( 0 ) 
	st.Cycles(1)
	return False

def TBLRD_POSTI( st,  inst):
	tablat = st.GetTabLat( 1 ) 
	st.Cycles(1)
	return False

def TBLRD_PREI( st,  inst):
	tablat = st.GetTabLat( 2 ) 
	st.Cycles(1)
	return False

def TBLRD_POSTD( st,  inst):
	tablat = st.GetTabLat( 3 ) 
	st.Cycles(1)
	return False

def TBLRD_PRED( st,  inst):
	tablat = st.GetTabLat( 4 ) 
	st.Cycles(1)
	return False


def TBLWT( st,  inst):
	st.SetTabLat( 0 ) 
	st.Cycles(1)
	return False

def TBLWT_POSTI( st,  inst):
	st.Cycles(1)
	st.SetTabLat( 1 ) 
	return False

def TBLWT_PREI( st,  inst):
	st.SetTabLat( 2 ) 
	st.Cycles(1)
	return False

def TBLWT_POSTD( st,  inst):
	st.SetTabLat( 3 ) 
	st.Cycles(1)
	return False

def TBLWT_PRED( st,  inst):
	st.SetTabLat( 4  ) 
	st.Cycles(1)
	return False


def CPFSGT( st,  inst):    
    w = st.getW()
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    
    if ( val < w ):
        st.incPc()
        
    st.Cycles(1)
    return False
   
def CPFSLT( st,  inst):    
    w = st.getW()
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    
    if ( val < w ):
        st.incPc()
        
    st.Cycles(1)
    return False
   
def CPFSEQ( st,  inst):    
    w = st.getW()
    val = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM)
    
    if ( val == w ):
        st.incPc()
        
    st.Cycles(1)
    return False
   
def NEGF( st,  inst):    
    pclModified = False
    
    # get source registers
    src1 = st.regRead(inst.value, inst.access == Inst.ACCESS_RAM) 
    
    # calculate result
    new_value = 1 + ~src1

    # write result before status update
    pclModified = st.regWrite(inst.value, ( new_value & 0xFF ), inst.access == Inst.ACCESS_RAM )

    # update status flags
    st.SetStatusForSubtract( new_value, 0, src1 )
    
    st.Cycles(1)
    return pclModified
   
def SETF( st,  inst):    
    st.Cycles(1)
    return st.regWrite(inst.value, 0xFF, inst.access == Inst.ACCESS_RAM )
   
def LFSR( st,  inst):    
    st.setLFSR( inst.dest - Inst.DEST_FSR_0, inst.value )
    st.Cycles(1)
    return False
    