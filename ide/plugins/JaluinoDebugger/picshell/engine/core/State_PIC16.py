from picshell.engine.util.Format import Format
from picshell.engine.core.PicBuilder_PIC16 import PicBuilder_PIC16

#
# PIC_16 State Implementation
#

class State_PIC16:
    
    
    ADCON0 = 0x1F # in bk 0
    ADCON1 = 0x1F # in bk 1
    ADRESH = 0x1E # in bk 0
    ADRESL = 0x1E # in bk 1
    
    spAdrReg ={}
 
    
    def __init__(self, pic ):
        self.pic = pic
        
        self.spAdrReg ={}
        for reg_key in pic.fsr_regs.keys():
           self.spAdrReg[ pic.fsr_regs[ reg_key ] ] = reg_key

        
        self.w=0 # the w register 

        self.bk = [0]* ((0xFFF)) # int[] internal registers (16 banks)
        self.accessMap = [0]* ((0xFF)) # int[] internal registers (16 banks)
        self.cycles = 0
               
        # not all PICs have eeprom, so check if var does exist in the PIC definition
        try:
           if hasattr( pic, "eeprom_size" ):
              self.eeprom_size = pic.eeprom_size
              self.eeData = [0]*pic.eeprom_size
              self.EECON1 = pic.fsr_regs["EECON1"]
              self.EECON2 = pic.fsr_regs["EECON2"]
              self.EEADR = pic.fsr_regs["EEADR"]

              self.EEADR = pic.fsr_regs["EEADR"]
              self.EEDATA = pic.fsr_regs["EEDATA"]
              
              if pic.fsr_regs.has_key( "EEADRH" ):
                 self.EEADRH = self.pic.fsr_regs["EEADRH"]
              else:
                 self.EEADRH = 0xFFFF
                 
              if pic.fsr_regs.has_key( "EEDATH" ):
                 self.EEDATH = self.pic.fsr_regs["EEDATH"]


              #print "EECON1 %04X " % self.EECON1
              #print "EECON2 %04X " % self.EECON2
              
           else:
              self.eeprom_size = 0
              self.eeData = []
              self.EECON1 = 0xFFFF
              self.EECON2 = 0xFFFF
              self.EEADRH = 0xFFFF
              
        except NameError:
           self.eeData = []
           self.EECON1 = 0xFFFF
           self.EECON2 = 0xFFFF


        self.pcstack = [0]*pic.stack_size   # int[] pc stack 
        self.eeWriteStep = 0    # for EECON2 write seq (0x55, 0xAA)
        self.pc = 0            # program counter
        self.level = 0         # pc stack level
        self.monitors = []  # single address monitors
        self.globalWriteMonitors =[] # all addresses monitors    
        self.globalReadMonitors =[] # all addresses monitors    
        self.adc = [0]*8 # adc values, filled by callback pos 0 = AN0, pos1 = AN1 ...
        self.uartProvider = None  
        self.uartReceiver = None
        self.bank_size = 0x100

        self.code_size = self.pic.code_size
         
        self.STATUS = self.pic.fsr_regs["STATUS"]
        self.BSR = self.pic.fsr_regs["BSR"]

        self.TBLPTRL = self.pic.fsr_regs["TBLPTRL"]
        self.TBLPTRH = self.pic.fsr_regs["TBLPTRH"]
        self.TBLPTRU = self.pic.fsr_regs["TBLPTRU"]
        self.TABLAT  = self.pic.fsr_regs["TABLAT"]

        self.FSR0L = self.pic.fsr_regs["FSR0L"]
        self.FSR0H = self.pic.fsr_regs["FSR0H"]
        self.FSR1L = self.pic.fsr_regs["FSR1L"]
        self.FSR1H = self.pic.fsr_regs["FSR1H"]
        self.FSR2L = self.pic.fsr_regs["FSR2L"]
        self.FSR2H = self.pic.fsr_regs["FSR2H"]


        if pic.fsr_regs.has_key( "PIR1" ):
           self.PIR1 = self.pic.fsr_regs["PIR1"]
        else:
           self.PIR1 = 0xFFFF

        self.PCL = self.pic.fsr_regs["PCL"]
        self.PCLATH = self.pic.fsr_regs["PCLATH"]
        self.PCLATU = self.pic.fsr_regs["PCLATU"]

        if pic.fsr_regs.has_key( "INTCON" ):
           self.INTCON = self.pic.fsr_regs["INTCON"]
        else:
           self.INTCON = 0xFFFF

        if pic.fsr_regs.has_key( "FSR" ):
           self.FSR = self.pic.fsr_regs["FSR"]
        else:
           self.FSR = 0xFFFF

        if pic.fsr_regs.has_key( "INDF0" ):
           self.INDF0 = self.pic.fsr_regs["INDF0"]
        else:
           self.INDF0 = 0xFFFF
        
        if pic.fsr_regs.has_key( "INDF1" ):
           self.INDF1 = self.pic.fsr_regs["INDF1"]
        else:
           self.INDF1 = 0xFFFF

        if pic.fsr_regs.has_key( "INDF2" ):
           self.INDF2 = self.pic.fsr_regs["INDF2"]
        else:
           self.INDF2 = 0xFFFF

        self.port_names = []
        self.port_addr  = []
        self.lat_addr  = []
        self.tris_addr = []

        for portID in range( ord("A"),ord("L") ):
           portName = "PORT" + chr( portID )
           trisName = "TRIS" + chr( portID )
           latName  = "LAT" + chr( portID )
           
           if pic.fsr_regs.has_key( portName )  and pic.fsr_regs.has_key( trisName ) and pic.fsr_regs.has_key( latName ) :
              self.port_addr.append( self.pic.fsr_regs[ portName ] )
              self.tris_addr.append( self.pic.fsr_regs[ trisName ] )
              self.lat_addr.append( self.pic.fsr_regs[ latName ] )
              self.port_names.append( portName )
              # print "ADDING PORT " + portName + "  %04X " % self.pic.fsr_regs[ portName ] + "  %04X " % self.pic.fsr_regs[ trisName ]

        if pic.fsr_regs.has_key( "RCREG" ):
           self.RCREG = self.pic.fsr_regs["RCREG"]
        else:
           self.RCREG = 0xFFFF

        if pic.fsr_regs.has_key( "TXREG" ):
           self.TXREG = self.pic.fsr_regs["TXREG"]
        else:
           self.TXREG = 0xFFFF

        
        self.builder = PicBuilder_PIC16()
        
        self.bankValue = 0

        # 32 byte flash holding register
        self.flash_holding = [0] * 32
        for i in range (0x00, len( self.flash_holding )):
             self.flash_holding[i] = 0xFF


        # init active memory banks (bank 0..7)
        for i in range (0x00, 0xFFF):
             self.bk[i] = 0xFF
             
        # init special purpose regs (from F60 )
        for i in range (0xF60, 0xFFF):
             self.bk[i] = 0x00
             
        # setup access map (0..5F maps to bank 0, 60..FF maps to bank 15)
        for i in range (0, 0xFF):
        	if i < 0x60:
        		self.accessMap[i] = 0x000 + i
        	else:
        		self.accessMap[i] = 0xF00 + i
      	             
        # init eeprom
        for i in range (0,len(self.eeData)):
            self.eeData[i] = 0xFF  
        
        # init TRIS
        for reg in self.tris_addr:
            self.bk[ reg ] = 0xFF
            
        # init PORT
        for reg in self.port_addr:
            self.bk[ reg ] = 0xFF

        # init LAT
        for reg in self.lat_addr:
            self.bk[ reg ] = 0xFF

        self.bk[ self.BSR ] = 0x00


    def Cycles(self,cycles):
       self.cycles = self.cycles + cycles
    def GetCycles(self):
       return self.cycles
         
    def getW(self):
        return self.w

    def getStatus(self):
        return self.bk[self.STATUS]
   
    def setW(self,w):
        self.w = w;
    
    #  7 6 5 4  3 2     1   0
    #  x x x N OV Z  DC(1) C(2)
    #                       1 (FE)       
    #                   2 (FD)
    #              4 (FB)
    #           8 (F7)
    #        10 (EF)


    def SetStatusNZ(self, value ):
       # mask 11101011
       new_stat = ( self.bk[self.STATUS] &  0xEB )
         
       # update Z
       if ( value == 0  ):
          new_stat = new_stat | 0x04

       # update N
       if ( ( value & 0x80 ) != 0):
          new_stat = new_stat | 0x10

       self.regWrite( self.STATUS, new_stat, True)
    
    
    def SetStatusForAdd(self, new_value, src1, src2):
    
       new_stat = ( self.bk[self.STATUS] &  0xE0 )
       
         
       # update C
       if ( (new_value & 0x100) != 0 ):
          new_stat = new_stat | 0x01

       # update DC
       if ( ( ( ( new_value ^ src1 ) ^ src2 ) &0x10 ) != 0 ):
          new_stat = new_stat | 0x02

       # update Z
       if ( (new_value & 0xff ) == 0 ):
          new_stat = new_stat | 0x04

       # update OV
       if (  ( ( new_value ^ src1 )  & 80)  != 0 ):
          new_stat = new_stat | 0x08


       # update N
       if ( (new_value & 0x80) != 0 ):
          new_stat = new_stat | 0x10
		
       self.regWrite( self.STATUS, new_stat, True)


    def SetStatusForSubtract(self, new_value, src1, src2):
    
       # print "Set status for Sub %03X " % new_value + " %02X " % src1 + " %02X " % src2
       new_stat = ( self.bk[self.STATUS] &  0xE0 )
       
         
       # update C
       if ( (new_value & 0x100) == 0 ):
          new_stat = new_stat | 0x01

       # update DC
       if ( ( ( ( new_value ^ src1 ) ^ src2 ) &0x10 ) == 0 ):
          new_stat = new_stat | 0x02

       # update Z
       if ( (new_value & 0xff ) == 0 ):
          new_stat = new_stat | 0x04

       # update OV
       if ( (  ( ( ( src1 & ~src2 )  & ~new_value  ) | 
                 ( new_value & ~src1 & src2    ) ) & 0x80) != 0 ):
          new_stat = new_stat | 0x08


       # update N
       if ( (new_value & 0x80) != 0 ):
          new_stat = new_stat | 0x10
		
       self.regWrite( self.STATUS, new_stat, True)

 
#    value.put((value.get() & ~ (STATUS_Z | STATUS_C | STATUS_DC | STATUS_OV | STATUS_N)) |  
#	      ((new_value & 0xff)   ? 0 : STATUS_Z)   |
#	      ((new_value & 0x100)  ? 0 : STATUS_C)   |
#	      (((new_value ^ src1 ^ src2)&0x10) ? 0 : STATUS_DC) |
#	      ((((src1 & ~src2 & ~new_value) | (new_value & ~src1 & src2)) & 0x80) ? STATUS_OV : 0) |
#	      ((new_value & 0x80)   ? STATUS_N : 0));

    def getC(self):
        return (self.bk[self.STATUS] & 0x01 )>0
    
    def setC(self,c):
         if (c):
             self.regWrite(self.STATUS & 0xFF,self.bk[self.STATUS] | 0x01, True)  # set 
         else:
             self.regWrite(self.STATUS & 0xFF,self.bk[self.STATUS] & 0xFE, True) # clear 

    def getDC(self):
        return (self.bk[self.STATUS] & 0x02 )>0
    
    def setDC(self,n):
         if (n):
             self.regWrite(self.STATUS & 0xFF,self.bk[self.STATUS] | 0x02, True)  # set 
         else:
             self.regWrite(self.STATUS & 0xFF,self.bk[self.STATUS] & 0xFD, True) # clear 

    def getZ(self):
        return (self.bk[self.STATUS] & 0x04)>0
    
    def setZ(self,z):
        if (z):
            self.regWrite(self.STATUS & 0xFF, self.bk[self.STATUS] | 0x04, True)  # set
        else:
            self.regWrite(self.STATUS & 0xFF ,self.bk[self.STATUS] & 0xFB, True)  # clear


    def getOV(self):
        return (self.bk[self.STATUS] & 0x08 )>0
    
    def setOV(self,n):
         if (n):
             self.regWrite(self.STATUS & 0xFF,self.bk[self.STATUS] | 0x08, True)  # set 
         else:
             self.regWrite(self.STATUS & 0xFF,self.bk[self.STATUS] & 0xF7, True) # clear 
    
    def getN(self):
        return (self.bk[self.STATUS] & 0x10 )>0
    
    def setN(self,n):
         if (n):
             self.regWrite(self.STATUS & 0xFF,self.bk[self.STATUS] | 0x10, True)  # set 
         else:
             self.regWrite(self.STATUS & 0xFF,self.bk[self.STATUS] & 0xEF, True) # clear 
    
    
    def setLFSR( self, ff, value ):
        # print "setLFSR: %d " % ff + " to value %04X" % value
    
        if (ff == 0):
            self.regWrite( self.FSR0L, value & 0xFF )
            self.regWrite( self.FSR0H, (value >> 8 ) & 0x0F )            
        elif (ff== 1):
            self.regWrite( self.FSR1L, value & 0xFF )
            self.regWrite( self.FSR1H, (value >> 8 ) & 0x0F )            
        elif (ff== 2):
            self.regWrite( self.FSR2L, value & 0xFF )
            self.regWrite( self.FSR2H, (value >> 8 ) & 0x0F )            
        else:
            print "ERROR: setLFSR, Unknown FSR register %d " , ff
    
    #
    # write to register
    #
    def regWrite(self, reg, value, access = False):
        value = value & 0xFF
        in_value = value
        port_addr = 0xFFFF
        pclModified = False
        
        bank = self.bank()
        
        if ( access ):
           reg = reg & 0xFF
           abs_addr = self.accessMap[reg]

           if ( abs_addr == self.INDF0 ) :
              #print "REGWRITE ACCESS INDFO " + "%02X" % reg + " ABS ADDR " + "%03X" % abs_addr + " to value "+ "%02X" % value
              self.bk[ abs_addr ] = value
              abs_addr = ( self.bk[ self.FSR0H ] << 8 ) + self.bk[ self.FSR0L ]
               
           elif ( abs_addr == self.INDF1 ) :
              # print "REGWRITE ACCESS INDF1 " + "%02X" % reg + " ABS ADDR " + "%03X" % abs_addr + " to value "+ "%02X" % value
              self.bk[ abs_addr ] = value
              abs_addr = ( self.bk[ self.FSR1H ] << 8 ) + self.bk[ self.FSR1L ]
           elif ( abs_addr == self.INDF2 ) :
              #print "REGWRITE ACCESS INDF2 " + "%02X" % reg + " ABS ADDR " + "%03X" % abs_addr + " to value "+ "%02X" % value
              self.bk[ abs_addr ] = value
              abs_addr = ( self.bk[ self.FSR2H ] << 8 ) + self.bk[ self.FSR2L ]

           #print "REGWRITE ACCESS " + "%02X" % reg + " ABS ADDR " + "%03X" % abs_addr + " to value "+ "%02X" % value
           self.bk[ abs_addr ] = value
           
        else:
           # TODO: check bank range
           abs_addr = ( self.bank() * self.bank_size ) + reg
           self.bk[ abs_addr ] = value
           #print "REGWRITE BSR " + " bank: %02X " % self.bank() + " reg: %02X" % reg + " ABS ADDR " + "%04X" % abs_addr + " to value "+ "%02X" % value
    
        # check if this is a LAT register, if so, take TRIS bits into account
        # i.e. don't change the bits that are set to output
        for i in range( 0, len( self.lat_addr) ) :
           if self.lat_addr[i] == abs_addr:

              port_addr = self.port_addr[i] 
              tris = self.bk[ self.tris_addr[i]] 
              port_value = self.bk[ port_addr ] 
                         		
              # print "WRITE TO LAT REG %02X" % abs_addr + " TRIS =%02X" % tris + " PORT=%02X" % port_value + " NEWVAL %02X" % value
                         
              port_value = port_value & tris
              value = value & (255-tris)
              
              value = value | port_value
              self.bk[ port_addr ] = value
              # print "Write PORT %04X " % port_addr + " value %02X" % value

        #if(abs_addr==self.TXREG):
        #   print "SET TX_REG TO : %02X " % value
        #if(abs_addr==self.STATUS):
        #    print "SET STATUS TO : %02X " % value
        
        #
        # Register has a specific meaning ?
        #    
        if(abs_addr==self.PCL):
            #
            # PCL modified ? i.e computed goto
            # don't use regread, since it will update PCLATH/PCLATU
            pcl = self.bk[ self.PCL ]
            pclatu = ( self.bk[self.PCLATU] ) << 16
            pclath = ( self.bk[self.PCLATH] ) << 8
            jump_addr = pclatu + pclath + pcl 
            #print "COMPUTED GOTO %06X" % jump_addr
            self.setPc( jump_addr /2 )
            
            pclModified = True
        #
        # ADC Simulation
        #
        elif (abs_addr == self.ADCON0) :
            if value&0x4 >0 : # bit2 GO
                #start the conversion
                chanelToRead = (value & 0x38) >> 3 #00XX X000 chs2..chs0
                #print self.bk[self.ADCON1]
                adfm = ((self.bk[self.ADCON1] & 0x80) > 0)
                adrsh = 0
                adrsl = 0
                
                #self.adc is need to be filled by the component (potentiometer) on the ui side 
                if (adfm) :
                    # right justified 6 most significant bit of ADRESH are read as 0
                    adrsh = (self.adc[chanelToRead] >> 8) & 0x03 # only 2 bit
                    adrsl = self.adc[chanelToRead] & 0xFF # 8 bit
                else :
                    # left justified 6 least significant bit of ADRESL are read as 0
                    adrsh = (self.adc[chanelToRead] >> 2) & 0xFF 
                    adrsl = (self.adc[chanelToRead] & 0x03)<< 6 
                    
                self.abswrite(self.ADRESH, adrsh)
                self.abswrite(self.ADRESL, adrsl)
                #self.bk[self.ADRESH] = adrsh
                #self.bk[self.ADRESL] = adrsl
                
                self.bk[self.ADCON0] = value & (0xFF-4) # auto clear bit 2 GO
                
        #
        # EEPROM
        #
        elif (abs_addr==self.EECON2):
           
 		     if ((self.eeWriteStep == 0) and (self.bk[self.EECON2]==0x55)):
		        self.eeWriteStep = self.eeWriteStep +1
		     elif ((self.eeWriteStep == 1) and (self.bk[self.EECON2]==0xAA)):
		        self.eeWriteStep = self.eeWriteStep +1 
		     # print "self.eeWriteStep set to : %d" % self.eeWriteStep
		        
        elif (abs_addr==self.EECON1):
                #
                # DATA EEPROM READ/WRITE
                # very basic impl... yet functional for my needs till now...
                #
                eepgd = (self.bk[self.EECON1] >> 7)&0xFF; # programm or data memory ? (bk3)
                rd = self.bk[self.EECON1]&1
                wr = (self.bk[self.EECON1]&2)>>1
                wren = (self.bk[self.EECON1]&4)>>2
                free = (self.bk[self.EECON1]&10)>>4
                cfgs = (self.bk[self.EECON1]&20)>>6

                if  ( self.EEADRH != 0xFFFF ):
                    eeadr = ( self.bk[ self.EEADRH ] << 8 ) + self.bk[self.EEADR] # get the address(bk2)
                else:
                    eeadr = self.bk[self.EEADR] # get the address(bk2)
                eeadr = eeadr & ( self.eeprom_size - 1 )

                if (eepgd == 0 ):
                    # 0 -> data memory
                    if (rd == 1):
                        # READ
                        self.bk[self.EEDATA]= self.eeData[eeadr] # read eeprom -> data register
                        # print "EEPROM read : %04X" % eeadr + " value %02X" % self.bk[self.EEDATA]
    
                        # RD set back to 0
                        self.bk[self.EECON1] &= 0xFE
                    elif ((wren==1) and (wr == 1) and (self.eeWriteStep==2)):
                        #WRITE
                        self.eeData[ eeadr ] = self.bk[ self.EEDATA ]&0xFF # write
                        # print "EEPROM write : %04X" % eeadr + " value %02X" % self.eeData[ eeadr ]
                        #WR set back to 0
                        self.bk[self.EECON1] &= 0xFD
                        self.eeWriteStep = 0
                else:
                    # program memory
                    tl = self.bk[ self.TBLPTRL ]
                    th = self.bk[ self.TBLPTRH ]
                    tu = self.bk[ self.TBLPTRU ]
                    
                    # tl_masked = tl & 0x
                    taddr = ( tu << 16 ) + ( tu << 8 ) + tl
                    
                    # print " PROGRAM MEMORY %02X" % tu + "%02X" % th + "%02X"% tl

                    # erase 64 block                    
                    if ((wren==1) and (free == 1) and (wr == 1) and (self.eeWriteStep==2)):
                        
                        base_addr = ( taddr & 0xFFFFC0 )
                        
                        print "ERASING FLASH 32 bytes, start at :%06X " % base_addr
                        
                        for addr in range( 0, 32 ):
                            self.writeProgramMem( base_addr + addr,Format.bin( 0xFFFF ) )

                        #WR set back to 0
                        self.bk[self.EECON1] &= 0xFD
                        self.eeWriteStep = 0 
                        
                    # write block of 32 bytes
                    elif ((wren==1) and (wr == 1) and (self.eeWriteStep==2)):
                        print " PROGRAM MEMORY WRITE BLOCK %02X" % tu + "%02X" % th + "%02X"% tl
                        
                        base_addr = ( taddr & 0xFFFFE0 )

                        for addr in range( 0, len(self.flash_holding) / 2 ):
                            data = self.flash_holding[ addr * 2 + 1 ] +  self.flash_holding[ addr * 2 ]
                            self.writeProgramMem( base_addr + addr,Format.bin( data ) )
                            print "WRITING FLASH, addr :%06X " % (base_addr + addr ) + " value " + Format.bin( data ) 
                        
                        #WR set back to 0
                        self.bk[self.EECON1] &= 0xFD
                        self.eeWriteStep = 0
                    
        # update monitors, have to update both LAT and port registers if applicable
        for monitor in self.monitors:
           if (monitor.address == abs_addr):
              monitor.execute(in_value);
           if (monitor.address == port_addr):
              monitor.execute(value);
              
        for monitor in self.globalWriteMonitors:
           monitor.execute(abs_addr,in_value,self);   
           if port_addr != 0xFFFF:
              monitor.execute(port_addr,value,self);   
                   
        return pclModified
 
    #
    # Register read
    #
    def regRead(self,reg, access = False ):
        
        # hack to unlock ADCON0:G0
        #if (reg == 0x1F):
        #    self.bk[0x1F] = self.bk[0x1F] &(255-4) # force ADCON:GO ( bit 2) to 0

        #
        # Register has a specific meaning ?
        #    
        if(reg==self.PCL):
            #
            # PCL modified ? i.e computed goto, update PCLATU & PCLATH values
            self.bk[ self.PCLATH ] = ( ( self.pc >> 8  ) & 0xFF )
            self.bk[ self.PCLATU ] = ( ( self.pc >> 16 ) & 0x1F )


        if ( access ):
           reg = reg & 0xFF
           abs_addr = self.accessMap[reg]
        else:
           abs_addr = ( self.bank() * self.bank_size ) + reg
           #print "REGREAD BSR " + " bank: %02X " % self.bank() + " reg: %02X" % reg + " ABS ADDR " + "%03X" % abs_addr + " to value "+ "%02X" % self.bk[ abs_addr ] 

        
        if ( abs_addr == self.INDF0 ) :
           #print "REGREAD ACCESS INDFO " + "%02X" % reg + " ABS ADDR " + "%03X" % abs_addr + " to value "+ "%02X" % value
           abs_addr = ( self.bk[ self.FSR0H ] << 8 ) + self.bk[ self.FSR0L ]
            
        elif ( abs_addr == self.INDF1 ) :
           #print "REGREAD ACCESS INDF1 " + "%02X" % reg + " ABS ADDR " + "%03X" % abs_addr + " to value "+ "%02X" % value
           abs_addr = ( self.bk[ self.FSR1H ] << 8 ) + self.bk[ self.FSR1L ]
        elif ( abs_addr == self.INDF2 ) :
           #print "REGWREAD ACCESS INDF2 " + "%02X" % reg + " ABS ADDR " + "%03X" % abs_addr + " to value "+ "%02X" % value
           abs_addr = ( self.bk[ self.FSR2H ] << 8 ) + self.bk[ self.FSR2L ]

        retValue = self.bk[ abs_addr ]
        #print "REGREAD " + "%02X" % reg + " ABS ADDR " + "%03X" % abs_addr + "  value "+ "%02X" % retValue

        if ( self.PIR1 == abs_addr ): 
	      
           data = self.bk[ self.PIR1 ]
           # print "PIR1 content is %02X" % data
	            
           if self.uartProvider != None and  self.uartProvider.hasData() :
              data = data | 32 # set RCIF flag
              
           if self.uartReceiver != None and  self.uartReceiver.isReady() :
              data = data | 16 # set TXIF flag
           
           # print "PIR1 retValue %02X" % data
           return data

	        
        elif ( self.RCREG == abs_addr ):
           retValue = self.bk[ self.RCREG ]  
           if self.uartProvider != None and  self.uartProvider.hasData() :
              retValue =  self.uartProvider.getNext()          
              self.bk[ self.RCREG ] = retValue
        
        # check if this is a PORT register, if so, take TRIS bits into account
        # i.e. don't change the bits that are set to output
        for i in range( 0, len( self.port_addr) ) :
           if self.port_addr[i] == abs_addr:
              for monitor in self.globalReadMonitors:
                 retValue = monitor.execute(reg,self,retValue); # will be updated by the monitor
                                                          # used for external device like buttons, switch...
                                                          # these external register have no callback, so I must
                                                          # update reg when I discover the change ... i.e when I read
                                                          # the port the device is on...
                 self.regWrite(abs_addr, retValue)        

        return retValue   

    def GetTabLat(self, mode):
       tl = self.bk[ self.TBLPTRL ]
       th = self.bk[ self.TBLPTRH ]
       tu = self.bk[ self.TBLPTRU ]

       #print " TABLAT %02X"% tu + "%02X"% th + "%02X"% tl

       
       # pre increment
       if mode == 2:
           tl = tl + 1
           if tl > 255:
              tl = 0
              th =  th + 1
           if th > 255:
              th = 0
              tu =  tu + 1
       if mode == 4:
           tl = tl - 1
           if tl == -1:
              tl = 255
              th =  th - 1
           if th == -1:
              th = 255
              tu =  tu - 1

       # note, program memory is organized in bytes, so divide by two
       tptr = ( ( tu << 16 ) + ( th << 8 ) + tl ) >> 1

       #print "GetTabLat tptr %08X " % tptr
       
       (dataH,dataL) = self.readProgramMem( tptr, True )
       #print "GetTabLat %08X " % tptr + " %02X" % dataH + " %02X" % dataL
       
       if ( tl & 0x01 ) == 1:
          ret = dataH
       else:
          ret = dataL

       # post increment
       if mode == 1:
           tl = tl + 1
           if tl > 255:
              tl = 0
              th =  th + 1
           if th > 255:
              th = 0
              tu =  tu + 1
       if mode == 3:
           tl = tl - 1
           if tl == -1:
              tl = 255
              th =  th - 1
           if th == -1:
              th = 255
              tu =  tu - 1
              
       self.bk[ self.TBLPTRL ] = tl
       self.bk[ self.TBLPTRH ] = th
       self.bk[ self.TBLPTRU ] = tu
       self.bk[ self.TABLAT  ] = ret
        
       return ret       	

    def SetTabLat(self, mode ):
       tl = self.bk[ self.TBLPTRL ]
       th = self.bk[ self.TBLPTRH ]
       tu = self.bk[ self.TBLPTRU ]

       # print " TABLAT WRITE %02X "% tl + "%02X "% th + "%02X "% tu
       
       # pre increment
       if mode == 2:
           tl = tl + 1
           if tl > 255:
              tl = 0
              th =  th + 1
           if th > 255:
              th = 0
              tu =  tu + 1
       if mode == 4:
           tl = tl - 1
           if tl == -1:
              tl = 255
              th =  th - 1
           if th == -1:
              th = 255
              tu =  tu - 1

       # note, program memory is organized in bytes, so divide by two
       tptr = ( ( tu << 16 ) + ( th << 8 ) + tl ) >> 1

       # print "GetTabLat tptr %08X " % tptr
       
       value = self.bk[ self.TABLAT  ]
       self.flash_holding[ tl & (len( self.flash_holding ) -1 ) ] = value 
       
       # print "SetTabLat flash_holding %d " % ( tl & 0x1F ) " set to %02X" % value
       
       # post increment
       if mode == 1:
           tl = tl + 1
           if tl > 255:
              tl = 0
              th =  th + 1
           if th > 255:
              th = 0
              tu =  tu + 1
       if mode == 3:
           tl = tl - 1
           if tl == -1:
              tl = 255
              th =  th - 1
           if th == -1:
              th = 255
              tu =  tu - 1
              
       self.bk[ self.TBLPTRL ] = tl
       self.bk[ self.TBLPTRH ] = th
       self.bk[ self.TBLPTRU ] = tu

    
    # very specific use,
    # try to use regRead instead
    # Register read (with no bank handeling)
    #
    def absreg(self, reg):
        value = self.bk[reg]
        #if reg in (5,6,7,8,9) and len(self.globalReadMonitors)>0 : # for devices...
        #    for monitor in self.globalReadMonitors:
        #        value = monitor.execute(reg,self,value); 
        #        self.abswrite(reg, value)
        return value
    
    # very specific use,
    # try to use regWrite instead 
    #
    def abswrite(self, reg,value):
        value = value & 0xFF
        self.bk[reg] = value
        
        #
        # watching any register ?
        #
        
        for monitor in self.monitors:
            if (monitor.address == reg):
                monitor.execute(value);
                
        for monitor in self.globalWriteMonitors:
            monitor.execute(reg,value,self); 
    
    
    #
    # BANK 
    #
    def bank(self):
        return self.bk[ self.BSR ] 
    def SetBank(self, bankValue ):
        # AF TODO check range
        self.bk[ self.BSR ] = bankValue
    
    #
    # internal PC 
    #
    #    
    def getPc(self):
        return self.pc
    
    def setPc(self,i):
        self.pc = i
        #print "Set PC %08X" % self.pc
        # print "Set PCL reg %02X with content" % self.PCL 
        # print "%02X" % self.bk[ self.PCL ]
        self.bk[self.PCL]=(self.pc+1)&0xFF
    
    def incPc(self):
        self.setPc( self.pc + 1 )
    
    #
    # compute next pc for Goto and Call regarding to pclath 
    #
    def changePcForCallGoto(self, addr):
        # print "GOTO ADDRESS " + "%06X" % addr 
        self.setPc( addr / 2 )
    
    #
    # Usefull for Stats
    #
    def getMonitors(self):
        return self.monitors

    def setMonitors(self, monitors):
        self.monitors = monitors

        for mon in monitors:
           m = getattr(mon, 'setPic', None)
           if callable(m):
              m( self.pic )
              
    def appendMonitor(self, monitor):
        self.monitors.append( monitor )
        m = getattr(monitor, 'setPic', None)
        if callable(m):
           m( self.pic )

    
    def setMonitors(self,monitors):
        self.monitors = monitors
    
    def getLevel(self):
        return self.level;
    
    def setLevel(self,i):
        self.level = i;
    
    def pushStack(self):
        self.pcstack[self.level] = self.getPc()
        self.level = self.level + 1
        if (self.level == 8):
            self.level = 0
    
    def popStack(self):
        self.level = self.level -1
        if (self.level < 0):
            self.level = 7
        return self.pcstack[self.level]

    # bit must be in the form bit0 -> 1
    # bit1 -> 2
    # bit2 -> 4
    # bit3 -> 8
    # ...
    def isOutput(self,port,bit):
        return ((self.bk[0x80+port] & bit) >0)
        
    def getBuilder(self):
        return self.builder; # 14 bit Builder
    