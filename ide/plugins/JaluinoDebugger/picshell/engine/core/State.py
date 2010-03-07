from picshell.engine.util.Format import Format
from picshell.engine.core.PicBuilder import PicBuilder
from array import array

#
# 16F877 State Impl 
#

class State:
    
    
    spAdrReg = {}
    
    def __init__(self, pic):
        self.spAdrReg ={}
        for reg_key in pic.fsr_regs.keys():
           self.spAdrReg[ pic.fsr_regs[ reg_key ] ] = reg_key
        
        self.pic = pic
        self.w=0 # the w register 
        self.bk = [0]* ((0x7F * 4)) # int[] internal registers (4 banks)
        #self.bk = array( 'B', [0]* ((0x7F * 4)) )

        if pic.fsr_regs.has_key( "ADCON0" ):
           self.ADCON0 = self.pic.fsr_regs["ADCON0"]
        else:
           self.ADCON0 = 0xFFFF
        if pic.fsr_regs.has_key( "ADCON1" ):
           self.ADCON1 = self.pic.fsr_regs["ADCON1"]
        else:
           self.ADCON1 = 0xFFFF
        
        if pic.fsr_regs.has_key( "ADRESH" ):
           self.ADRESH = self.pic.fsr_regs["ADRESH"]
        else:
           self.ADRESH = 0xFFFF
        
        if pic.fsr_regs.has_key( "ADRESL" ):
           self.ADRESL = self.pic.fsr_regs["ADRESL"]
        else:
           self.ADRESL = 0xFFFF
        
        # not all PICs have eeprom, so check if var does exist in the PIC definition
        try:
           if hasattr( pic, "eeprom_size" ):
              self.eeprom_size = pic.eeprom_size
              self.eeData = [0]*pic.eeprom_size
              self.EECON1 = pic.fsr_regs["EECON1"]
              self.EECON2 = pic.fsr_regs["EECON2"]
              self.EEADR = pic.fsr_regs["EEADR"]

              self.EEADR = pic.fsr_regs["EEADR"]

              if pic.fsr_regs.has_key( "EEDATA" ):
                  self.EEDATA = pic.fsr_regs["EEDATA"]
              
              if pic.fsr_regs.has_key( "EEDAT" ):
                  self.EEDATA = pic.fsr_regs["EEDAT"]
              
              if pic.fsr_regs.has_key( "EEADRH" ):
                 self.EEADRH = self.pic.fsr_regs["EEADRH"]
              else:
                 self.EEADRH = 0xFFFF
                 
              if pic.fsr_regs.has_key( "EEDATH" ):
                 self.EEDATH = self.pic.fsr_regs["EEDATH"]

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

        self.code_size = self.pic.code_size

        self.pcstack = [0]*pic.stack_size   # int[] pc stack 
        self.eeWriteStep = 0    # for EECON2 write seq (0x55, 0xAA)
        self.pc = 0            # program counter
        self.level = 0         # pc stack level
        self.monitors = []  # single address monitors
        self.globalWriteMonitors =[] # all addresses monitors    
        self.globalReadMonitors =[] # all addresses monitors    
        self.adc = [0]*16 # adc values, filled by callback pos 0 = AN0, pos1 = AN1 ...
        self.uartProvider = None  
        self.uartReceiver = None
        self.builder = PicBuilder()
        self.spAdrReg = []
        self.cur_bank = 0
        self.cycles = 0

        
        # determine bank size from INDF shadow registers	
        try:		
           b0 = pic.shadow_regs[ 0x0 ][0]
           b1 = pic.shadow_regs[ 0x0 ][1]
           self.bank_size = b1 - b0
        except:
           self.bank_size = 0x00   


        self.STATUS = self.pic.fsr_regs["STATUS"]

        if pic.fsr_regs.has_key( "PIR1" ):
           self.PIR1 = self.pic.fsr_regs["PIR1"]
        else:
           self.PIR1 = 0xFFFF
           
        if pic.fsr_regs.has_key( "PCL" ):
           self.PCL = self.pic.fsr_regs["PCL"]
        else:
           self.PCL = 0xFFFF

        if pic.fsr_regs.has_key( "PCLATH" ):
           self.PCLATH = self.pic.fsr_regs["PCLATH"]
        else:
           self.PCLATH = 0xFFFF

        if pic.fsr_regs.has_key( "INTCON" ):
           self.INTCON = self.pic.fsr_regs["INTCON"]
        else:
           self.INTCON = 0xFFFF

        if pic.fsr_regs.has_key( "FSR" ):
           self.FSR = self.pic.fsr_regs["FSR"]
        else:
           self.FSR = 0xFFFF

        if pic.fsr_regs.has_key( "INDF" ):
           self.INDF = self.pic.fsr_regs["INDF"]
        else:
           self.INDF = 0xFFFF

        self.port_names = []
        self.port_addr  = []
        self.tris_addr = []

        for portID in range( ord("A"),ord("L") ):
           portName = "PORT" + chr( portID )
           trisName = "TRIS" + chr( portID )
           
           if pic.fsr_regs.has_key( portName ):
              self.port_addr.append( self.pic.fsr_regs[ portName ] )
              self.tris_addr.append( self.pic.fsr_regs[ trisName ] )
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

        # init register map (could be optimized now... as user register are inited to 0xFF..)
        for i in range (0, len(self.bk)):
             self.bk[i] = 0x00 
        
        # bank 0 0x20..0x7F user register to 0xFF
        for i in range (0x20, 0x80):
             self.bk[i] = 0xFF
        # bank 1 0xa0..0xef user register to 0xFF
        for i in range (0xa0,0xf0 ):
             self.bk[i] = 0xFF 
        # bank 2 0x120..0x16f user register to 0xFF
        for i in range (0x120,0x170 ):
             self.bk[i] = 0xFF 
        # bank 3 0x1a0..0x1ef user register to 0xFF
        for i in range (0x1a0,0x1f0 ):
             self.bk[i] = 0xFF 
             
        # init eeprom
        for i in range (0,len(self.eeData)):
            self.eeData[i] = 0xFF  
        
        # init port values      
        for reg in self.port_addr:		        
           self.bk[reg] = 0xFF
        # init tris bit values   
        for reg in self.tris_addr:		        
           self.bk[reg] = 0xFF

        if self.pic.shadow_regs.has_key( self.STATUS ):
            self.shadow_status_regs = self.pic.shadow_regs[ self.STATUS ]
        else:
            self.shadow_status_regs = [ self.STATUS ]
        
        if self.pic.shadow_regs.has_key( self.PCL ):
            self.shadow_pcl_regs = self.pic.shadow_regs[ self.PCL ]
        else:
            self.shadow_status_regs = [ self.PCL ]
           
        # init STATUS
        for reg in self.shadow_status_regs:
           self.bk[ self.STATUS ]  = 0x18   

        self.num_ports = len( self.port_addr)

    def Cycles(self,cycles):
       self.cycles = self.cycles + cycles
    def GetCycles(self):
       return self.cycles

    def getW(self):
        return self.w
   
    def setW(self,w):
        self.w = w

    def getStatus(self):
        return self.bk[self.STATUS]
    
    def getZ(self):
        return (self.bk[self.STATUS]&4)>0
    
    def setZ(self,z):
        if (z):
            val = self.bk[self.STATUS] | 4  # set
            for reg in self.shadow_status_regs:        
               self.bk[reg] = val
        else:
            val = self.bk[self.STATUS] & 251  # clear
            for reg in self.shadow_status_regs:        
               self.bk[reg] = val

    def getC(self):
        return (self.bk[self.STATUS]&1)>0
    
    def setC(self,c):
         if (c):
             val = self.bk[self.STATUS] | 1  # set
             for reg in self.shadow_status_regs:        
                self.bk[reg] = val
         else:
            val = self.bk[self.STATUS] & 254  # clear
            for reg in self.shadow_status_regs:        
               self.bk[reg] = val

    def SetStatusNZ(self, value ):    
       self.setZ( value == 0 )


    def SetStatusForAdd(self, new_value, src1, src2):
    
       new_stat = ( self.bk[self.STATUS] &  0xF8 )
         
       # update C
       if ( (new_value & 0x100) != 0 ):
          new_stat = new_stat | 0x01

       # update DC
       if ( ( ( ( new_value ^ src1 ) ^ src2 ) &0x10 ) != 0 ):
          new_stat = new_stat | 0x02

       # update Z
       if ( (new_value & 0xff ) == 0 ):
          new_stat = new_stat | 0x04

       for reg in self.shadow_status_regs:        
          self.bk[reg] = new_stat


    def SetStatusForSubtract(self, new_value, src1, src2):
    
       new_stat = ( self.bk[self.STATUS] &  0xF8 )       
         
       # update C
       if ( (new_value & 0x100) == 0 ):
          new_stat = new_stat | 0x01

       # update DC
       if ( ( ( ( new_value ^ src1 ) ^ src2 ) &0x10 ) == 0 ):
          new_stat = new_stat | 0x02

       # update Z
       if ( (new_value & 0xff ) == 0 ):
          new_stat = new_stat | 0x04
		
       for reg in self.shadow_status_regs:        
          self.bk[reg] = new_stat

    
    #
    # write to register
    #
    def regWrite(self, reg, value, access = False ):
        value = value & 0xFF
        pclModified = False
        bank = self.cur_bank

        #print "Regwrite %04X " % reg + " to value %02X" % value + " bank %02X " % bank

        # calculate the absolute address
        abs_addr = ( ( reg & (self.bank_size -1 ) ) + bank * self.bank_size )
        
        # check if indirect addressing is required
        if ( reg == self.INDF ):
            # combine FSR + IRP bit (bit7 of status) to form 9 bit absolute address
            abs_addr = ( ( self.getStatus() & 0x80 ) << 1 ) + self.bk[ self.FSR ]

        # get shadow regs
        if self.pic.shadow_regs.has_key( abs_addr ):
           # print "multi keys for key %02X" % abs_addr        
           shadow_regs = self.pic.shadow_regs[ abs_addr ]
           abs_addr = shadow_regs[0]
        else:
           # print "single key for key %02X" % abs_addr        
           shadow_regs = [ abs_addr ] 
	           
        #print "Regwrite %04X " % abs_addr + " to value %02X" % value
        
                   
        #
        # Register has a specific meaning ?
        #
        if( self.STATUS == abs_addr):
            for reg in shadow_regs : 
                self.bk[reg] = value
            self.cur_bank = (self.bk[self.STATUS] >> 5)&3

        elif( self.PCL == abs_addr):
            #
            # PCL modified ? i.e computed goto
            #
            pcl = value
            self.bk[ self.PCL ]  = value
            
            pclath = self.bk[ self.PCLATH ]
                     
            pclath = pclath << 8
            self.pc = pcl+(pclath&0x1FFF) # take only bit4..0 of pclath as pc is 13 bit wise
            # print "PCL WRITE REG ! PCL is %02X" % pcl 
            # print " pclath %04x" % pclath 
            # print " new PC %06X " % self.pc
            
            pclModified = True
            
        #
        # ADC Simulation
        #
        elif (self.ADCON0 == abs_addr):
        
            for reg in shadow_regs : 
               self.bk[reg] = value
        
            if value&0x4 >0 : # bit2 GO
                #start the conversion
                chanelToRead = (value & 0x38) >> 3 #00XX X000 chs2..chs0

                adfm = ((self.bk[ self.ADCON1 ] & 0x80) > 0)
                adrsh = 0
                adrsl = 0

                #print "ADCON1 %04X " % self.ADCON1 + " val %02X" % self.bk[ self.ADCON1 ]
                #print "ADC %02X " % adfm + " channel to read %d " % chanelToRead + " raw %02X" % value
                
                
                #self.adc is need to be filled by the component (potentiometer) on the ui side 
                if (adfm) :
                    # right justified 6 most significant bit of ADRESH are read as 0
                    adrsh = (self.adc[chanelToRead] >> 8) & 0x03 # only 2 bit
                    adrsl = self.adc[chanelToRead] & 0xFF # 8 bit
                    #print "ADC STATE, read channel %d" % chanelToRead + " value %d " % self.adc[chanelToRead]
                else :
                    # left justified 6 least significant bit of ADRESL are read as 0
                    adrsh = (self.adc[chanelToRead] >> 2 ) & 0xFF 
                    adrsl = (self.adc[chanelToRead] & 0x03 )<< 6 
                    #print "ADC STATE, read channel %d" % chanelToRead + " value %d " % self.adc[chanelToRead] + " L %02X " % adrsl+ " H %02X " % adrsh
                    
                self.abswrite(self.ADRESH, adrsh)
                self.abswrite(self.ADRESL, adrsl)
                #self.bk[self.ADRESH] = adrsh
                #self.bk[self.ADRES] = adrsl
                
                self.bk[self.ADCON0] = value & (0xFF-4) # auto clear bit 2 GO
                
        #
        # EEPROM
        #
        elif (  self.EECON2 == abs_addr ):
                for reg in shadow_regs : 
                   self.bk[reg] = value
                if ((self.eeWriteStep == 0) and (self.bk[abs_addr]==0x55)):
                    self.eeWriteStep = self.eeWriteStep +1   
                elif ((self.eeWriteStep == 1) and (self.bk[abs_addr]==0xAA)):
                    self.eeWriteStep = self.eeWriteStep +1    
                # print "EECON2 %d " % self.eeWriteStep + " at addr %02X " % abs_addr + " value %02X " % self.bk[abs_addr]
        elif (self.EECON1 == abs_addr ):
                #
                # DATA EEPROM READ/WRITE
                # very basic impl... yet functional for my needs till now...
                #
                for reg in shadow_regs : 
                   self.bk[reg] = value

                eepgd = ( value  >> 7)&0xFF # programm or data memory ? (bk3)
                rd = value & 1
                wr = (value&2)>>1
                wren = (value&4)>>2
                
                if  ( self.EEADRH != 0xFFFF ):
                    eeadr = ( self.bk[ self.EEADRH ] << 8 ) + self.bk[self.EEADR] # get the address(bk2)
                else:
                    eeadr = self.bk[self.EEADR] # get the address(bk2)
                eeadr = eeadr & ( self.eeprom_size - 1 )
                
                # print "EECON1: eepgd %d " % eepgd + " rd %d " % rd + " wr %d " % wr + " wren %d " % wren  + " eeadr %02x " % eeadr
                if (eepgd == 0 ):
                    # 0 -> data memory
                    if (rd == 1):
                        # READ

                        if self.pic.shadow_regs.has_key( self.EEDATA ):
                            ee_data_shadow_regs = self.pic.shadow_regs[ self.EEDATA ]
                        else:                        
                            ee_data_shadow_regs = [ self.EEDATA ]
                        
                        eedata_value = self.eeData[ eeadr ]
                        
                        # update all eedata regs
                        for reg in ee_data_shadow_regs:
                            self.bk[ reg  ]= eedata_value # read eeprom -> data register

                        # print "EEPROM READ at ADDR %02X " % eeadr + " value %02X " % self.eeData[ eeadr ] 
                            
                        # RD set back to 0
                        for reg in shadow_regs : 
                           self.bk[reg] &= 0xFE
                        
                    elif ((wren==1) and (wr == 1) and (self.eeWriteStep==2)):
                        #WRITE
                        self.eeData[ eeadr ] = self.bk[self.EEDATA]&0xFF # write
                        #WR set back to 0

                        # print "EEPROM WRITE at ADDR %02X " % eeadr + " value %02X " % self.bk[self.EEDATA]

                        for reg in shadow_regs : 
                           self.bk[reg] &= 0xFD
                           
                        self.eeWriteStep = 0
                else:
                    # program memory
                    adr = ( ( self.absreg(self.EEADRH) << 8  ) + self.absreg(self.EEADR) ) & 0x1FFF # 13 bit adresse
                    
                    if (rd == 1):
                        (dataH,dataL) = self.readProgramMem(adr)
                        
                        self.abswrite(self.EEDATA, dataL)
                        self.abswrite(self.EEDATH, dataH)
                        
                        # RD set back to 0
                        for reg in shadow_regs : 
                           self.bk[reg] &= 0xFE
                    
                    elif ((wren==1) and (wr == 1) and (self.eeWriteStep==2)):
                        
                        dataL =  Format.bin(self.absreg(self.EEDATA))
                        dataH = Format.bin(self.absreg(self.EEDATH))
                        data = int(dataH+dataL,2) & 0x3FFF # 14 bit data
                        self.writeProgramMem(adr,Format.bin(data))
                        
                        for reg in shadow_regs : 
                           self.bk[reg] &= 0xFD
                        self.eeWriteStep = 0
        else:
	        # check if this is a PORT register, if so, take TRIS bits into account
	        # i.e. don't change the bits that are set to output
	        for i in range( 0, self.num_ports ) :
	           if self.port_addr[i] == abs_addr:
	
	              tris = self.bk[ self.tris_addr[i]]
	              old_value = self.bk[ self.port_addr[i] ] 
	
	              # print "REG %02X" % abs_addr + " TRIS =%02X" % tris + " OLDVAL=%02X" % old_value + " NEWVAL %02X" % value
	                         
	              old_value = old_value & tris
	              value = value & (255-tris)
	              
	              # print "1EG %02X" % abs_addr + " TRIS =%02X" % tris + " OLDVAL=%02X" % old_value + " NEWVAL %02X" % value
	
	              value = value | old_value
	              #print "FOUND FINAL AFTER MASKING %02X" % value
	        # some bytes are avaiable in multi bank
	        for reg in shadow_regs : 
	           self.bk[reg] = value
	           # print "DO Regwrite %04X " % reg + " set to %02X" % value
          
                    
        #
        # watching any register ?
        #
        for monitor in self.monitors:
            if (monitor.address == abs_addr ):
                monitor.execute( value )
        for monitor in self.globalWriteMonitors:
            monitor.execute(abs_addr,value,self)   
        
        return pclModified
 
    #
    # Register read
    #
    def regRead(self,reg, access = False ):

        bank = self.cur_bank
        
        # hack to unlock ADCON0:G0
        #if (reg == 0x1F):
        #    self.bk[0x1F] = self.bk[0x1F] &(255-4) # force ADCON:GO ( bit 2) to 0

        # calculate the absolute address
        abs_addr = ( reg + bank * self.bank_size )

        # print "REGREAD: reg:%02x"%reg + " bank:%02X "%bank + " > abs = %04X" % abs_addr

        # check if indirect addressing is required
        if ( reg == self.INDF ):
            # compbine FSR + IRP bit (bit7 of status) to form 9 bit absolute address
            abs_addr = ( ( self.getStatus() & 0x80 ) << 1 ) + self.bk[ self.FSR ]
            # print "INDIRECT: status:%02x"%self.getStatus() + " FSR:%02X "%self.bk[ self.FSR ]+ " > abs = %04X" % abs_addr

        # get shadow regs
        if self.pic.shadow_regs.has_key( abs_addr ):
           shadow_regs = self.pic.shadow_regs[ abs_addr ]
           abs_addr = shadow_regs[0]
        else:
           shadow_regs = [ abs_addr ] 

        # print "PIR1 %02X" % self.PIR1
        # print shadow_regs
                   
        if ( self.PIR1 == abs_addr ): 
      
            data = self.bk[ self.PIR1 ]
            # print "PIR1 content is %02X" % data
            
            if self.uartProvider != None and  self.uartProvider.hasData() :
                data = data | 32 # set RCIF flag
            if self.uartReceiver != None and  self.uartReceiver.isReady() :
                data = data | 16 # set TXIF flag
            return data
        
        elif ( self.RCREG == abs_addr ):
            data = self.bk[ self.RCREG ]  
            if self.uartProvider != None and  self.uartProvider.hasData() :
                data =  self.uartProvider.getNext()          
            return data 
        else:
	        value = self.bk[abs_addr]

	        # check if this is a PORT register, if so, take TRIS bits into account
	        # i.e. don't change the bits that are set to output
	        for port_addr in self.port_addr :
	           if port_addr == abs_addr:
	              for monitor in self.globalReadMonitors:
	                 value = monitor.execute(reg,self,value) # will be updated by the monitor
                                                             # used for external device like buttons, switch...
                                                             # these external register have no callback, so I must
                                                             # update reg when I discover the change ... i.e when I read
                                                             # the port the device is on...
	              self.regWrite(abs_addr, value)
        
	        return value
    
    # very specific use,
    # try to use regRead instead
    # Register read (with no bank handeling)
    #
    def absreg(self, reg):
        value = self.bk[reg]
        #if reg in (5,6,7,8,9) and len(self.globalReadMonitors)>0 : # for devices...
        #    for monitor in self.globalReadMonitors:
        #        value = monitor.execute(reg,self,value) 
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
                monitor.execute(value)
                
        for monitor in self.globalWriteMonitors:
            monitor.execute(reg,value,self) 
    
    
    #
    # BANK 
    #
    def bank(self):
        return self.cur_bank
        #return (self.bk[self.STATUS] >> 5)&3
    
    #
    # internal PC 
    #
    #    
    def getPc(self):
        return self.pc
    
    def setPc(self,i):
        self.pc = i
        newVal = ( self.pc & 0xFF )
        for reg in self.shadow_pcl_regs:
           self.bk[ reg ] = newVal
    
    def incPc(self):        
        self.pc = self.pc + 1
        newVal = ( self.pc & 0xFF )
        for reg in self.shadow_pcl_regs:
           self.bk[ reg ] = newVal
    
    #
    # compute next pc for Goto and Call regarding to pclath 
    #
    def changePcForCallGoto(self, adr):
        # manage PCLATH bit 4:3
        #pclath = self.regRead(self.PCLATH)
        # 24 = 00011000
        
        pclath =  (self.bk[self.PCLATH]&24) << 8
        self.setPc( (adr&0x7FF) + pclath )
    
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
    
    def getLevel(self):
        return self.level
    
    def setLevel(self,i):
        self.level = i
    
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
        return self.builder # 14 bit Builder
    
