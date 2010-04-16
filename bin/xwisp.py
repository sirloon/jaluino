#!/usr/local/bin/python
#############################################################################
#
# XWisp
#
# see http://www.voti.nl/xwisp
#
# 07-JAN-2010 V 1.35 (released)
#    18F4685-group config flags mask corrected
#
# 18-JUN-2009 V 1.34 (released)
#    better error message for:
#       - wrong COM port
#       - loss of comm on entering programming mode
#    tested: 16F72x, 18F2553
#    some minor corrections
#
# 15-MAR-2009 V 1.33 (released)
#    GUI should be functional now
#
# 01-FEB-2009 v 1.32 (released)
#    GUI iconbitmap exception handled
#    12-bit core ID locations corrected
#    14-bit cores without ID (16x94) bug corrected
#
# 18-JAN-2009 v 1.31 (released)
#    PIC16H
#
# 01-JUN-2008 v 1.30 (release)
#    GUI available but not documented
#
# XX-MAR-2008 v 2.01 (work in progress)
#    chip-fixed bits not applied before programming!
#    (errors with fuses in 18F4550)
#
# XX-NOV-2007 v 2.00 (work in progres)
#    attempt to connect first without a serial line break (faster)
#    16F88x config word 2 fixed bits corrected
#    WAIT END and WAIT ERR commands added
#    some exception handling
#    wisp628 >= 1.23 is identified as '(wisp648 firmware)'
#    CMD_CHIPS, CMD_INFO, CMD_LVP, CMD_HVP, CMD_SHORT, CMD_RESET added
#    GET, PUT, etc. now end in target reset
#    automatic handling of power short added
#    power short at prog exit added
#    some GUI code added but not yet activated
#    added 18F4685, 18F4455 and relatives
#    compare changed to remove quadratic timing
#    when a chip is specified it must be found
#
# 12-JUL-2007 v 1.20
#    update for Wisp648
#    lots of new targets
#    reading of target without EEPROM no longer fails
#
# xx-FEB-2003 v 1.09
#    write block size added to support WLoader for 16F87XA
#    fixed (fuses) bits added  
#    precious items (oscal, bandgap) added
#    warning on missing fuses information
#    commands: USE, NOPURGE
#    ignore CCS comment line in hex file 
#    added 16F627A, 16F628A, 16F648A, 16F688
#    eeprom size for 16F62x corrected
#    added 16F87, 16F88
#    problem with f84/c84 erase corrected [Cyril Wilkinson]
#    16C84 fixed fuses bits added
#    16F87xA fixed fuses bits corrected
#    PORT <name> changed forn compatibility with for Unixes
#    idem for file name arguments
#
# 07-FEB-2003 v 1.07
#    16f818/819 added
#    baudrate switching changed for Wisp628 >= 1.08
#    ID writing tested
#    various small bugs corrected
#    16F72 added
#
# 04-JAN-2003 v 1.06
#    error message for unsupported baudrates corrected
#    some ZPL code added, not functional yet
#    hard-wired bits in fuses
#    PASS bug corrected
#    16F630/676 added
#    12F protection setting corrected, but not used yet
#    CLOSE_WINDOW command
#    TPROG command
#    18F DATA EEPROM corrected
#    use multi-address read on Wisp628 >= 1.07
#
# 19-NOV-2002 v 1.05
#    use of higher baudrates
#    PASS repaired
#    higher serial ports (COM9..) can now be used on Windows
#
# 19-OCT-2002 v 1.04
#    12F629 and 12F675 swap corrected
#    DUMP added to on-line help
#    CLOSE, CLEAR
#    WAIT corrected
#    RTS, DTR take immediate effect
#
# 30-SEP-2002 v 1.03
#    tested with jython, should work on posix
#
# 14-SEP-2002 v 1.02
#    16F877A added
#    target detection changed
#    MACRO bug corrected
#
# 05-SEP-2002 v 1.01
#    communication speedup
#
# 04-SEP-2002 v 1.00
#    first version
#
#############################################################################
#
# issues
#
# block others while using analyser or pins setter
# pins setter: allow custom naming schemes
# gui log: line numbers
# gui: large GO
# gui: resize
# gui pin tool: log for logic analyser?
# error handling
# command-line add 'precious' to preserve for instance an ID
# pin access on the command line
# log functie werkt niet (RobH)
# 18F4685 write 256 eeprom when 1024 enabled => strange error, reads from wrong part?
# exception log does not work for a TK text window?
# 16F88x calibration word!
# can not set fuses without setting a target first
# LOG <file> does not work
# progress indication should be self-timing (esp. for 18F's)
# do not try to write fuses to WLoader?
# select -a+fc might go wrong when protected
# writing 16F7x ID memory fails
# initial (blanco) image contains all 0, should be 3FFF/FF?
# when reading a hex file the length is ignored
# is an errorlevel reported to DOS?
# strange error when reading unknown device ID with specified chip
#
#############################################################################
#
# (c) 2002...2009 Wouter van Ooijen / voti
#
# Redistribution and use in source and binary forms, with or without 
# modification, is permitted.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER "AS IS" AND ANY EXPRESS 
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
# THE POSSIBILITY OF SUCH DAMAGE.
#
#############################################################################

Version = '1.35'


#############################################################################
#
# misc
#
#############################################################################

def Split_Quoted( String ):
   List = []
   Item = ''
   Escape = 0
   Quote = ''
   for Char in String:
      #print Char, '"'.find( Char ), Quote, Item, List
      if Escape:
         Item = Item + Char
         Escape = 0
      # ecaping is a bit troublesome (Windows/Linux!)
      #elif Char == '\\':
      #   Escape = 1
      elif Char == Quote:
         #print 'Q]'
         List.append( Item )
         Item = ''
         Quote == ''      
      elif '"'.find( Char ) <> -1:
         #print 'Q['
         Quote = Char
      elif Quote <> '':
         #print 'Qq'
         Item = Item + Char
      elif " \t".find( Char )<> -1:
         if Item <> '':
            List.append( Item )
            Item = ''
      else:
         Item = Item + Char
   if Item <> '':
      List.append( Item )
   return List
   
# must be possible to do this nicer...   
def Repeat( Char, N ):
   Result = ''
   for i in range( 0, N ):
      Result = Result + Char
   return Result     


#############################################################################
#
# dealing with bits that are fixed in the hardware
#
#############################################################################

class Mask:
   "masking bits to a hard-wired 0 or 1"
   
   def __init__( self, ZERO = 0, ONE = 0 ):
      self.ZERO = ZERO
      self.ONE = ONE
      
   def Apply( self, X ):
      return ( X | self.ONE ) & ( -1 ^ self.ZERO )      
      
class Fixed:
   "list of hard-wired masks"
   "usage:"
   "Fix = [ Address : Mask( ... ), ... ]"
   "Use_Value( Fix( Address, Value )"
   
   def __init__( self, List ):
      self.List = List
      
   def Fix( self, Address, Value ):
      if self.List.has_key( Address ):
         return self.List[ Address ].Apply( Value )
      return Value
      
class XWisp_Error( Exception ):

     def __init__(self, Value, Explanation = None):
         self.Value = "\n" + Value
         if Explanation != None:
            self.Value += "\n\n" + Explanation
         
     def __str__(self):
         return self.Value


#############################################################################
#
# intel hex file read, write, print, merge, etc.
#
#############################################################################

class Hex_Image:
   "read, write and manipulate Intel hex format files"

   class Hex_Image_Error( IOError ):
      "errors raised by Hex_Image, derived from IOError"
      pass

   def Raise( self, Message ):
      "raise a Hex_Image_Error with suitable prefix"
      raise self.Hex_Image_Error, self.Error_Prefix + Message

   def __init__( self, File = None, Stride = 1, Suffixes = [ 'hex' ] ):
      "initialize, optionally specify stride and/or file to read from"
      self.Error_Prefix = ''
      self.Clear()
      self.Stride = Stride
      self.Suffixes = Suffixes
      self.Fixed = Fixed({ })
      if File <> None:
         self.Read( File )

   def Clear( self ):
      "clear all data, but do not modify stride"
      self.Data = {}
      self.Extended_Linear = 0

   def Set( self, Address, Value ):
      "set value at specified address"
      for Offset in range( 0, self.Stride ):
         self.Data[ Address * self.Stride + Offset ] = Value % 256
         Value = Value / 256;

   def Erase( self, Address ):
      for Offset in range( 0, self.Stride ):
         A = Address * self.Stride + Offset
         if self.Data.has_key( A ):
            del self.Data[ A ]

   def Get( self, Address, Default = None ):
      "return value at specified address"
      Value = None
      for Offset in range( self.Stride - 1, -1, -1 ):
         # print "%04X %04X %04X " % ( Address, Offset, Value )
         if self.Data.has_key( self.Stride * Address + Offset ):
            if Value == None:
               Value = 0
            Value = ( 256 * Value ) + \
               self.Data.get( self.Stride * Address + Offset )
         # print "%04X" % Value
      if Value == None:
         Value = Default
      if self.Fixed <> None:
         Value = self.Fixed.Fix( Address, Value )
      return Value

   def Get_Hex( self, Address, Default = None ):
      "return hex (string) representation "
      "of the value at the specified address"
      if self.Has( Address ):
         Value = self.Get( Address )
      else:
         Value = Default
      #if ( Value > 0xFF ) or ( Value < 0 ):
      #  print "%X -> %X " % ( Address, Value )
      return ( '%%0%dX' % ( 2 * self.Stride )) % Value            

   def __Has_Range( self, Base, Count ):
      "check whether all addresses in Base .. Base + Count are present"
      for Address in range( Base, Base + Count ):
         if not self.Data.has_key( Address ):
            return 0
      return 1

   def Has( self, Address ):
      "check whether Address is present, taking stride into account"
      return self.__Has_Range( Address * self.Stride, self.Stride )

   def Addresses( self ):
      "return sorted list of all addresses"
      List = self.Data.keys()
      List.sort()
      return [ A / self.Stride for A in List \
         if (( A % self.Stride == 0 ) & \
            self.__Has_Range( A, self.Stride ))]

   def __Try_Open( self, File_Name, Suffixes ):
      if Suffixes == None:
         Suffixes = self.Suffixes
      try:
         File = open( File_Name, 'r' )
         return File
      except:
         pass
      for Suffix in Suffixes:
         try:
            File = open( File_Name + '.' + Suffix, 'r' )
            return File
         except:
            pass
      try:
         File = open( File_Name, 'r' )
      except:
         self.Raise( 'could not open %s for reading' % File_Name )

   def Read( self, File_Name, Suffixes = None ):
      "read from a file"
      File = self.__Try_Open( File_Name, Suffixes )
      Save_Stride = self.Stride
      self.Stride = 1
      Linear_Base = 0
      try:
         Nr = 0
         for Line in File.readlines():
            Nr = Nr + 1
            self.Error_Prefix = File_Name + ' line ' + str( Nr ) + ' '
            while ( 'x' + Line )[-1:] < ' ':
               # print "[" + Line + "]"
               Line = Line[:-1]
            if ( Line + ';' )[0] != ';': # ignore empty lines and CCS comment lines             
               if Line[0] <> ':':
                  self.Raise( 'does not start with a colon' )
               if len( Line ) % 2 <> 1:
                  self.Raise( 'does not contain an odd number of characters' )
               Length = int( Line[1:3], 16 )
               Address = int( Line[3:7], 16 )
               Type = Line[7:9]
               Checksum = ( Length + Address / 256 + \
                  Address % 256 + int( Type )) % 256
               Address = Address + Linear_Base
               Line = Line[9:]
               if Type == '00':
                  # data
                  while len(Line) > 2:
                     Data = int( Line[0:2], 16 )
                     self.Set( Address, Data )
                     Line = Line[2:]
                     Address = Address + 1
                     Checksum = ( Checksum + Data ) % 256

               elif Type == '01':
                  # end of file
                  pass

               elif Type == '02':
                  # extended segment
                   self.Raise( 'Type=2' )

               elif Type == '03':
                  # start segment
                  self.Raise( 'Type=3' )

               elif Type == '04':
                  # extended linear
                  Value = int( Line[0:4], 16 )
                  Linear_Base = 0x10000 * Value
                  Checksum = ( Checksum + Value / 256 ) + ( Value % 256 )
                  self.Extended_Linear = 1
                  Line = Line[4:]

               elif Type == '05':
                  # start linear
                  print "Hex file contains start address, which is ignored"
                  Value = long( Line[0:8], 32 )
                  Checksum = Checksum + int( Line[0:2], 16 )
                  Checksum = Checksum + int( Line[2:4], 16 )
                  Checksum = Checksum + int( Line[4:6], 16 )
                  Checksum = Checksum + int( Line[6:8], 16 )
                  Line = Line[8:]                  
   
               else:
                  self.Raise( 'unknown type=' + Type )

               if ( Checksum + int( Line, 16 )) % 256 <> 0:
                  self.Raise(
                     'checksum found=' + Line +
                     ' expected=' + ( '%02X' % (( 256 - Checksum ) % 256 )))
 
      finally:
         self.Stride = Save_Stride
         File.close()

   def Add( self, Image ):
      "add content of another image"
      for Address in Image.Data.keys:
         self.Data[ Address ] = Image.Data.get( Address )

   def __Hex_Line( self, Count, Base, Type, Data, Checksum ):
      "create data line for writing"
      Checksum = Checksum + Count + Type + \
         (( Base / 256 ) % 256 ) + ( Base % 256 )
      Checksum = ( 256 - ( Checksum % 256 )) % 256
      return ':' + \
         ( '%02X' % Count ) + \
         ( '%04X' % ( Base % 0x10000 )) + \
         ( '%02X' % Type ) + \
         Data + \
         ( '%02X' % Checksum )

   def Write( self, File_Name, Extended_Linear = None ):
      "write to a hex file"
      import os
      File_Name = os.path.normpath( File_Name )
      try:
         os.makedirs( os.path.dirname( File_Name ))
      except:
         pass
      try:
         File = open( File_Name, 'w' )
      except:
         self.Raise( 'could not open %s for writing' % File_Name )
      Save_Stride = self.Stride
      self.Stride = 1
      Save_Fixed = self.Fixed
      self.Fixed = None
      try:
         if Extended_Linear == None:
            Extended_Linear = self.Extended_Linear
         if Extended_Linear:
            File.write( ':020000040000FA\n' )
         Count = 10000
         Line = ''
         Last = 0
         for Address in self.Addresses():
            if ( Count >= 16 ) \
            or ( Address <> Last + 1 ) \
            or ( Address % 16 == 0) \
            or ( Address / 0x10000 ) <> ( Last / 0x10000 ):
               if Line <> '':
                  File.write( self.__Hex_Line(
                     Count, Base, 0x00, Line, Checksum ) + '\n')
               Base = Address
               Count = 0
               Line = ''
               Checksum = 0
            if Address / 0x10000 <> Last / 0x10000:
               Segment = Address / 0x10000
               File.write( self.__Hex_Line(
                  0x02, 0x0000, 0x04,
                  ( '%04X' % Segment ),
                  Segment / 256 + Segment % 256 ) + '\n')
            Line = Line + self.Get_Hex( Address )
            Checksum = ( Checksum + self.Get( Address )) % 256
            Count = Count + 1
            Last = Address
         if Line <> '':
            File.write( self.__Hex_Line(
               Count, Base, 0x00, Line, Checksum ) + '\n')
         File.write( ':00000001FF\n' )
      finally:
         self.Stride = Save_Stride
         self.Fixed = Save_Fixed
         File.close()

   def __str__( self ):
      "return printeable representation"
      Last = -10
      Count = 0
      Result = ''
      for Address in self.Addresses():
         if ( Address <> Last + 1 ) | ( Count == ( 16 / self.Stride )):
            if Result <> '':
               Result = Result + '\n'
            Result = Result + ( '%04X:' % Address )
            Count = 0
         Result = Result + ' ' + self.Get_Hex( Address )
         Count = Count + 1
         Last = Address
      if Result == '':
         Result = 'image is empty'
      return ( 'stride=%d\n' % self.Stride ) + Result

   def String( self ):
  
      return self.__str__()      

   def Clone( self ):
      "return cloned copy"
      import copy
      return copy.deepcopy( self )

   def _Compare(
      self,
      Image,
      Name1 = 'image1',
      Name2 = 'image2',
      Range = None,
   ):
      "return either None, or a string describing the first difference"
      # return None
      # print "list 1"
      List_1 = self.Addresses()
      # print "list 2"
      List_2 = Image.Addresses()
      if self.Stride != Image.Stride:
         return "strides are different: $s=%d %s=%d" % \
            Name1, Name2, self.Stride, Image.Stride
      N = 0
      for Address in List_1:
         # if Address % 256 == 0: print "%05X %d" % ( Address, Address )
         if ( Range == None ) or Address in Range:
            if len( List_2 ) == 0:
               return "address %04X in %s but not in %s" % \
                  ( Address, Name1, Name2 )
            Other = List_2.pop( 0 )
            # Other = List_2[ N ]
            # N = N + 1
            if Address < Other:
               return "address %04X in %s but not in %s" % \
                  ( Address, Name1, Name2 )
            if Address > Other:
               return "address %04X in %s but not in %s" % \
                  ( Other, Name2, Name1 )
            if 1: 
             if self.Get( Address ) != Image.Get( Other ):
               return "different data at address %04X: %s=%s %s=%s" % \
                  ( Address, \
                  Name1, self.Get_Hex( Address ), \
                  Name2, Image.Get_Hex( Address ) )
      return None
    
   # for speed tests only   
   #def Getx( self, Address ):
   #   return 5

   def Compare(
      self,
      Image,
      Name1 = 'image1',
      Name2 = 'image2',
      Range = None,
   ):
      "return either None, or a string describing the first difference"
      if self.Stride != Image.Stride:
         return "strides are different: $s=%d %s=%d" % \
            Name1, Name2, self.Stride, Image.Stride
      N = 0
      for Address in self.Addresses():
         # if Address % 256 == 0: pass
         # print ":  %05X %d" % ( Address, Address )
         if ( Range == None ) or Range.In( Address ):           
            S = self.Get( Address )
            O = Image.Get( Address )
            # print "self %04X, other %04X" % ( S, O )
            if O == None:
               return "address %04X in %s but not in %s" % \
                  ( Address, Name1, Name2 )
            if S != O:
               return "different data at address %04X: %s=%X %s=%X" % \
                  ( Address, Name1, S, Name2, O )
      return None


#############################################################################
#
# dealing with precious information that must be preserved
#
#############################################################################

class Precious:

   def __init__( self, Default, List ):
      self.List = List
      self.Addresses = []
      self.Image = None
      self.Default = Default
      self.Addresses = Hex_Image()
      for Address, Mask in List:
         self.Addresses.Set( Address, 0 )
            
   def Patch( self, Image ):
      # print self.List
      for Address, Mask in self.List:
         # print Address, Mask
         # print Image.Has( Address ), ( "%04X" % self.Default )
         if Image.Has( Address ):
            Original = Image.Get( Address )
         else:
            Original = self.Default 
         Precious = self.Image.Get( Address, self.Default )
         New = ( Precious & Mask ) | ( Original & ~ Mask )
         if 0:
            print "patch a=%04X O=%04X P=%04X M=%04X %04X %04X N=%04X" % \
              ( Address, Original, Precious, ( Precious & Mask ), \
              ( Original & ~ Mask ), Mask, New )
         Image.Set( Address, New )
            

#############################################################################
#
# ZPL
#
#############################################################################

class ZPL_Message:
   "a ZPL message"
   
   def Clear( self ):
      self._Last_Byte = 0
      self._Message = ''
      self._Checksum = 0
      self._Image = ''
      
   def __init__( self ):
      self.Clear()
      self.Command_Indicator = 0xA5
      self._Encode_0 = chr( 0xF9 )
      self._Encode_1 = chr( 0xFB )
      
   def Message( self ):
      return self._Message
      
   def _Add_Bit( self, Bit ):
      if Bit:
         self._Message = self._Message + self._Encode_1
      else:
         self._Message = self._Message + self._Encode_0
               
   def Add_Bit( self, New_Bit, Stuffing = 1 ):
      self._Last_Byte = (( 2 * self._Last_Byte ) % 256 ) + New_Bit
      self._Add_Bit( New_Bit )
      if self._Last_Byte == self.Command_Indicator:
         if Stuffing:
            print "STUFFING"
            self._Add_Bit( 0 )
            self.Last_Byte = 0 # clear command indicator
         else:
            self._Add_Bit( 1 )
            
   def Add( self, New_Byte, Stuffing = 1 ):
      self._Checksum = self._Checksum ^ New_Byte
      self._Image = self._Image + ( "%02X [%02X] " % (New_Byte, self._Checksum ))
      for Dummy in range( 8 ):
         self.Add_Bit(( New_Byte & 1 ) <> 0, Stuffing )
         New_Byte = New_Byte / 2
         
   def Add_Checksum( self ):
      self.Add( self._Checksum )
         
   def Add_Command_Indicator( self ):
      self.Add( self.Command_Indicator, Stuffing = 0 )
      
   def Decode( self ):
      #return self._Image
      Result = ''
      for C in self._Message:
         if C == self._Encode_0:
            Result = Result + '0'
         elif C == self._Encode_1:
            Result = Result + '1'
         else:
            Result = Result + '?'
      return self._Image + '  ' + Result

                  
class ZPL:
   "zero-pin loader protocol"
   
   def Log( self, String ):
      "debug log"
      import time, sys
      self.Console.Print( str( "%04.3f" % time.clock() ) + ' ' + String )
   
   def __init__(
      self,
      Console,
      Port,
      DTR = None,
      RTS = None,
      Debug = 0
   ):
      "initialize and connect Port"
      import serial

# klopt nix meer van      

      self.Console = Console
      self.Com_Port = Port
      self.DTR = DTR
      self.RTS = RTS
      self.Debug = 0
      self.Error_Prefix = ''

      # connect the serial port
      if self.Debug:
         self.Log(
            'ZPL( Port=%s )'
            % ( str( self.Com_Port )))
      self.Port = serial.Serial(
         port      = self.Com_Port,
         baudrate  = 115200,
         stopbits  = serial.STOPBITS_ONE,
         timeout   = 2.0 )

      # set handshake lines
      #self.Set_RTS( self.RTS )
      #self.Set_DTR( self.DTR )
      
      # commands
      self.Command_Start = 0x33
      self.Command_Write_Flash = 0x44
      self.Command_Write_EEPROM = 0x55
      self.Command_Run = 0x66

   def Close( self ):
      "close serial port"
      if self.Debug:
         self.Log( 'self.Close()' )
      self.Port.close()
      
   def Send( self, Msg ):
      "send a message"
      import time
      if 0:
         for C in Msg.Message():
            print 'send char '
            self.Port.write( C )
            time.sleep( 0.001 )
         print 'send: ' + Msg.Decode()
      else:
         # print 'send:' + Msg.Decode()
         self.Port.write( Msg.Message() )
               
   def Send_Message( 
      self, 
      Command, 
      Address = 0, 
      Data = None
   ):
      "compose and send a ZPL message"    
      import time
      if Data == None:
         Data = []
         for Dummy in range( 64 ):
            Data.append( 0 )
      M = ZPL_Message()
      M.Add( 0 )
      for X in Data:
         M.Add( X )
      M.Add( Address & 0xFF )
      M.Add(( Address / 0x100 ) & 0xFF )
      M.Add(( Address / 0x10000 ) & 0xFF ) 
      M.Add( Command )
      M.Add_Checksum()
      M.Add_Command_Indicator()
      time.sleep( 0.1 )
      self.Send( M )
      time.sleep( 0.1 )
      
   def Load( self, File ):
      import time
      Image = Hex_Image( File )
      self.Send_Message( Command = self.Command_Start )
      for A0 in range( 0, 3 ): # ( 16 * 1024 ) / 64 ):
         N = 0
         D = []
         for A1 in range( 64 ):
            Address = A0 * 64 + A1
            if Image.Has( Address ):
               N = N + 1
            D.append( Image.Get( Address, Default = 0xFF ))
         Address = A0 * 64
         # print Address, N
         if N > 0:
            # print Address
            self.Send_Message( 
               Command = self.Command_Write_Flash,
               Address = Address,
               Data = D )                                    
            time.sleep( 0.025 )
      self.Send_Message( Command = self.Command_Run, Address = 2 )
      
   def Test( self ):
      self.Load( 'b452-1.hex' )
      return
      import time
      if 0: 
         x  = ''
         for y in range( 100 ):
            x = x + chr( 0xF9 ) + chr( 0xF0 )
         while 1:
            time.sleep( 0.001 )
            self.Port.write( x )         
            # print 1
      x = []
      for d in range( 64 ):
         x.append( 0x31 )
      if 0:
         self.Send_Message( Command = self.Command_Start, Data = x )                  
      if 1:
         self.Send_Message( 
            Command = self.Command_Write_Flash,
            Address = 0x000000 ,
            Data = x)                  

          
#############################################################################
#
# WBus access
#
#############################################################################

class WBus:
   "access to a WBus serial 'bus'"

   class WBus_Protocol_Error( IOError ):
      "protocol errors raised by WBus, derived from IOError"
      pass

   class WBus_Command_Failed( IOError ):
      "command failure error raised by WBus, derived from IOError"
      pass

   class WBus_Use_Error( IOError ):
      "use errors raised by WBus, derived from IOError"
      pass

   def Log( self, String ):
      "debug log"
      import time, sys
      self.Console.Print( str( "%04.3f" % time.clock() ) + ' ' + String )

   def Set_RTS( self, Value ):
      "set RTS line"
      if self.Debug:
         if Value <> None:
            self.Log( 'self.SetRTS( %d )' % Value )
      self.RTS = Value
      if self.RTS != None:
         self.Port.setRTS( self.RTS )

   def Set_DTR( self, Value ):
      "set DTR line"
      if self.Debug:
         if Value <> None:
            self.Log( 'self.SetDTR( %d )' % Value )
      self.DTR = Value
      if self.DTR != None:
        self.Port.setDTR( self.DTR )

   def __init__(
      self,
      Console,
      Port = None,
      ID = 0,
      Baudrate = 19200,
      DTR = None,
      RTS = None,
      Debug = 0
   ):
      '''initialize and connect Port.
      Port, ID, Baudrate etc. can be specified'''
      import serial, time
      from serial import serialutil

      self.Console = Console
      self.Com_Port = Port
      self.ID = ID
      self.Baudrate = Baudrate
      self.DTR = DTR
      self.RTS = RTS
      self.Debug = 0
      self.Error_Prefix = ''
      self.Fast = 0

      # connect the serial port
      self.Open_Port()

      # set handshake lines, perform reset only if no DTR value set
      self.Set_RTS( RTS )
      if self.DTR <> None:
         self.Port.setDTR( self.DTR )
      else:
         self.Set_DTR( 1 )
         time.sleep( 0.005 )
         self.Set_DTR( 0 )
         
   def Open_Port( self ):
      import serial, time
      from serial import serialutil

      if self.Debug:
         self.Log(
            'WBus( Port=%s Baudrate=%s )'
            % ( str( self.Com_Port ), str( self.Baudrate )))
      try:
         self.Port = serial.Serial(
            port      = self.Com_Port,
            baudrate  = self.Baudrate,
            stopbits  = serial.STOPBITS_ONE,
            timeout   = 2.0 )
      except serialutil.SerialException :
         raise XWisp_Error( 
            "could not open port '%s'" % str( self.Com_Port ).replace( '\\\\.\\', ''),
            "This port might not exist, be disabled, or be used by another application. "
            "Note that in a Windows DOS box a legacy application can claim a serial port, "
            "which will only be relased when the DOS box is closed. "
         )      
         
   def Try_To_Connect( self, Break = 0 ):

      # send break to get devices to attention or active state
      if Break > 0:
         self.Port.sendBreak( duration = Break )

      # test for echoing hardware
      self.Clear()
      self.Port.write( chr( 255 ))
      Echo = self.Port.read( 1 )
      self.Echoing = ( Echo == chr( 255 ))

      # activate device
      self.Send_Slowly(( '%04X' % self.ID ) + 'h' )

      # get device type and version
      self.Clear()
      self.Send_Expect( 't' )
      self.Type = self.Get()
      self.Send_Expect( 'v' )
      self.Version = self.Get()
               
   def Connect(
      self,
      ID = None,
      DTR = None,
      RTS = None
   ):
      '''connect to WBus device.
      ID, Baudrate, DTR, RTS can be specified'''
      
      if self.Port == None:
         self.Open_Port()

      # handle parameters
      if ID <> None:
         self.ID = ID
      self.Set_RTS( RTS )
      self.Set_DTR( DTR )
      
      try:
         self.Try_To_Connect( 0 )
      except:
         if self.Debug:
            self.Log( 'now try with break' )
         try:   
            self.Try_To_Connect( 0.2 )
         except:
            raise XWisp_Error( 
               "failed to connect",
               "The connection to the programmer failed. Some possible causes: "
               "\n   - the programmer is not connected, not powered, or defect"
               "\n   - the communication port is not set correctly"
               "\n   - the serial cable is not good (must be straight, not null-modem)" )

   def Close( self ):
      "close connection and serial port"
      if self.Debug:
         self.Log( 'self.Close()' )
      self.Port.close()
      self.Port = None

   def Clear( self ):
      "clear input buffer"
      import time
      if self.Debug:
         self.Log( 'Clear()' )
      time.sleep( 0.1 )
      self.Port.flushInput()
      self.Port.flushOutput()

   def Send_Char( self, Char ):
      "send a char, observe timing, set high bit when hardware echoes"
      import time
      #time.sleep( 0.002 )
      if self.Debug:
         self.Log( "Send_Char( '%s' )" % Char )
      if self.Echoing and ( Char != '' ) :
         Char = chr( ord( Char ) + 128 )
      # print 'x1'
      self.Port.write( Char )
      # print 'x2'
      if self.Debug:
         self.Log( 'Send_Char done' )

   def Receive_Char( self ):
      "receive a char, skip hardware echo"
      if self.Debug:
         self.Log( 'Receive_Char()' )
      Result = self.Port.read( 1 )
      if self.Echoing:
         Result = self.Port.read( 1 )
      if self.Debug:
         self.Log( "Received = '%s'" % Result )
      return Result
      
   def Receive_All( self, N = 0 ):
      "receive all that is available in the buffer"
      if self.Debug:
         self.Log( 'Receive_All( %d )' % N )
      Result = self.Port.read( N )
      if self.Debug:
         s = ''
         for c in Result:
            s = s + ( ' %02X' % ord( c ) )
         self.Log( 'Received(%s )' % s )
      return Result      

   def Send_Slowly( self, String ):
      "send slowly"
      import time
      if self.Debug:
         self.Log( 'Send_Slowly( "' + String + '" )' )
      for Char in String:
         time.sleep( 0.05 )
         self.Send_Char( Char )

   def Send( self, Char ):
      "send a char "
      if self.Debug:
         self.Log( 'Send( "' + Char + '" )' )
      self.Send_Char( Char )

   def Send_Receive( self, Char ):
      "send a char and expect a response from the device"
      if self.Debug:
         self.Log( 'Send_Receive( "' + Char + '" )' )
      self.Send_Char( Char )
      Response = self.Receive_Char()
      if Response == '?':
         raise self.WBus_Command_Failed, \
            "send=%c" % Char
      if self.Debug:
         self.Log( "Response='%s'" % Response )
      return Response

   def Send_Expect( self, String ):
      "send and expect echo from the device"
      import time
      if self.Debug:
         self.Log( 'Send_Expect( "' + String + '" )' )
      if self.Fast: 
         self.Port.write( String )      
         Reply = self.Port.read( len( String ))
         if Reply != String.upper():
            raise self.WBus_Protocol_Error, \
               "send='" + String + "' received='" + Reply + "'"
      else:
         for Char in String:
            Reply = self.Send_Receive( Char )
            if Reply != Char.upper():
               raise self.WBus_Protocol_Error, \
                  "send='" + Char + "' received='" + Reply + "'"
                  
   def Send_And_Receive( self, String ):
      "send and receive echo from the device"
      import time
      if self.Debug:
         self.Log( 'Send_Expect( "' + String + '" )' )
      if self.Fast: 
         self.Port.write( String )      
         Reply = self.Port.read( len( String ))
         return Reply
      else:
         Reply = ""
         for Char in String:
            Reply_Char = self.Send_Receive( Char )
            Reply = Reply + Reply_Char
            if Reply != Char.upper():
               return Reply
         return Reply

   def Send_Succeed( self, String ):
      "send and hope to get echo from the device"
      import time
      if self.Debug:
         self.Log( 'Send_Succeed( "' + String + '" )' )
      if self.Fast: 
         self.Port.write( String )      
         Reply = self.Port.read( len( String ))
         if Reply != String.upper():
            return 0
      else:
         for Char in String:
            Reply = self.Send_Receive( Char )
            if Reply != Char.upper():
               return 0
      return 1

   def Get( self, N = None ):
      "get string or fixed size response from the device"
      if self.Debug: self.Log( 'Get( N=' + str( N ) + ' )' )
      Result = ''
      if N != None:
         if self.Fast:
            self.Port.write( Repeat( 'n', N ))
            Result = self.Port.read( N )
         else:
            for Dummy in range( N ):
               Response = self.Send_Receive( 'n' )
               Result = Result + Response
      else:
         Response = self.Send_Receive( 'n' )
         if ( Response != ' ' ):
            for Dummy in [ 1, 2, 3 ]:
               Response = Response + self.Send_Receive( 'n' )
            return Response
         else:
            Response = ''
            while ( Response != ' ' ) and ( len( Response ) < 32 ):
               Result = Result + Response
               Response = self.Send_Receive( 'n' )
      if self.Debug: self.Log( 'Get result "%s"' % Result )
      return Result


#############################################################################
#
# Target information
#
#############################################################################

Algorithm_PIC16   = 0
Algorithm_PIC16A  = 1
Algorithm_PIC16B  = 2
Algorithm_PIC18   = 3
Algorithm_PIC16C  = 4
Algorithm_PIC16D  = 5
Algorithm_PIC16E  = 6
Algorithm_PIC16F  = 7
Algorithm_PIC12   = 8
Algorithm_PIC16G  = 9
Algorithm_PIC18A  = 10
Algorithm_PIC16H  = 11
Algorithm_PIC16I  = 12
Algorithm_Name = [ 
   "Algorithm_PIC16",
   "Algorithm_PIC16A",
   "Algorithm_PIC16B",
   "Algorithm_PIC18",
   "Algorithm_PIC16C",
   "Algorithm_PIC16D",
   "Algorithm_PIC16E",
   "Algorithm_PIC16F",
   "Algorithm_PIC12",
   "Algorithm_PIC16G",
   "Algorithm_PIC18A",
   "Algorithm_PIC16H",
   "Algorithm_PIC16I",
]

Region_Code   = 10
Region_Data   = 11
Region_ID     = 12
Region_Device = 13
Region_Fuses  = 14

Region_Name = {
   Region_Code    : "Code",
   Region_Data    : "Data",
   Region_ID      : "ID",
   Region_Device  : "Device",
   Region_Fuses   : "Fuses" }

# fuses must be last for Write_Verify
All_Regions = [
   Region_Code,
   Region_Data, 
   Region_ID,
   Region_Device, 
   Region_Fuses ]
Programming_Regions = [ 
   Region_Code, 
   Region_Data, 
   Region_ID, 
   Region_Fuses ]

_PIC_Types_By_ID    = {}
_PIC_Types_By_ID_18 = {}
_PIC_Types_By_Name  = {}
_PIC_Types_List     = []

class PIC_Range:
   "describes a PIC store region"

   def __init__( self, Base, Start = None, End = None, Ignore = None ):
     if Start == None:
         self.Base = 0
         self.Start = 0
         self.End = Base - 1
         self.Ignore = Ignore
         if Ignore == None:
            self.Ignore = [ 0x3FFF ]
     else:
         self.Base = Base
         self.Start = Start
         self.End = End
         self.Ignore = Ignore
         if Ignore == None:
            self.Ignore = []
     self.Size = ( self.End + 1 ) - self.Start
     
   def Range( self, Reverse = 0 ):
      Result = range( self.Start, self.End + 1 )
      if Reverse:
         Result.reverse()
      return Result
      
   def In( self, Address ):
      return ( Address >= self.Start ) and ( Address <= self.End )

class PIC_EEPROM_14( PIC_Range ):
   "describes 14-bit PIC EEPROM data storage"
   def __init__( self, Size ):
      PIC_Range.__init__( self, 0x2100, 0x2100, 0x2100 + Size - 1, [ 0x00FF ] )

class PIC_EEPROM_16( PIC_Range ):
   "describes 16-bit PIC EEPROM data storage"
   def __init__( self, Size ):
      PIC_Range.__init__( self, 0xF00000, 0xF00000, 0xF00000 + Size - 1, [ 0x00FF ] )

class PIC_Code( PIC_Range ):
   "describes PIC Flash code storage"
   def __init__( self, Size ):
      PIC_Range.__init__( self, Size )
      
class PIC_ID_12( PIC_Range ):
   "12-bit PIC ID storage"
   def __init__( self, Origin, Size ):
      PIC_Range.__init__( self, 0, Origin, Origin+ Size - 1, [ 0x3FFF ] )
      # print "HELLO", self.Base, self.Start, self.End, self.Range(), self.Ignore
         
class PIC_ID_14( PIC_Range ):
   "14-bit PIC ID storage"
   def __init__( self, Size ):
      PIC_Range.__init__( self, 0x2000, 0x2000, 0x2000 + Size - 1, [ 0x3FFF ] )
      # print "HELLO", self.Base, self.Start, self.End, self.Range()
         
class PIC_ID_16( PIC_Range ):
   "16-bit PIC ID storage"
   def __init__( self, Size ):
      PIC_Range.__init__( self, 0x000000, 0x200000, 0x200000 + Size - 1, [ 0xFF ] )
      # print "HELLO", self.Base, self.Start, self.End, self.Range()

P16F87xA_Fixed = Fixed({ 0x2007 : Mask( ONE = 0x1030 ) })

P16F87x_Fixed = Fixed({ 0x2007 : Mask( ONE = 0x0400 ) })

P16F88x_Fixed = Fixed({ 0x2008 : Mask( ONE = 0x38FF ) })

P16F917_Fixed = Fixed({ 0x2007 : Mask( ONE = 0x2000 ) })

P16F630_Fixed = Fixed({ 0x2007 : Mask( ZERO = 0x0E00 ) })

P16F688_Fixed = Fixed({ 0x2007 : Mask( ONE = 0x3000 ) })

P12F629_Fixed = Fixed({ 0x2007 : Mask( ZERO = 0x0E00 ) })

P16F7x_Fixed  = Fixed({ 0x2007 : Mask( ONE = 0x3FA0 ) })

P16F716_Fixed  = Fixed({ 0x2007 : Mask( ONE = 0x1F30 ) })

P16F7x7_Fixed = Fixed({ 
   0x2007 : Mask( ONE = 0x0600 ),
   0x2008 : Mask( ONE = 0x3FDC )
})

P16F818_Fixed = Fixed({ })

P16F628_Fixed = Fixed({ 0x2007 : Mask( ONE = 0x0200 ) })
               
P16F627A_Fixed = Fixed( { 0x2007 : Mask( ONE = 0x1E00 ) })               
P16F628A_Fixed = Fixed( { 0x2007 : Mask( ONE = 0x1E00 ) })               
P16F648A_Fixed = Fixed( { 0x2007 : Mask( ONE = 0x1E00 ) })
               
P18xx2_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xFF ),
   0x300001 : Mask( ZERO = 0xD8 ),
   0x300002 : Mask( ZERO = 0xF0 ),
   0x300003 : Mask( ZERO = 0xF0 ),
   0x300004 : Mask( ZERO = 0xFF ),
   0x300005 : Mask( ZERO = 0xFE ),
   0x300006 : Mask( ZERO = 0x7A ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0xF0 ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xF0 ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0xF0 ),
   0x30000D : Mask( ZERO = 0xBF )   
})

P18xx8_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xFF ),
   0x300001 : Mask( ZERO = 0xD8 ),
   0x300002 : Mask( ZERO = 0xF0 ),
   0x300003 : Mask( ZERO = 0xF0 ),
   0x300004 : Mask( ZERO = 0xFF ),
   0x300005 : Mask( ZERO = 0xFF ),
   0x300006 : Mask( ZERO = 0x7A ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0xF0 ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xF0 ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0xF0 ),
   0x30000D : Mask( ZERO = 0xBF )   
})

P18F1x20_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xFF ),
   0x300001 : Mask( ZERO = 0x30 ),
   0x300002 : Mask( ZERO = 0xF0 ),
   0x300003 : Mask( ZERO = 0xE0 ),
   0x300004 : Mask( ZERO = 0xFF ),
   0x300005 : Mask( ZERO = 0x7F ),
   0x300006 : Mask( ZERO = 0x7A ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0xFC ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xFC ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0xFC ),
   0x30000D : Mask( ZERO = 0xBF )   
})

P18F2x20_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xFF ),
   0x300001 : Mask( ZERO = 0x30 ),
   0x300002 : Mask( ZERO = 0xF0 ),
   0x300003 : Mask( ZERO = 0xE0 ),
   0x300004 : Mask( ZERO = 0xFF ),
   0x300005 : Mask( ZERO = 0x7C ),
   0x300006 : Mask( ZERO = 0x7A ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0xF0 ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xF0 ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0xF0 ),
   0x30000D : Mask( ZERO = 0xBF )   
})

P18Fxx20_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xFF ),
   0x300001 : Mask( ZERO = 0xD8 ),
   0x300002 : Mask( ZERO = 0xF0 ),
   0x300003 : Mask( ZERO = 0xF0 ),
   0x300004 : Mask( ZERO = 0x7C ),
   0x300005 : Mask( ZERO = 0xFC ),
   0x300006 : Mask( ZERO = 0x7A ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0x00 ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0x00 ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0x00 ),
   0x30000D : Mask( ZERO = 0xBF )   
})

P18F2520_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xFF ),
   0x300001 : Mask( ZERO = 0x30 ),
   0x300002 : Mask( ZERO = 0xE0 ),
   0x300003 : Mask( ZERO = 0xE0 ),
   0x300004 : Mask( ZERO = 0xFF ),
   0x300005 : Mask( ZERO = 0x78 ),
   0x300006 : Mask( ZERO = 0x3A ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0xF3 ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xF3 ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0xFC ),
   0x30000D : Mask( ZERO = 0xBF )   
})

Vdd_before_Vpp = 145
Vpp_before_Vdd = 146
Cycle_at_Exit  = 147
Limited_Vdd_before_Vpp = 148
Is_Alias = 149
Has_Code = 150
PGM_Pulldown = 151
Variable_Vdd = 152

class PIC_One_Type:
   "describes a single PICmicro type"

   def __init__(
      self,
      Name = None,
      Shorthands = None,
      Algorithm = None,
      Code = None, Data = None, ID = None, Fuses = None,
      Protect = None,
      ID_Value = None,
      Speed = None,
      Fixed = None,
      Revision_Bits = 5,
      Preserve = Precious( List = [], Default = 0 ),
      Progspec    = None,
      Vdd         = None,
      Vpp         = None,
      Properties  = None,
      Tested      = None      
   ):
      self.Name       = Name
      self.ID_Value   = ID_Value
      self.Shorthands = Shorthands
      self.Progspec   = Progspec
      self.Vpp        = Vpp
      self.Vdd        = Vdd
      self.Properties = Properties
      self.Tested     = Tested
      self.Algorithm  = Algorithm
      self.Speed      = Speed
      self.Preserved  = Preserve
      
      _PIC_Types_By_Name[ Name ] = self
      _PIC_Types_List.append( Name )
      _PIC_Types_List.sort()
      for Short in Shorthands:
         _PIC_Types_By_Name[ Short ] = self
         
      self.IPA = 1
      if ( Algorithm == Algorithm_PIC18 ) | ( Algorithm == Algorithm_PIC18A ):
         if not Is_Alias in self.Properties:
            if _PIC_Types_By_ID_18.has_key( self.ID_Value ):
               raise "duplicate ID %s %s" % ( self.Name, _PIC_Types_By_ID_18[ ID_Value ].Name )
            _PIC_Types_By_ID_18[ ID_Value ] = self
         self.PIC18 = 1
         self.IPA = 2
         # print Name, Revision_Bits
      else:
         if self.ID_Value <> -1:
            _PIC_Types_By_ID[ ID_Value ] = self
         self.PIC18 = 0
      self.PIC12 = 0
      if Algorithm == Algorithm_PIC12:
         self.PIC12 = 1
         
      if ( Algorithm == Algorithm_PIC16 ) or \
      ( Algorithm == Algorithm_PIC16A ) or \
      ( Algorithm == Algorithm_PIC16B ) or \
      ( Algorithm == Algorithm_PIC16C ) or \
      ( Algorithm == Algorithm_PIC16D ) or \
      ( Algorithm == Algorithm_PIC16E ) or \
      ( Algorithm == Algorithm_PIC16F ) or \
      ( Algorithm == Algorithm_PIC16G ) or \
      ( Algorithm == Algorithm_PIC16H ) or \
      ( Algorithm == Algorithm_PIC16I ) :
         Device = PIC_Range( 0x2000, 0x2006, 0x2006 )
         if Fuses == None:
            Fuses  = PIC_Range( 0x2000, 0x2007, 0x2007, Ignore = [ 0x3FFF ] )
      elif ( Algorithm == Algorithm_PIC12 ):
         # wovo
         Device = None
         if ID == None:
            ID = PIC_Range( 0, Code.End + 1, Code.End + 4, Ignore = [ 0x0FFF ] )
         if Fuses == None:
            Fuses  = PIC_Range( 0xFFF, 0xFFF, 0xFFF, Ignore = [ 0x0FFF ] )                 
      elif ( Algorithm == Algorithm_PIC18 ) | ( Algorithm == Algorithm_PIC18A )  :
         Device    = PIC_Range( 0x000000, 0x3FFFFE, 0x3FFFFF )
         if Fuses == None:
            Fuses     = PIC_Range( 0x000000, 0x300000, 0x30000D, Ignore = [] )
         Code.Ignore = [ 0xFF ]
      else:
         raise IOError, 'internal error: invalid algorithm'
      if Data == None:
         Data = PIC_Range( 0, 0, -1 )
      if ID == None:
         ID = PIC_Range( 0, 0, -1 )
      self.Region = {}
      self.Region[ Region_Code   ]  = Code
      self.Region[ Region_Data   ]  = Data
      self.Region[ Region_ID     ]  = ID
      self.Region[ Region_Device ]  = Device
      self.Region[ Region_Fuses  ]  = Fuses
      self.Protect = Protect
      self.Revision_Bits = Revision_Bits
      self.ID_Modulo = 0x01 << self.Revision_Bits
      self.Device_ID = ID_Value
      self.Fuses_Address = 0x2007
      self.Fixed = Fixed
      if ( Algorithm == Algorithm_PIC18 ) | ( Algorithm == Algorithm_PIC18A ):
         self.Factor = 0x100
         self.Stride = 1
         self.Write_Cluster = 8
      else:
         self.Factor = 0x10000
         self.Stride = 2
         self.Write_Cluster = 1
      if Algorithm == Algorithm_PIC16D:
         self.Write_Cluster = 4
      if Algorithm == Algorithm_PIC16F:
         self.Write_Cluster = 4
      self.Write_Block = 8
      if Algorithm == Algorithm_PIC16B:
         self.Write_Block = 8      

   def In_Region( self, Region, Address ):
      # print Address, self.Region[ Region].Start, self.Region[ Region].End
      return ( Address >= self.Region[ Region].Start ) and \
         ( Address <= self.Region[ Region].End )

def PIC_Type_From_Name( Name, Default = None ):
   return _PIC_Types_By_Name.get( Name.lower(), Default )

def PIC_Type_From_ID( ID, Default = None ):
   return _PIC_Types_By_ID.get( ID, Default )
   
def PIC_Type_From_ID_18( ID, Default = None ):
   return _PIC_Types_By_ID_18.get( ID, Default )
   
Preserve_1K = Precious(
   Default = 0x3FFF,
   List = [( 0x2007, 0x3000 ), ( 0x3FF , 0x3FFF )])     
   
class Chip_Status:

   def __init__( self, Tested, Comment = '' ):
      self.Tested = Tested
      self.Comment = Comment
      
   def Short( self ):
      if self.Tested:
         T = 'OK'
      else:
         T = 'impl'
      if self.Comment <> '':
         T = T + " #"
      return T      
      
   def Text( self ):
      if self.Tested:
         T = 'Tested with a real chip.'
      else:
         T = 'Implemented from specs, NOT tested with a real chip.'
      if self.Comment <> '':
         T = T + " " +  self.Comment
      return T
      
Chip_Status_OK         = Chip_Status( 1 )   
Chip_Status_Specs_Only = Chip_Status( 0 )
Chip_Status_10F        = Chip_Status( 1, "This chip requires a power cycle to start automatically after programming. " )

PIC_One_Type(
   Name        = '10f200',
   Shorthands  = [ 'f200' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 256, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 256 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41228D",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_10F
   )

PIC_One_Type(
   Name        = '10f204',
   Shorthands  = [ 'f204' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 512, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 512 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41228D",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_10F
   )
   
PIC_One_Type(
   Name        = '10f202',
   Shorthands  = [ 'f202' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 256, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 256 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41228D",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_10F
   )

PIC_One_Type(
   Name        = '10f206',
   Shorthands  = [ 'f206' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 512, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 512 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41228D",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_10F
   )
   
PIC_One_Type(
   Name        = '10f220',
   Shorthands  = [ 'f220' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 256, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 256 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41266B",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '10f222',
   Shorthands  = [ 'f222' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 512, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 512 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41266B",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '12f508',
   Shorthands  = [ 'f508' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 512, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 512 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41227D",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '12f509',
   Shorthands  = [ 'f509' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 1024, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 1024 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41227D",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '12f510',
   Shorthands  = [ 'f510' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 1024, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 1024 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41257A",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f505',
   Shorthands  = [ 'f505' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 512, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   Preserve    = Precious( Default = 0xFFF, List = [( 1024 - 1, 0xFFF )]),
   ID_Value    = -1,
   Progspec    = "DS41226E",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f54',
   Shorthands  = [ 'f54' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 1024, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   ID_Value    = -1,
   Progspec    = "DS41207C",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f57',
   Shorthands  = [ 'f57' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 2048, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   ID_Value    = -1,
   Progspec    = "DS41208B",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f59',
   Shorthands  = [ 'f59' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 2048, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0FE0 ) }),
   ID_Value    = -1,
   Progspec    = "DS41243B",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status( 1, "Note the different pinout! " )
   )
   
PIC_One_Type(
   Name        = '12f609',
   Shorthands  = [ 'f609' ],
   Algorithm   = Algorithm_PIC16H,
   Code        = PIC_Range( 1024 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0040,   
   Fixed       = Fixed({ 0x2007 : Mask( ONE = 0x3C00 ) }),
   Preserve    = Precious( Default = 0x20CF, List = [( 0x2008, 0x3FFF )]),
   ID_Value    = 0x2240,
   Progspec    = "DS41284B",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '12f615',
   Shorthands  = [ 'f615' ],
   Algorithm   = Algorithm_PIC16H,
   Code        = PIC_Range( 1024 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0040,   
   Fixed       = Fixed({ 0x2007 : Mask( ONE = 0x3C00 ) }),
   Preserve    = Precious( Default = 0x20CF, List = [( 0x2008, 0x3FFF )]),
   ID_Value    = 0x2180,
   Progspec    = "DS41284B",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '16f610',
   Shorthands  = [ 'f610' ],
   Algorithm   = Algorithm_PIC16H,
   Code        = PIC_Range( 1024 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0040,   
   Fixed       = Fixed({ 0x2007 : Mask( ONE = 0x3C00 ) }),
   Preserve    = Precious( Default = 0x20CF, List = [( 0x2008, 0x3FFF )]),
   ID_Value    = 0x2260,
   Progspec    = "DS41284B",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '16f616',
   Shorthands  = [ 'f616' ],
   Algorithm   = Algorithm_PIC16H,
   Code        = PIC_Range( 2048 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0040,   
   Fixed       = Fixed({ 0x2007 : Mask( ONE = 0x3C00 ) }),
   Preserve    = Precious( Default = 0x20CF, List = [( 0x2008, 0x3FFF )]),
   ID_Value    = 0x1240,
   Progspec    = "DS41284B",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )
   
Preserve_1K = Precious(
   Default = 0x3FFF,
   List = [( 0x2007, 0x3000 ), ( 0x3FF , 0x3FFF )])     

PIC_One_Type(
   Name        = '12f629',
   Shorthands  = [ 'f629', '629' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 1024 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0180,
   ID_Value    = 0x0F80,
   Fixed       = P12F629_Fixed,
   Preserve    = Preserve_1K,
   Progspec    = "DS41191D",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '12f675',
   Shorthands  = [ 'f675', '675' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 1024 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0180,
   ID_Value    = 0x0FC0,
   Fixed       = P12F629_Fixed,
   Preserve    = Preserve_1K,
   Progspec    = "DS41191D",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f630',
   Shorthands  = [ 'f630', '630' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 1024 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0180,
   ID_Value    = 0x10C0,
   Fixed       = P16F630_Fixed,
   Preserve    = Preserve_1K,
   Progspec    = "DS41191D",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '16f676',
   Shorthands  = [ 'f676', '676' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 1024 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0180,
   ID_Value    = 0x10E0,
   Fixed       = P16F630_Fixed,
   Preserve    = Preserve_1K,
   Progspec    = "DS41191D",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f684',
   Shorthands  = [ 'f684', '684' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 2048 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x1080,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f685',
   Shorthands  = [ 'f685', '685' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 2048 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x04A0,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f687',
   Shorthands  = [ 'f687', '687' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 4096 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x1320,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f688',
   Shorthands  = [ 'f688', '688' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 4096 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x1180,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f689',
   Shorthands  = [ 'f689', '689' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 4096 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x1340,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f690',
   Shorthands  = [ 'f690', '690' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 4096 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x1400,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '12f635',
   Shorthands  = [ 'f635', '635' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 1024 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x0FA0,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f631',
   Shorthands  = [ 'f631', '631' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 1024 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x1420,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '12f683',
   Shorthands  = [ 'f683', '683' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 2048 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x0460,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f636',
   Shorthands  = [ 'f636', '636' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 2048 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x10A0,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f639',
   Shorthands  = [ 'f639', '639' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 2048 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x10A0,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Is_Alias, Has_Code ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f677',
   Shorthands  = [ 'f677', '677' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Range( 2048 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x00C0,
   ID_Value    = 0x1440,
   Fixed       = P16F688_Fixed,
   Progspec    = "DS41204G",
   Vpp         = ( 10.00, 13.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16c84',
   Shorthands  = [ 'c84' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Range( 1024 ),
   Data        = PIC_EEPROM_14( 64 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0x2007 : Mask( ONE = 0x3FE0 ) }),
   ID_Value    = -1,
   Progspec    = "unknown",
   Vpp         = ( 12.00, 14.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f83',
   Shorthands  = [ 'f83', '83' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 512 ),
   Data        = PIC_EEPROM_14( 64 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3FF0,
   ID_Value    = -1,
   Progspec    = "DS30262e",
   Vpp         = ( 12.00, 14.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f84',
   Shorthands  = [ 'f84', 'x84' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 1024 ),
   Data        = PIC_EEPROM_14( 64 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3FF0,
   ID_Value    = -1,
   Progspec    = "DS30262e",
   Vpp         = ( 12.00, 14.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f84a',
   Shorthands  = [ 'f84a', '84a' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 1024 ),
   Data        = PIC_EEPROM_14( 64 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3FF0,
   ID_Value    = 0x0560,
   Progspec    = "DS30262e",
   Vpp         = ( 12.00, 14.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f627',
   Shorthands  = [ 'f627', '627' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 1024 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3D00,
   ID_Value    = 0x07A0, # actual value differs from the datasheet!
   Speed       = 80,
   Fixed       = P16F628_Fixed,
   Progspec    = "DS30034d",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, PGM_Pulldown ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f627a',
   Shorthands  = [ 'f627a', '627a' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Code( 1024 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3D00,
   ID_Value    = 0x1040, # actual value differs from the datasheet!
   Speed       = 80,
   Fixed       = P16F628_Fixed,
   Progspec    = "DS41196g",
   Vpp         = ( 10.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, PGM_Pulldown ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f628',
   Shorthands  = [ 'f628', '628' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 2048 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3D00,
   ID_Value    = 0x07C0, # actual value differs from the datasheet!
   Speed       = 80,
   Fixed       = P16F628_Fixed,
   Progspec    = "DS30034d",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, PGM_Pulldown ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f628a',
   Shorthands  = [ 'f628a', '628a' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Code( 2048 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x2100,
   ID_Value    = 0x1060,
   Speed       = 80,
   Fixed       = P16F628A_Fixed,
   Progspec    = "DS41196g",
   Vpp         = ( 10.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, PGM_Pulldown ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f648a',
   Shorthands  = [ 'f648a', '648a' ],
   Algorithm   = Algorithm_PIC16C,
   Code        = PIC_Code( 4096 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x2100,
   ID_Value    = 0x1100, 
   Speed       = 80,
   Fixed       = P16F648A_Fixed,
   Progspec    = "DS41196g",
   Vpp         = ( 10.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, PGM_Pulldown ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f818',
   Shorthands  = [ 'f818', '818' ],
   Algorithm   = Algorithm_PIC16D,
   Code        = PIC_Code( 1024 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3100,
   ID_Value    = 0x04C0,
   Revision_Bits = 4,
   Fixed       = P16F818_Fixed,
   Progspec    = "DS39603c",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f819',
   Shorthands  = [ 'f819', '819' ],
   Algorithm   = Algorithm_PIC16D,
   Code        = PIC_Code( 2048 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3100,
   ID_Value    = 0x04E0,
   Revision_Bits = 4,
   Fixed       = P16F818_Fixed,
   Progspec    = "DS39603c",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f72',
   Shorthands  = [ 'f72', '72' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 4096 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x00A0,
   Speed       = 10,
   Fixed       = P16F7x_Fixed,
   Progspec    = "DS39588a",
   Vpp         = ( 12.75, 13.25 ),
   Vdd         = ( 4.75, 5.25 ),
   Properties  = [ Vdd_before_Vpp, Variable_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f73',
   Shorthands  = [ 'f73', '73' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 4096 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x0600,
   Speed       = 10,
   Fixed       = P16F7x_Fixed,
   Progspec    = "DS30324b",
   Vpp         = ( 12.75, 13.25 ),
   Vdd         = ( 4.75, 5.25 ),
   Properties  = [ Vdd_before_Vpp, Variable_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f74',
   Shorthands  = [ 'f74', '74' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 4096 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x0620,
   Speed       = 10,
   Fixed       = P16F7x_Fixed,
   Progspec    = "DS30324b",
   Vpp         = ( 12.75, 13.25 ),
   Vdd         = ( 4.75, 5.25 ),
   Properties  = [ Vdd_before_Vpp, Variable_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f76',
   Shorthands  = [ 'f76', '76' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 8192 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x0640,
   Speed       = 10,
   Fixed       = P16F7x_Fixed,
   Progspec    = "DS30324b",
   Vpp         = ( 12.75, 13.25 ),
   Vdd         = ( 4.75, 5.25 ),
   Properties  = [ Vdd_before_Vpp, Variable_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f77',
   Shorthands  = [ 'f77', '77' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 8192 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x0660,
   Speed       = 10,
   Fixed       = P16F7x_Fixed,
   Progspec    = "DS30324b",
   Vpp         = ( 12.75, 13.25 ),
   Vdd         = ( 4.75, 5.25 ),
   Properties  = [ Vdd_before_Vpp, Variable_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f716',
   Shorthands  = [ 'f716', '716' ],
   Algorithm   = Algorithm_PIC16F,
   Code        = PIC_Code( 2048 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x1140,
   Speed       = 10,
   Fixed       = P16F716_Fixed,
   Progspec    = "DS40245b",
   Vpp         = ( 11.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status( 1, "==> Read the chip errata!" )
   )

PIC_One_Type(
   Name        = '16f737',
   Shorthands  = [ 'f737', '737' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 4096 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x0BA0,
   Speed       = 10,
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   Fixed       = P16F7x7_Fixed,
   Progspec    = "DS30492B",
   Vpp         = ( 12.75, 13.25 ),
   Vdd         = ( 4.75, 5.25 ),
   Properties  = [ Vdd_before_Vpp, Variable_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f747',
   Shorthands  = [ 'f747', '747' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 4096 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x0BE0,
   Speed       = 10,
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   Fixed       = P16F7x7_Fixed,
   Progspec    = "DS30492B",
   Vpp         = ( 12.75, 13.25 ),
   Vdd         = ( 4.75, 5.25 ),
   Properties  = [ Vdd_before_Vpp, Variable_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f767',
   Shorthands  = [ 'f767', '767' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 8192 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x0EA0,
   Speed       = 10,
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   Fixed       = P16F7x7_Fixed,
   Progspec    = "DS30492B",
   Vpp         = ( 12.75, 13.25 ),
   Vdd         = ( 4.75, 5.25 ),
   Properties  = [ Vdd_before_Vpp, Variable_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f777',
   Shorthands  = [ 'f777', '777' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 8192 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x0DE0,
   Speed       = 10,
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   Fixed       = P16F7x7_Fixed,
   Progspec    = "DS30492B",
   Vpp         = ( 12.75, 13.25 ),
   Vdd         = ( 4.75, 5.25 ),
   Properties  = [ Vdd_before_Vpp, Variable_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f785',
   Shorthands  = [ 'f785', '785' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 2048 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x1200,
   Speed       = 10,
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   Fixed       = Fixed({ 0x2007 : Mask( ONE = 0x3000 ) }),
   Progspec    = "DS41237C",
   Vpp         = ( 12.00, 14.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16hv785',
   Shorthands  = [ 'hv785' ],
   Algorithm   = Algorithm_PIC16A,
   Code        = PIC_Code( 2048 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x1220,
   Speed       = 10,
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   Fixed       = Fixed({ 0x2007 : Mask( ONE = 0x3000 ) }),
   Progspec    = "DS41237C",
   Vpp         = ( 12.00, 14.00 ),
   Vdd         = ( 4.50, 4.95 ),
   Properties  = [ Vpp_before_Vdd ],
   Tested      = Chip_Status_Specs_Only
   )

PIC_One_Type(
   Name        = '16f870',
   Shorthands  = [ 'f870', '870' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 2048 ),
   Data        = PIC_EEPROM_14( 64 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x0D00,
   Fixed       = P16F87x_Fixed,
   Progspec    = "DS39025f",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f871',
   Shorthands  = [ 'f871', '871' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 2048 ),
   Data        = PIC_EEPROM_14( 64 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x0D20,
   Fixed       = P16F87x_Fixed,
   Progspec    = "DS39025f",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f872',
   Shorthands  = [ 'f872', '872' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 2048 ),
   Data        = PIC_EEPROM_14( 64 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x08E0,
   Fixed       = P16F87x_Fixed,
   Progspec    = "DS39025f",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f873',
   Shorthands  = [ 'f873', '873' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 4096 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x0960,
   Fixed       = P16F87x_Fixed,
   Progspec    = "DS39025f",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f873a',
   Shorthands  = [ 'f873a', '873a' ],
   Algorithm   = Algorithm_PIC16B,
   Code        = PIC_Code( 4096 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x0E40,
   Fixed       = P16F87xA_Fixed,
   Progspec    = "DS39589b",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f874',
   Shorthands  = [ 'f874', '874' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 4096 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x0920,
   Fixed       = P16F87x_Fixed,
   Progspec    = "DS39025f",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f874a',
   Shorthands  = [ 'f874a', '874a' ],
   Algorithm   = Algorithm_PIC16B,
   Code        = PIC_Code( 4096 ),
   Data        = PIC_EEPROM_14( 128 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x0010,
   ID_Value    = 0x0E60,
   Fixed       = P16F87xA_Fixed,
   Progspec    = "DS39589b",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f876',
   Shorthands  = [ 'f876', '876' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x09E0,
   Fixed       = P16F87x_Fixed,
   Progspec    = "DS39025f",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f876a',
   Shorthands  = [ 'f876a', '876a' ],
   Algorithm   = Algorithm_PIC16B,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x0E00,
   Fixed       = P16F87xA_Fixed,
   Progspec    = "DS39589b",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f877',
   Shorthands  = [ 'f877', '877' ],
   Algorithm   = Algorithm_PIC16,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x09A0,
   Fixed       = P16F87x_Fixed,
   Progspec    = "DS39025f",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f877a',
   Shorthands  = [ 'f877a', '877a' ],
   Algorithm   = Algorithm_PIC16B,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x0E20,
   Fixed       = P16F87xA_Fixed,
   Progspec    = "DS39589b",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f87',
   Shorthands  = [ 'f87', '87' ],
   Algorithm   = Algorithm_PIC16D,
   Code        = PIC_Code( 4096 ),
   Data        = PIC_EEPROM_14( 256 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x2100,
   ID_Value    = 0x0720,
   Fixed       = Fixed({ 0x2008 : Mask( ONE = 0x3FFC )}),
   Progspec    = "DS39607b",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f88',
   Shorthands  = [ 'f88', '88' ],
   Algorithm   = Algorithm_PIC16D,
   Code        = PIC_Code( 4096 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x2100,
   ID_Value    = 0x0760,
   Fixed       = Fixed({ 0x2008 : Mask( ONE = 0x3FFC )}),
   Progspec    = "DS39607b",
   Vpp         = ( 9.00, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f882',
   Shorthands  = [ 'f882', '882' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 2048 ),
   Data        = PIC_EEPROM_14( 128 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x2000,
   Fixed       = P16F88x_Fixed,
   Progspec    = "DS41287c",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f883',
   Shorthands  = [ 'f883', '883' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 4096 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x2020,
   Fixed       = P16F88x_Fixed,
   Progspec    = "DS41287c",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f884',
   Shorthands  = [ 'f884', '884' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 4096 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x2040,
   Fixed       = P16F88x_Fixed,
   Progspec    = "DS41287c",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f886',
   Shorthands  = [ 'f886', '886' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x2060,
   Fixed       = P16F88x_Fixed,
   Progspec    = "DS41287c",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f887',
   Shorthands  = [ 'f887', '887' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x2080,
   Fixed       = P16F88x_Fixed,
   Progspec    = "DS41287c",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f913',
   Shorthands  = [ 'f913', '913' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x13E0,
   Fixed       = P16F917_Fixed,
   Progspec    = "DS41244E",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f914',
   Shorthands  = [ 'f914', '914' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x13C0,
   Fixed       = P16F917_Fixed,
   Progspec    = "DS41244E",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f916',
   Shorthands  = [ 'f916', '916' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x13A0,
   Fixed       = P16F917_Fixed,
   Progspec    = "DS41244E",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f917',
   Shorthands  = [ 'f917', '917' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x1380,
   Fixed       = P16F917_Fixed,
   Progspec    = "DS41244E",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f946',
   Shorthands  = [ 'f946', '946' ],
   Algorithm   = Algorithm_PIC16G,
   Code        = PIC_Code( 8192 ),
   Data        = PIC_EEPROM_14( 256 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x1460,
   Fixed       = P16F917_Fixed,
   Progspec    = "DS41244E",
   Vpp         = ( 10.00, 12.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )
   
P16F722_Fixed = Fixed({ 
   0x2007 : Mask( ONE = 0x0880 ),
   0x2008 : Mask( ONE = 0x3FCF )
})   

PIC_One_Type(
   Name        = '16f722',
   Shorthands  = [ 'f722', '722' ],
   Algorithm   = Algorithm_PIC16I,
   Code        = PIC_Code( 2048 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x1880,
   Fixed       = P16F722_Fixed,
   Progspec    = "DS41332B",
   Vpp         = ( 8.00, 9.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f723',
   Shorthands  = [ 'f723', '723' ],
   Algorithm   = Algorithm_PIC16I,
   Code        = PIC_Code( 4096 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x1860,
   Fixed       = P16F722_Fixed,
   Progspec    = "DS41332B",
   Vpp         = ( 8.00, 9.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f724',
   Shorthands  = [ 'f724', '724' ],
   Algorithm   = Algorithm_PIC16I,
   Code        = PIC_Code( 4096 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x1840,
   Fixed       = P16F722_Fixed,
   Progspec    = "DS41332B",
   Vpp         = ( 8.00, 9.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f726',
   Shorthands  = [ 'f726', '726' ],
   Algorithm   = Algorithm_PIC16I,
   Code        = PIC_Code( 8192 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x1820,
   Fixed       = P16F722_Fixed,
   Progspec    = "DS41332B",
   Vpp         = ( 8.00, 9.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f727',
   Shorthands  = [ 'f727', '727' ],
   Algorithm   = Algorithm_PIC16I,
   Code        = PIC_Code( 8192 ),
   Fuses       = PIC_Range( 0x2000, 0x2007, 0x2008 ),
   ID          = PIC_ID_14( 4 ),
   Protect     = 0x3130,
   ID_Value    = 0x1800,
   Fixed       = P16F722_Fixed,
   Progspec    = "DS41332B",
   Vpp         = ( 8.00, 9.00 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vpp_before_Vdd, Limited_Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '16f526',
   Shorthands  = [ 'f526' ],
   Algorithm   = Algorithm_PIC12,
   Code        = PIC_Range( 1024, Ignore = [ 0x0FFF ] ),
   Protect     = 0x000F,
   Fixed       = Fixed({ 0xFFF : Mask( ONE = 0x0F00 ) }),
   ID_Value    = -1,
   Progspec    = "DS413137B",
   Vpp         = ( 12.50, 13.50 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f242',
   Shorthands  = [ 'f242', '242' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0480,
   Fixed       = P18xx2_Fixed,
   Progspec    = "DS39576b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f248',
   Shorthands  = [ 'f248', '248' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0800,
   Fixed       = P18xx8_Fixed,
   Progspec    = "DS39576b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f252',
   Shorthands  = [ 'f252', '252' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0400,
   Fixed       = P18xx2_Fixed,
   Progspec    = "DS39576b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f258',
   Shorthands  = [ 'f258', '258' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0840,
   Fixed       = P18xx8_Fixed,
   Progspec    = "DS39576b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f442',
   Shorthands  = [ 'f442', '442' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x04A0,
   Fixed       = P18xx2_Fixed,
   Progspec    = "DS39576b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f448',
   Shorthands  = [ 'f448', '448' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0820,
   Fixed       = P18xx8_Fixed,
   Progspec    = "DS39576b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f452',
   Shorthands  = [ 'f452', '452' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0420,
   Fixed       = P18xx2_Fixed,
   Progspec    = "DS39576b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f458',
   Shorthands  = [ 'f458', '458' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0860,
   Fixed       = P18xx8_Fixed,
   Progspec    = "DS39576b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f1220',
   Shorthands  = [ 'f1220', '1220' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 2 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x07E0,
   Fixed       = P18F1x20_Fixed,
   Progspec    = "DS39592e",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2220',
   Shorthands  = [ 'f2220', '2220' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 2 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0580,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39592e",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4220',
   Shorthands  = [ 'f4220', '4220' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 2 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x05A0,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39592e",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f1320',
   Shorthands  = [ 'f1320', '1320' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 4 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x07C0,
   Fixed       = P18F1x20_Fixed,
   Progspec    = "DS39592e",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2320',
   Shorthands  = [ 'f2320', '2320' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 4 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0500,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39592e",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4320',
   Shorthands  = [ 'f4320', '4320' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 8 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0520,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39592e",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )  

PIC_One_Type(
   Name        = '18f2439',
   Shorthands  = [ 'f2439', '2439' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 12 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0480,
   Fixed       = P18xx2_Fixed,
   Progspec    = "DS39592b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Has_Code, Is_Alias ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2539',
   Shorthands  = [ 'f2539', '2539' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 24 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0400,
   Fixed       = P18xx2_Fixed,
   Progspec    = "DS39592b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Has_Code, Is_Alias ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4439',
   Shorthands  = [ 'f4439', '4439' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 12 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x04A0,
   Fixed       = P18xx2_Fixed,
   Progspec    = "DS39592b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Has_Code, Is_Alias ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4539',
   Shorthands  = [ 'f4539', '4539' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 28 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0420,
   Fixed       = P18xx2_Fixed,
   Progspec    = "DS39592b",
   Vpp         = ( 9.00, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Has_Code, Is_Alias ],
   Tested      = Chip_Status_OK
   )
   
P16F722_Fixed = Fixed({ 
   0x2007 : Mask( ONE = 0x0880 ),
   0x2008 : Mask( ONE = 0x3FCF )
})    
DS39622_Fixed  = Fixed({
   0x300000 : Mask( ZERO = 0xFF ),
   0x300002 : Mask( ZERO = 0xE0 ),
   0x300004 : Mask( ZERO = 0xFF ),
   0x300005 : Mask( ZERO = 0x79 ),
   0x300006 : Mask( ZERO = 0x38 ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xFF ),
   0x30000B : Mask( ZERO = 0x3F ),
   0x30000C : Mask( ZERO = 0xFF ),
   0x30000D : Mask( ZERO = 0xBF ),
})

PIC_One_Type(
   Name        = '18f2221',
   Shorthands  = [ 'f2221', '2221' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 4 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2160,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_Specs_Only
   )

PIC_One_Type(
   Name        = '18f2321',
   Shorthands  = [ 'f2321', '2321' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 8 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2120,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2410',
   Shorthands  = [ 'f2410', '2410' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 16 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1160,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2420',
   Shorthands  = [ 'f2420', '2420' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   Revision_Bits = 4,
   ID_Value    = 0x1140,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2423',
   Shorthands  = [ 'f2423', '2423' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   Revision_Bits = 4,
   ID_Value    = 0x1150,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

P18F2450_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xC0 ),
   0x300001 : Mask( ZERO = 0x30 ),
   0x300002 : Mask( ZERO = 0xC0 ),
   0x300003 : Mask( ZERO = 0xE0 ),
   0x300004 : Mask( ZERO = 0xFF ),
   0x300005 : Mask( ZERO = 0x78 ),
   0x300006 : Mask( ZERO = 0x12 ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0xF3 ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xF3 ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0xFC ),
   0x30000D : Mask( ZERO = 0xBF )   
})

PIC_One_Type(
   Name        = '18f2450',
   Shorthands  = [ 'f2450', '2450' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 16 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2420,
   Fixed       = P18F2450_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

P18F2455_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xC0 ),
   0x300001 : Mask( ZERO = 0x30 ),
   0x300002 : Mask( ZERO = 0xC0 ),
   0x300003 : Mask( ZERO = 0xE0 ),
   0x300004 : Mask( ZERO = 0xFF ),
   0x300005 : Mask( ZERO = 0x78 ),
   0x300006 : Mask( ZERO = 0x1A ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0xF3 ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xF3 ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0xFC ),
   0x30000D : Mask( ZERO = 0xBF )   
})

PIC_One_Type(
   Name        = '18f2455',
   Shorthands  = [ 'f2455', '2455' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 24 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1260,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2458',
   Shorthands  = [ 'f2458', '2458' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 24 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2A60,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2480',
   Shorthands  = [ 'f2480', '2480' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1AE0,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2510',
   Shorthands  = [ 'f2510', '2510' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1120,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2515',
   Shorthands  = [ 'f2515', '2515' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 48 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0CE0,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2520',
   Shorthands  = [ 'f2520', '2520' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   Revision_Bits = 4,
   ID_Value    = 0x1100,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2523',
   Shorthands  = [ 'f2523', '2523' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1110,
   Revision_Bits = 4,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2525',
   Shorthands  = [ 'f2525', '2525' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 48 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0CC0,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2550',
   Shorthands  = [ 'f2550', '2550' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1240,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2553',
   Shorthands  = [ 'f2553', '2553' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2A40,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2580',
   Shorthands  = [ 'f2580', '2580' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1AC0,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '18f2585',
   Shorthands  = [ 'f2585', '2585' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 48 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0EE0,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f2610',
   Shorthands  = [ 'f2610', '2610' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 64 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0CA0,
   Fixed       = P18F2455_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '18f2620',
   Shorthands  = [ 'f2620', '2620' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 64 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0C80,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )   

PIC_One_Type(
   Name        = '18f2680',
   Shorthands  = [ 'f2680', '2680' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 64 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0EC0,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )   

PIC_One_Type(
   Name        = '18f2682',
   Shorthands  = [ 'f2682', '2682' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 80 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2700,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )   

PIC_One_Type(
   Name        = '18f2685',
   Shorthands  = [ 'f2685', '2685' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 96 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2720,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )   

PIC_One_Type(
   Name        = '18f4221',
   Shorthands  = [ 'f4221', '4221' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 4 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2140,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4321',
   Shorthands  = [ 'f4321', '4321' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 8 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2100,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4410',
   Shorthands  = [ 'f4410', '4410' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 16 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x10E0,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4420',
   Shorthands  = [ 'f4420', '4420' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x10C0,
   Revision_Bits = 4,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4423',
   Shorthands  = [ 'f4423', '4423' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 2 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x10D0,
   Revision_Bits = 4,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4450',
   Shorthands  = [ 'f4450', '4450' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 16 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2400,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4455',
   Shorthands  = [ 'f4455', '4455' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 24 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1220,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4458',
   Shorthands  = [ 'f4458', '4458' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 24 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2A20,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4480',
   Shorthands  = [ 'f4480', '4480' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1AA0,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4510',
   Shorthands  = [ 'f4510', '4510' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x10A0,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4515',
   Shorthands  = [ 'f4515', '4515' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 48 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0C60,
   Fixed       = P18F2x20_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '18f4520',
   Shorthands  = [ 'f4520', '4520' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1080,
   Revision_Bits = 4,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4523',
   Shorthands  = [ 'f4523', '4523' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1090,
   Revision_Bits = 4,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4525',
   Shorthands  = [ 'f4525', '4525' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 48 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0C40,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '18f4550',
   Shorthands  = [ 'f4550', '4550' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1200,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4553',
   Shorthands  = [ 'f4553', '4553' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2A00,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4580',
   Shorthands  = [ 'f4580', '4580' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x1A80,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4585',
   Shorthands  = [ 'f4585', '4585' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 48 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0EA0,
   Fixed       = P18F2520_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4610',
   Shorthands  = [ 'f4610', '4610' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 64 * 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0C20,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4620',
   Shorthands  = [ 'f4620', '4620' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 64 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0C00,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '18f4680',
   Shorthands  = [ 'f4680', '4680' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 64 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0E80,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4682',
   Shorthands  = [ 'f4682', '4682' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 80 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2740,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )
   
PIC_One_Type(
   Name        = '18f4685',
   Shorthands  = [ 'f4685', '4685' ],
   Algorithm   = Algorithm_PIC18A,
   Code        = PIC_Code( 96 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x2760,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39622k",
   Vpp         = ( 9.50, 12.50 ),
   Vdd         = ( 3.00, 5.50 ),
   Properties  = [ Vdd_before_Vpp, Cycle_at_Exit ],
   Tested      = Chip_Status_OK
   )   

PIC_One_Type(
   Name        = '18f6520',
   Shorthands  = [ 'f6520', '6520' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0B20,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39583b",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_Specs_Only
   )

PIC_One_Type(
   Name        = '18f6620',
   Shorthands  = [ 'f6620', '6620' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0660,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39583b",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_Specs_Only
   )

PIC_One_Type(
   Name        = '18f6720',
   Shorthands  = [ 'f6720', '6720' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 64 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0620,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39583b",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_Specs_Only
   )

PIC_One_Type(
   Name        = '18f8520',
   Shorthands  = [ 'f8520', '8520' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0B00,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39583b",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_Specs_Only
   )

PIC_One_Type(
   Name        = '18f8620',
   Shorthands  = [ 'f8620', '8620' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 32 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0640,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39583b",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_Specs_Only
   )

PIC_One_Type(
   Name        = '18f8720',
   Shorthands  = [ 'f8720', '8720' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 64 * 1024 ),
   Data        = PIC_EEPROM_16( 1024 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0600,
   Fixed       = DS39622_Fixed,
   Progspec    = "DS39583b",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_Specs_Only
   )
   
P18Fx431_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xFF ),
   0x300001 : Mask( ZERO = 0x30 ),
   0x300002 : Mask( ZERO = 0xF0 ),
   0x300003 : Mask( ZERO = 0xC0 ),
   0x300004 : Mask( ZERO = 0xC3 ),
   0x300005 : Mask( ZERO = 0x62 ),
   0x300006 : Mask( ZERO = 0x7A ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0xF0 ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xF0 ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0xF0 ),
   0x30000D : Mask( ZERO = 0xBF )   
})

P18Fx331_Fixed = Fixed({
   0x300000 : Mask( ZERO = 0xFF ),
   0x300001 : Mask( ZERO = 0x30 ),
   0x300002 : Mask( ZERO = 0xF0 ),
   0x300003 : Mask( ZERO = 0xC0 ),
   0x300004 : Mask( ZERO = 0xC3 ),
   0x300005 : Mask( ZERO = 0x62 ),
   0x300006 : Mask( ZERO = 0x7A ),
   0x300007 : Mask( ZERO = 0xFF ),
   0x300008 : Mask( ZERO = 0xF3 ),
   0x300009 : Mask( ZERO = 0x3F ),
   0x30000A : Mask( ZERO = 0xF3 ),
   0x30000B : Mask( ZERO = 0x1F ),
   0x30000C : Mask( ZERO = 0xF3 ),
   0x30000D : Mask( ZERO = 0xBF )   
})

PIC_One_Type(
   Name        = '18f2331',
   Shorthands  = [ 'f2331', '2331' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 8 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x08E0,
   Fixed       = P18Fx331_Fixed,
   Progspec    = "DS30500a",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status( 1, "Note the extra Vdd pin! " )
   )

PIC_One_Type(
   Name        = '18f2431',
   Shorthands  = [ 'f2431', '2431' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x08C0,
   Fixed       = P18Fx431_Fixed,
   Progspec    = "DS30500a",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status( 1, "Note the extra Vdd pin! " )
   )

PIC_One_Type(
   Name        = '18f4331',
   Shorthands  = [ 'f4331', '4331' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 8 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x08A0,
   Fixed       = P18Fx331_Fixed,
   Progspec    = "DS30500a",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )

PIC_One_Type(
   Name        = '18f4431',
   Shorthands  = [ 'f4431', '4431' ],
   Algorithm   = Algorithm_PIC18,
   Code        = PIC_Code( 16 * 1024 ),
   Data        = PIC_EEPROM_16( 256 ),
   ID          = PIC_ID_16( 8 ),
   Protect     = 0x3130,
   ID_Value    = 0x0880,
   Fixed       = P18Fx431_Fixed,
   Progspec    = "DS30500a",
   Vpp         = ( 9.50, 13.25 ),
   Vdd         = ( 4.50, 5.50 ),
   Properties  = [ Vdd_before_Vpp ],
   Tested      = Chip_Status_OK
   )


#############################################################################
#
# Console abstraction
#
#############################################################################

class Dos_Console:
   def __init__( self ):
      self.Erase = 0

   def Beep( self ):
      try:
         import winsound
         winsound.Beep( 440, 400 )
      except:
         self.Print( "sorry, could not beep" )

   def Print( self, String, Progress = 0 ):
      import sys
      if self.Erase:
         sys.stdout.write( "\r%60s\r" % '' )
         self.Erase = 0
      self.Erase = Progress
      sys.stdout.write( String )
      if not Progress:
         sys.stdout.write( '\n' )
      sys.stdout.flush()

   def Print_String( self, String ):
      import sys
      sys.stdout.write( String )
      sys.stdout.flush()

   def Set_Raw( self ):
      import os
      if os.name == 'nt':
         pass
      elif os.name == 'posix':
         # Untested code derived from the Python FAQ....
         import termios, TERMIOS, sys
         self.fd = sys.stdin.fileno()
         self.Old_Attr = termios.tcgetattr( self.fd )
         new = termios.tcgetattr( self.fd )
         new[3] = new[3] & ~TERMIOS.ICANON & ~TERMIOS.ECHO
         new[6][TERMIOS.VMIN] = 1
         new[6][TERMIOS.VTIME] = 0
         termios.tcsetattr( self.fd, TERMIOS.TCSANOW, new )
      else:
         raise IOError, "TTY not implemented for %s" % sys.platform

   def Set_Cooked( self ):
      import os
      if os.name == 'posix':
         import termios, TERMIOS, sys
         termios.tcsetattr( self.fd, TERMIOS.TCSAFLUSH, self.Old_Attr )

   def Get_Key( self ):
      import os
      if os.name == 'nt':
         import msvcrt
         if not msvcrt.kbhit():
            return ''
         while 1:
            z = msvcrt.getch()
            if z == '\0' or z == '\xe0':
                # was a functions key prefix
                msvcrt.getch()
            else:
                return z
      elif os.name == 'posix':
         return os.read( self.fd, 1 )

   def Title( self, Title ):
      pass
      
   def Close( self ):
      pass
      

#############################################################################
#
# Programming over a WBus
#
#############################################################################


class Bus_Target:
   "abstracts a programmable target"

   def __init__(
      self,
      Console,
      Bus = None,
      Type = None,
      DTR = None,
      RTS = None,
      TProg = 0
   ):
      "initialize. Bus and (target) Type can be specified"
      self.Bus = Bus
      self.Type = Type
      self.Region = None
      self.Address = 0
      self.New_Region = 0
      self.Debug = 0
      self.DTR = DTR
      self.RTS = RTS
      self.Console = Console
      self.Connected = 0
      self.TProg = TProg

   def Print( self, String, Progress = 0 ):
      self.Console.Print( String, Progress )

   def Log( self, String ):
      "debug log"
      import time, sys
      if self.Debug:
         self.Print( str( "%04.3f" % time.clock() ) + ' ' + String )

   def Connect( self, Bus = None, Type = None, DTR = None, RTS = None ):
      "connect to the programmer and target."

      # handle arguments"
      if Bus <> None:
         self.Bus = Bus
      if Type <> None:
         self.Type = Type
      if DTR <> None:
         self.DTR = DTR
      if RTS <> None:
         self.RTS = RTS

      # for debugging
      self.Log( "Connect( ... )" )

      # connect
      self.Bus.Connect( DTR = self.DTR, RTS = self.RTS )

      # check whether the device is supported
      if self.Bus.Type == 'WISP':
         pass
      elif self.Bus.Type == 'Wisp628':
         pass
      elif self.Bus.Type == 'Wisp648':
         pass
      elif self.Bus.Type == 'WLdr':
         pass
      else:
         raise IOError, 'device "' + self.Bus.Type + '" is not supported'
         
      self.Connected = 1

   def Close( self ):
      "close WBus connection"
      self.Log( "Close()" )
      self.Bus.Close()
      self.Connected = 0
      
   # set specific programming preferences, requires Wisp648 >= 2.00
   def _Set_Programming_Preferences( self ):
      if (( self.Bus.Type == 'Wisp628' ) or ( self.Bus.Type == 'Wisp648' )) and \
         ( float( self.Bus.Version ) >= 1.25 ) :
         N = 0
         T = ''
         
         # bit 0: selects LVP
         if self.Use_HVP:
            T += 'HVP, '
         else:
            T += 'LVP, '
            N = N + 1
            
         # bit 1: enables power short
         if Vdd_before_Vpp in self.Type.Properties:
            T += 'Vdd-Vpp, '
         else:
            T += 'Vpp-Vdd, '
            N = N + 2
            
         # bit 2: enables power short at exit
         if Cycle_at_Exit in self.Type.Properties:
            T += 'Exit-short, '
            N = N + 4
         else:
            T += 'no-Exit-short, '
            
         # bit 3: enables full pump
         if self.Type.Vpp[ 1 ] < 8.00:
            T += 'Half-pump'
         else:
            T += 'Full-pump'
            N = N + 8
            
         Cmd = "000%XBX" % N
         self.Log( "Specific programming settings: %s [%s]" % ( T, Cmd ))
         # print "settings: %s [%s]" % ( T, Cmd )
         self.Bus.Send_Expect( Cmd )
      
   def __Start_Programming( self, Reading = 0 ):
      "start programming at the start of self.Region"
      import time
      try: 
         Name = Algorithm_Name[ self.Type.Algorithm ]
      except:
         Name = '?'
      self.Log( "__Start_Programming() Region=%s Algorithm=%d,%s" % (
         Region_Name[ self.Region ], 
         self.Type.Algorithm, 
         Name ))
      self.Address = self.Type.Region[ self.Region ].Start
      Cmd = ''
      self.Read_Cluster = 1
      if self.Type.Algorithm == Algorithm_PIC16:
         if self.Region == Region_Code:    Cmd = '000cx'
         if self.Region == Region_Data:    Cmd = '000dx'
         if self.Region == Region_ID:      Cmd = '000fx'
         if self.Region == Region_Device:  Cmd = '000fx'
         if self.Region == Region_Fuses:   Cmd = '000fx'
      if self.Type.Algorithm == Algorithm_PIC16A:
         if self.Region == Region_Code:    Cmd = '001cx'
         if self.Region == Region_Data:    Cmd = '001dx'
         if self.Region == Region_ID:      Cmd = '001fx'
         if self.Region == Region_Device:  Cmd = '001fx'
         if self.Region == Region_Fuses:   Cmd = '001fx'
      if self.Type.Algorithm == Algorithm_PIC16B:
         if self.Region == Region_Code:    Cmd = '002cx'
         if self.Region == Region_Data:    Cmd = '002dx'
         if self.Region == Region_ID:      Cmd = '002fx'
         if self.Region == Region_Device:  Cmd = '002fx'
         if self.Region == Region_Fuses:   Cmd = '001fx' # strange, but seems to be needed...
      if self.Type.Algorithm == Algorithm_PIC16C:
         if self.Region == Region_Code:    Cmd = '004cx'
         if self.Region == Region_Data:    Cmd = '004dx'
         if self.Region == Region_ID:      Cmd = '004fx'
         if self.Region == Region_Device:  Cmd = '004fx'
         if self.Region == Region_Fuses:   Cmd = '004fx'
      if self.Type.Algorithm == Algorithm_PIC16D:
         if self.Region == Region_Code:    Cmd = '007cx'
         if self.Region == Region_Data:    Cmd = '007dx'
         if self.Region == Region_ID:      Cmd = '007fx'
         if self.Region == Region_Device:  Cmd = '007fx'
         if self.Region == Region_Fuses:   Cmd = '007fx'
      if self.Type.Algorithm == Algorithm_PIC16E:
         if self.Region == Region_Code:    Cmd = '008cx'
         if self.Region == Region_Data:    Cmd = '008dx'
         if self.Region == Region_ID:      Cmd = '008fx'
         if self.Region == Region_Device:  Cmd = '008fx'
         if self.Region == Region_Fuses:   Cmd = '008fx'
      if self.Type.Algorithm == Algorithm_PIC16F:
         if self.Region == Region_Code:    Cmd = '00bcx'
         if self.Region == Region_Data:    Cmd = '00bdx'
         if self.Region == Region_ID:      Cmd = '00bfx'
         if self.Region == Region_Device:  Cmd = '00bfx'
         if self.Region == Region_Fuses:   Cmd = '00bfx'
      if self.Type.Algorithm == Algorithm_PIC12:
         if self.Region == Region_Code:    Cmd = '00acx'
         if self.Region == Region_Data:    Cmd = '00adx'
         if self.Region == Region_ID:      Cmd = '00acx'
         if self.Region == Region_Device:  Cmd = '00afx'
         if self.Region == Region_Fuses:   Cmd = '00afx'
      if self.Type.Algorithm == Algorithm_PIC16G:
         if self.Region == Region_Code:    Cmd = '00ccx'
         if self.Region == Region_Data:    Cmd = '00cdx'
         if self.Region == Region_ID:      Cmd = '00cfx'
         if self.Region == Region_Device:  Cmd = '00cfx'
         if self.Region == Region_Fuses:   Cmd = '00cfx'
      if self.Type.Algorithm == Algorithm_PIC16H:
         if self.Region == Region_Code:    Cmd = '00dcx'
         if self.Region == Region_Data:    Cmd = '00ddx'
         if self.Region == Region_ID:      Cmd = '00dfx'
         if self.Region == Region_Device:  Cmd = '00dfx'
         if self.Region == Region_Fuses:   Cmd = '00dfx'
      if self.Type.Algorithm == Algorithm_PIC16I:
         if self.Region == Region_Code:    Cmd = '00ccx'
         if self.Region == Region_Data:    Cmd = '00cdx' # no eeprom in a 16F72x
         if self.Region == Region_ID:      Cmd = '00cfx'
         if self.Region == Region_Device:  Cmd = '00cfx'
         if self.Region == Region_Fuses:   Cmd = '00cfx'
      if self.Type.Algorithm == Algorithm_PIC18:
         if self.Region == Region_Code:    Cmd = '003cx'
         if self.Region == Region_Data:    Cmd = '003dx'
         if self.Region == Region_ID:      Cmd = '003cx'
         if self.Region == Region_Device:  Cmd = '003fx'
         if self.Region == Region_Fuses:   Cmd = '003fx'
      if self.Type.Algorithm == Algorithm_PIC18A:
         if self.Region == Region_Code:    Cmd = '009cx'
         if self.Region == Region_Data:    Cmd = '009dx'
         if self.Region == Region_ID:      Cmd = '009cx'
         if self.Region == Region_Device:  Cmd = '009fx'
         if self.Region == Region_Fuses:   Cmd = '009fx'
      self.Log( "the raw command is [%s]" % Cmd )
      if Cmd == '':
         raise IOError, \
            'internal error: unknown Algorithm or Region: ' + \
            str( self.Type.Algorithm ) + ' ' + str( self.Region )
      #time.sleep( 0.2 ) #why?
      if ( Reading ) and \
      (( self.Bus.Type == 'Wisp628' ) or ( self.Bus.Type == 'Wisp648' )) and \
      ( float( self.Bus.Version ) >= 1.07 ) :
         if ( self.Type.Algorithm == Algorithm_PIC18 ) :
            Cmd = '006' + Cmd[ 3: ]
            self.Read_Cluster = 8
         elif ( self.Type.Algorithm == Algorithm_PIC18A ) :
            if self.Region <> Region_Data:
               Cmd = '006' + Cmd[ 3: ]
               self.Read_Cluster = 8
         elif self.Type.Algorithm == Algorithm_PIC12:
            pass
            # self.Read_Cluster = 4
         elif self.Region == Region_Code:
            Cmd = '005' + Cmd[ 3: ]
            self.Read_Cluster = 4
            # print "using cluster=%d" % self.Read_Cluster
            
      self._Set_Programming_Preferences()
            
      self.Log( "the actual command is [%s]" % Cmd )
      Cmd = ( "%02X" % self.TProg ) + Cmd[ 2: ]
      Reply = self.Bus.Send_And_Receive( Cmd )
      if Reply != Cmd.upper():
         if Reply[ -1: ] == "?":
            raise XWisp_Error( 
               "send='" + Cmd + "' received='" + Reply + "'",
               "This error is likely caused by an attempt to "
               "use older Wisp628 / Wisp648 firmware with a newer "
               "programming algorithm. Update your firmware to the "
               "most recent version (www.voti.nl/wisp648, can also "
               "be used in Wisp628 hardware) and try again. "
            )   
         if Reply == Cmd[ : -1].upper():
           raise XWisp_Error( 
               "send='" + Cmd + "' received='" + Reply + "'",
               "This error is likely caused by a power failure when the "
               "Wisp628-with-dongle / Wisp648 hardware shorts the power. "
               "This can for instance be caused by a hardware problem in "
               "the dongle (use a larger the elco?) or Wisp648, or by an "
               "external 5V power source that does not respond well to a "
               "brief short (maybe try a ~ 5 Ohm series resistor, or use an "
               "7805-based power supply). If you do not need the power short "
               "(depends on your PIC type) you might disable it (Wisp648: "
               "remove the jumper or put it in the inactive position. "
            )   
         raise XWisp_Error( 
            "send='" + Cmd + "' received='" + Reply + "'",
            "error during power-cycle attempt"
         )
      self.Address = self.Type.Region[ self.Region ].Base

   def Set_Region( self, Region ):
      "switch interest to indicated region"
      self.Log( "Set_Region( %d )" % Region )
      self.Region = Region
      self.Address = -1
      self.New_Region = 1

   def __GoTo( self, Address, Reading = 0 ):
      "prepare read or write at self.Region and indicated address"
      self.Log(( "__GoTo( %04X )" % long(Address) ) + \
         ( " self.Address=%04X" % long(self.Address) ) + \
         ( " Region=" +  Region_Name[ self.Region ] ) + \
         ( " Reading=%d" % Reading ))
      if ( self.Address == -1 ) or ( Address < self.Address ):
         self.__Start_Programming( Reading = Reading )
      if ( self.Type.Algorithm == Algorithm_PIC18 ) or ( self.Type.Algorithm == Algorithm_PIC18A ) or \
         ((( self.Bus.Type == 'Wisp628' ) or ( self.Bus.Type == 'Wisp648' )) and \
          ( float( self.Bus.Version ) > 1.02 ) and \
          (( Address - self.Address ) > 4 )):
         if Address <> self.Address:
            self.Bus.Send_Expect( '%06Xm' % Address )
            self.Address = Address
      else:
         while Address > self.Address:
            self.Bus.Send_Expect( 'i' )
            self.Address = self.Address + 1 

   def Put( self, Address, Data ):
      "put (write) the indicated data at the indicated address"
      self.Log( "Put( %04X )" % Address )
      self.__GoTo( Address )
      self.Bus.Send_Expect(( '%04X' % Data ) + 'w' )
      if( self.Type.Algorithm == Algorithm_PIC18 ) | ( self.Type.Algorithm == Algorithm_PIC18A ):
         self.Address = self.Address + 1
         # self.Address = -1

   def Get( self, Address ):
      "get (read) from the indicated address"
      self.Log( "Get( %04X )" % Address )
      self.__GoTo( Address )
      self.Bus.Send_Expect( 'r' )
      if( self.Type.Algorithm == Algorithm_PIC18 ) | ( self.Type.Algorithm == Algorithm_PIC18A ):
         self.Address = self.Address + 1
      return int( self.Bus.Get( 2 * self.Type.Stride ), 16)
      
   def Get_Cluster( self, Base ):
      self.__GoTo( Base, Reading = 1 )
      Data = []
      self.Bus.Send_Expect( 'r' )
      Response = self.Bus.Get( 2 * self.Type.Stride * self.Read_Cluster )
      # print 2 * self.Type.Stride * self.Read_Cluster, Response
      for Address in range( Base, Base + self.Read_Cluster ):
         D = int( Response[ 0 : 2 * self.Type.Stride ], 16)         
         Response = Response[ 2 * self.Type.Stride : ] 
         Data.append( [ Address, D ])
         if ( self.Read_Cluster > 1 ) or \
         ( self.Type.Algorithm == Algorithm_PIC18 ) or ( self.Type.Algorithm == Algorithm_PIC18A ):
            self.Address = self.Address + 1
      return Data

   def Get_ID( self ):
      "get the target's device ID word"
      self.Log( "Get_ID()" )
      if self.Type.Region[ Region_Device ] == None:
         self.Device_Code = 0
         return
      self.Set_Region( Region_Device )
      Result = 0
      # print "hello", self.Type.Region[ Region_Device ].Range( Reverse = 1)
      
      for Address in self.Type.Region[ Region_Device ].Range( Reverse = 1):
         Result = Result * self.Type.Factor + self.Get( Address )
      self.Device_Code = Result
      self.Log( "DEVICE CODE=%04X " %self.Device_Code )
      
      Found = None
      for Name in _PIC_Types_List:
         Chip = _PIC_Types_By_Name[ Name ]         
         if ( self.Type.PIC18 == Chip.PIC18 ): 
           if ( Chip.Device_ID / Chip.ID_Modulo ) == ( self.Device_Code / Chip.ID_Modulo ):
            if not Is_Alias in Chip.Properties:
               if Found != None:
                   raise XWisp_Error, ( 'Internal error: %s and %s match the same ID' % 
                      ( Chip.Name, Found.Name ))
               Found = Chip
            
      if self.Type != None:
         self.Type = Found
         self.Device_Revision = Result % Chip.ID_Modulo
         self.Device_ID = Result - self.Device_Revision
         self.Log( "DEVICE CODE=%04X ID=%04X REV=%04X " %
            ( self.Device_Code, self.Device_ID, self.Device_Revision,  ))

   def Identify_Try( self, Expect ):
      "try to identify the connected PIC"
      self.Log( "Identify_Try( '%s' )" % Expect )

      Try = PIC_Type_From_Name( Expect )
      self.Type = Try
      self.Get_ID()
      if Try.PIC18:
         self.Device_Code_18 = self.Device_Code
      else:
         self.Device_Code_16 = self.Device_Code 
      if self.Type <> None:
         Name = self.Type.Name
      else:
         Name = '<unknown>'
      self.Log( "self.Type from read = " + Name )
                              
   def Identify( self, Expect = None ):
      "identify the connected PIC"
      self.Log( "Identify()" )

      # start in reset, to effectuate switching between programming modes      
      if ( float( self.Bus.Version ) >= 1.25 ):
         # 0008BX added: reset target without power-down
         self.Bus.Send_And_Receive( "0008BX" )
         self.Bus.Send_Expect( "0000AX" )

      if Expect == None:
         self.Identify_Try( '16f84' )
         if self.Type == None: self.Identify_Try( '18f452' )
         if self.Type == None: self.Identify_Try( '12f629' )
      else:
         self.Type = PIC_Type_From_Name( Expect )
         if self.Type.ID_Value == -1:
            self.Type.Unconfirmed = 1
         else:
            self.Identify_Try( Expect )
            if self.Type == None:
               raise XWisp_Error, 'the ID found (%04X) does not match a %s' \
                  % ( self.Device_Code, Expect )
            else:
               self.Type.Unconfirmed = 0            
      if self.Type <> None:
         self.Get_Preserved()

   def Reset( self, Must = 0 ):
      "switch target to 'reset'"
      self.Log( "Reset()" )
      self.Bus.Send_Expect( "000A" )
      if self.Bus.Send_Succeed( "X" ):
         self.Log( "   OK" )         
      else:
         if Must:
            raise XWisp_Error, 'The reset command is not supported by the programmer.'
         else:
            self.Print( "   no reset because the programmer does not support this command" )
         
   def Run( self, Cmd = '0000' ):
      "switch target to 'run', use indicated mode"
      self.Log( "Run( Cmd=%s )" % Cmd )
      self.Bus.Send_Expect( Cmd + 'g' )

   def Progress( self, Address ):
      "called for each address where actual read or write takes place"
      "default: log first address in each reagion, and every multiple of 16"
      import sys
      if self.New_Region or ( Address % 32 == 0 ) or ( self.Debug ):
         self.New_Region = 0
         Line = self.Operation + ' ' + \
            Region_Name[ self.Region ] + ' ' + \
            ( '%04X' % Address )
         self.Print( Line, Progress = 1 )

   def Write( self, Image, Regions = Programming_Regions, Target = None, Warn = 1 ):
      "write the indicated regions of the indicated image to the target"
      self.Log( "Write( ... )" )
      self.Operation = 'write'
      for Region in Regions:
         self.Set_Region( Region )
         if (( self.Type.Algorithm == Algorithm_PIC18 ) |  ( self.Type.Algorithm == Algorithm_PIC18A )) \
         and (( Region == Region_Code ) | ( Region == Region_ID )):
            Message = ''
            N = 0
            # print self.Type.Region[ Region ].Range()
            for Address in self.Type.Region[ Region ].Range():
               Message = Message + ( Image.Get_Hex( Address, 0xFF ))
               if Image.Has( Address ):
                  self.Progress( Address )
                  N = N + 1
               if ( Address + 1 ) % self.Type.Write_Cluster == 0:
                  if N > 0:
                     self.__GoTo( Address - self.Type.Write_Cluster + 1 )
                     self.Bus.Send_Expect( Message + 'w' )
                     self.Address = Address + 1
                  N = 0
                  Message = ''
         else:
            Cluster = self.Type.Write_Cluster
            if self.Region <> Region_Code:
               Cluster = 1            
            if Cluster == 1:
               Block = self.Type.Write_Block
               # print "BLOCK = %d" % Block
               if self.Region <> Region_Code:
                  Block = 1                           
               # print "HELLO", self.Type.Region[ Region ].Range()
               Use = 0
               for Address in self.Type.Region[ Region ].Range():
                  self.Progress( Address )
                  if Image.Has( Address ):
                     Use = Use + 1
                  if ( Use > 0 ) and (( Address + 1 ) % Block == 0 ):
                     Use = 0
                     for A in range( Address + 1 - Block, Address + 1 ):
                        self.Put( A, Image.Get( A, 0x3FFF ))                     
            else:
               Message = ''
               N = 0
               for Address in self.Type.Region[ Region ].Range():
                  Message = Message + ( Image.Get_Hex( Address, 0x3FFF ))
                  if Image.Has( Address ):
                     self.Progress( Address )
                     N = N + 1
                  #print Address, Image.Get_Hex( Address, 0x3FFF ), N, Message
                  if ( Address + 1 ) % Cluster == 0:
                     if N > 0:
                        self.__GoTo( Address - Cluster + 1 )
                        self.Bus.Send_Expect( Message + 'w' )
                        self.Address = Address + 1
                     N = 0
                     Message = ''
      NN = 0
      for Address in self.Type.Region[ Region_Fuses ].Range():
         if Image.Has( Address ):
            NN = NN + 1
      if ( NN == 0 ) and Warn :
         self.Print( 'warning: no fuses information in image' )

   def Read( self, Regions = Programming_Regions, List = None, Ignore = 1 ):
      "read the indicated regions from the target"
      self.Log( "Read( ... )" )
      self.Operation = 'read'
      Image = Hex_Image( Stride = self.Type.Stride )      
      for Region in Regions:
         self.Log( "reading region %s %04X %04X %d (%s)" %
            ( Region_Name[ Region ],
            self.Type.Region[ Region ].Base,
            self.Type.Region[ Region ].Start,
            self.Type.Region[ Region ].End,            
            self.Type.Region[ Region ].Ignore
         ))
         if self.Type.Region[ Region ].End <> -1:
            self.Set_Region( Region )
            self.__GoTo( self.Type.Region[ self.Region ].Base, Reading = 1 )
            N = 0
            for Address in self.Type.Region[ Region ].Range():
               if ( List == None ) or ( List.Has( Address )):
                  N = N + 1
                  self.Progress( Address )
               if (( Address + 1 ) % self.Read_Cluster == 0) or \
               ( Address == self.Type.Region[ Region ].End ):
                  if N > 0:
                     Base = Address - self.Read_Cluster + 1
                     Data = self.Get_Cluster( Base )
                     # print ">>", self.Type.Region[ Region ].Ignore
                     for A, D in Data: 
                        if ( not Ignore ) or \
                        ( not D in self.Type.Region[ Region ].Ignore ):
                           if ( List == None ) or ( List.Has( A )):
                              Image.Set( A, D )
                        self.Log( "Read: %04X = %04X" % ( A, D ) )
                     N = 0
      return Image
      
   def Get_Preserved( self ):
      Image = Hex_Image( Stride = self.Type.Stride )
      self.Type.Preserved.Image = self.Read( 
         List = self.Type.Preserved.Addresses, Ignore = 0 )
      if 0:
         print "blanco"
         print Image.__str__()
      if 0:
         print "raw"
         print self.Type.Preserved.Image.__str__()
      self.Type.Preserved.Patch( Image )
      if 0:
         print "patched"
         print self.Type.Preserved.Image.__str__()
      Image.Fixed = self.Type.Fixed
      if 0:
         print "fixed"
         print self.Type.Preserved.Image.__str__()      
      self.Type.Preserved.Image = Image
      # print "preserved data read:"
      # print self.Type.Preserved.Image.__str__()

   def Verify( self, Image, Regions = Programming_Regions, Target = None ):
      for Region in Regions:
         Readback = self.Read( [ Region ], List = Image, Ignore = 0 )
         Readback.Fixed = Target.Fixed
         Im2 = Image.Clone()
         Im2.Fixed = Target.Fixed         
         Diff = Im2.Compare(
            Readback, 'file', 'target',
            Range = self.Type.Region[ Region ] )
         if Diff != None:
            raise XWisp_Error, 'verification failure: ' + Diff

   def Write_Verify( self, Image, Regions = Programming_Regions, Target = None ):
      "write and verify"
      self.Log( "Write_Verify( ... )" )
      #print "hello", Regions, zz
      for Region in Regions:
         self.Write( Image, [ Region ], Warn = ( Region == Region_Fuses ) )
         Readback = self.Read( [ Region ], List = Image, Ignore = 0 )
         Readback.Fixed = Target.Fixed
         Im2 = Image.Clone()
         Im2.Fixed = Target.Fixed         
         #if 1:
         #   print "readback for region %s :"
         #   print Readback
         Diff = Im2.Compare(
            Readback, 'file', 'target',
            Range = self.Type.Region[ Region ] )
         # print "difference ", Diff
         if Diff != None:
            raise XWisp_Error, 'verification failure: ' + Diff

   def Erase( self ):
      "erase target"
      self.Log( "Erase()" )
      if self.Type.Algorithm == Algorithm_PIC16:
         self.Bus.Send_Expect( '000ex' )
      elif self.Type.Algorithm == Algorithm_PIC16A:
         self.Bus.Send_Expect( '001ex' )
      elif self.Type.Algorithm == Algorithm_PIC16B:
         self.Bus.Send_Expect( '002ex' )
      elif self.Type.Algorithm == Algorithm_PIC16C:
         self.Bus.Send_Expect( '004ex' )
      elif self.Type.Algorithm == Algorithm_PIC16D:
         self.Bus.Send_Expect( '007ex' )
      elif self.Type.Algorithm == Algorithm_PIC16E:
         self.Bus.Send_Expect( '008ex' )
      elif self.Type.Algorithm == Algorithm_PIC16F:
         self.Bus.Send_Expect( '00bex' )
      elif self.Type.Algorithm == Algorithm_PIC16G:
         self.Bus.Send_Expect( '00cex' )
      elif self.Type.Algorithm == Algorithm_PIC16H:
         self.Bus.Send_Expect( '00dex' )
      elif self.Type.Algorithm == Algorithm_PIC16I:
         self.Bus.Send_Expect( '001ex' )
      elif self.Type.Algorithm == Algorithm_PIC12:
         self.Bus.Send_Expect( '00aex' )
      elif self.Type.Algorithm == Algorithm_PIC18:
         self.Bus.Send_Expect( '003ex' )
      elif self.Type.Algorithm == Algorithm_PIC18A:
         self.Bus.Send_Expect( '009ex' )
      else:
         raise IOError, \
            'internal error: unknown Algorithm ' + \
            str( self.Type.Algorithm )
      self.Write( self.Type.Preserved.Image, Warn = 0 )
      
   def Sample2( self, 
      After,
      Before = 0,
      Trigger = None,
      Idle = None
   ):
      import time
      "get samples from the logic sampler"
      Data = []
      self.Log( "Sample( %d, %d )" % ( Before, After ))
      self.Bus.Send_Expect( '000A' )
      self.Bus.Send( 'P' )
      Running = 1
      Triggered = 0
      Receive_Chunk = 50
      while Running:
         if Idle <> None:
            Idle()
         if Trigger.Stop_Requested():
            Running = 0
         self.Bus.Send( 'x' )
         Received_Data = self.Bus.Receive_All( Receive_Chunk )
         for D in Received_Data:
            if Before > 0:
               Before = Before - 1
               Data.append( D )
            else:
               if Trigger.Trigger( ord( D )):
                  Triggered = 1
               if not Triggered:
                  if len( Data ) > 0:
                     Data.pop( 0 )
                     Data.append( D )
               else:
                  if After > 0:
                     After = After - 1
                     Data.append( D )
                  else:
                     Running = 0
      self.Bus.Send( 'q' )
      self.Close()
      return Data
      
   def Sample( 
      self, 
      After,
      Before = 0,
      Trigger = None,
      Idle = None
   ):
      import time
      "get samples from the logic sampler"
      Data = []
      self.Log( "Sample( %d, %d )" % ( Before, After ))
      self.Bus.Send_Expect( '000A' )
      self.Bus.Send( 'P' )
      Running = 1
      Triggered = 0
      Receive_Chunk = 50
      N = 0
      while Running:
         self.Bus.Send( 'x' )
         Received_Data = self.Bus.Receive_All( Receive_Chunk )
         for D in Received_Data:
            N = N + 1
            if Triggered:
               if After > 0:
                  After = After - 1
                  Data.append( D )
               else:
                  Running = 0
            else:
               Before = Before - 1
               if Before < 1:
               #if Trigger.Trigger( ord( D )):
                  Triggered = 1            
      self.Bus.Send( 'q' )
      self.Close()
      print "Trigger after", N
      return Data
      

#############################################################################
#
# FWX (16F819 bootloader)
#
# 2004-01-16
#    changed to new message format
#
#############################################################################

class FWX:

   def __init__( self, Master, Console, Port ):
      import serial
      
      self.Cmd_Address         = 0
      self.Cmd_Block           = 1
      self.Cmd_Checksum        = 2
      self.Cmd_Run             = 3
      self.Cmd_Serial          = 4
      self.Cmd_Sleep           = 5
      self.Cmd_Write_Address   = 6
      self.Cmd_Write_Code      = 7
      self.Cmd_Reset           = 15
      self.Cmd_Report          = 20
      self.Broadcast           = 0xFF
      self.Broadcast_Response  = 0xFE
      
      self.Master   = Master
      self.ComPort  = Port
      self.Console  = Console
      self.Address  = 0xFE
      self.Debug    = 1
      self.Address  = self.Broadcast
      self.Source_Address = 0xFD
      
      self.Port = serial.Serial(
         port      = self.ComPort,
         baudrate  = 19200,
         stopbits  = serial.STOPBITS_ONE,
         timeout   = 2.0 )  
         
      self.Print( 'FWX extension 2.00' )
         
   def Close( self ):
      self.Port.close() 
      
   def Print( self, String, Progress = 0 ):
      # self.Console.Print( String, Progress )
      print String

   def Log( self, String ):
      import time, sys
      if self.Debug:
         self.Print( str( "%04.3f" % time.clock() ) + ' ' + String )      
         
   def Address( self, Address ):
      self.Address = Address
      
   def Send( self, Cmd, Data = 0, Address = None ):
      import time
      if Address == None:
         Address = self.Address
      Sum = Address + Cmd
      D = Data
      for Dummy in range( 0, 4 ):
         #self.Log( "%02X" % Sum )
         Sum = Sum + ( D % 0x100 )
         #self.Log( "%02X -> %02X" % ( D, Sum ))
         D = D / 0x100
      Sum = ( 1 - Sum ) % 0x100    
      Message = ";" + \
         ( "%02X" % self.Source_Address ) + \
         ( "%02X" % Address ) + \
         ( "%02X" % Cmd ) + \
         ( "%08X" % Data ) + \
         ( "%02X" % Sum )
      self.Log( "send " + Message )
      self.Port.write( Message )
      #for c in Message:
      #   self.Port.write( c )
      #   time.sleep( 0.01 )
      
   def Receive( self ):
      import time
      time.sleep( 0.1 )
      Message = ''
      while 1:
         C = self.Port.read( 1 )
         if C == "":
            return Message
         if C > ' ':
            if C == ';':
               Message = ''
            Message = Message + C
            if len( Message ) == 15:
               return Message
      
   def Write_Image( self, Image ):
      import time
      Start = 0x0200
      self.Log( "Write( ... )" )
      self.Port.flushInput()
      self.Port.flushOutput()
      time.sleep( 0.1 )
      self.Send( self.Cmd_Serial, 0x01020304 )
      time.sleep( 0.1 )
      Response = self.Receive()
      self.Log( "received    " + Response )               
      self.Send( self.Cmd_Write_Address, Start )
      time.sleep( 0.1 )
      Response = self.Receive()
      time.sleep( 0.1 )
      self.Log( "received    " + Response )               
      Last_Address = Start
      for Address in range( Start, 0x800 ):
         if Image.Has( Address ):
            Last_Address = Address
      # self.Log( "Last_Address %04X" % Last_Address )               
      Last_Address = ( 4 * ( Last_Address / 4 )) + 3
      # self.Log( "Last_Address %04X" % Last_Address )               
      for Address in range( Start, Last_Address + 1 ):
         print "%04X" % Address 
         # self.Progress( Address )
         if Image.Has( Address ):
            Data = Image.Get( Address )
         else:
            Data = 0x3FFF
         self.Send( self.Cmd_Write_Code, Data )
         # time.sleep( 0.1 )
         Response = self.Receive()
         # time.sleep( 0.1 )
         self.Log( "received    " + Response )         
      
      
   def Response_Data( self, Response ):
      if Response == '':
         return None
      if len( Response ) <> 17:
         raise IOError, "invalid response length (%s)" % Response
      if Response[ 0 ] <> ';':
         raise IOError, "invalid response first char (%s)" % Response
      if Response[ 1:3 ] <> 'FD':
         raise IOError, "invalid response address (%s)" % Response
      if Response[ 3:5 ] <> 'FF':
         raise IOError, "invalid response command (%s)" % Response
      Sum = ( int( Response[1:3], 16 ) + int( Response[3:5], 16 ) + \
            int( Response[5:7], 16 ) + int( Response[7:9], 16 ) + \
            int( Response[9:11], 16 ) + int( Response[11:13], 16 ) + \
            int( Response[13:15], 16 ) + int( Response[14:16], 16 ) ) % 0xFF
      #if Sum <> 1:   
      #   raise IOError, "invalid response checksum %d (%s)" % ( Sum, Response )
      return int( Response[5:13], 16 )
               
   def Send_Receive( self, Cmd, Data = 0, Address = None ):
      import time
      self.Send( Cmd, Data, Address )
      time.sleep( 0.1 )
      Response = self.Receive()
      self.Log( "received    " + Response )
      return self.Response_Data( Response )
      
   def CMD_A( self, Value = None ):
      if Value == None:
         Value = self.Master.Get_Arg()
      self.Address = int( Value )
      
   def CMD_ENUMERATE( self ):
      self.CMD_RESET()
      N = 1
      D = 0
      while D <> None:
         self.Send_Receive( self.Cmd_Block, Address = self.Broadcast )
         self.Send_Receive( self.Cmd_Address, Data = N, Address = self.Broadcast_Response )
         D = self.Send_Receive( self.Cmd_Serial, Address = N )
         if D <> None:
            self.Send_Receive( self.Cmd_Sleep, Address = N )
            self.Log( "%03d : %04X" % ( N, D ))
            N = N + 1
      self.Log( "%d FWX'es found" % ( N - 1 ))
         
   def CMD_RUN( self ):
      self.Send( self.Cmd_Run )
      
   def CMD_GO( self ):
      self.Master.CMD_LOAD()
      self.Master.Image.Stride = 2
      #self.Master.CMD_DUMP()
      self.Write_Image( self.Master.Patched_Image())
      self.CMD_RUN()
      
   def CMD_RESET( self ):
      import time
      self.Send_Receive( self.Cmd_Reset )
      time.sleep( 1.0 )
      
   def CMD_REPORT( self ):
      import time
      self.Send_Receive( self.Cmd_Report )


#############################################################################
#
# command interface
#
#############################################################################

Speed_Auto = 100
Speed_Fast = 101
Speed_Slow = 102

def binary( X, N = 8 , H = '1', L = '0' ):
   result = ''
   while N > 0:
      if X % 2 == 0:
         result = L + result
      else:
         result = H + result      
      N = N - 1
      X = X / 2
   return result
      
class Wisp_Line:
   "Wisp command line interpreter"

   def __init__( self, Line = None, Console = Dos_Console() ):
      import os
      self.Bus_Target = None
      self.Default_Baudrate = 19200
      self.Active_Baudrate = 19200
      #self.Active_Baudrate = 38400
      self.Active_Baudrate = 115200
      self.Target = None
      self.ID = 0
      self.Port = 0
      if os.name == 'nt':
         self.Port = 'COM1'
      if os.name == 'posix':
         self.Port = '/dev/ttyS0' # Linux first serial port
      self.Image = Hex_Image()
      self.Hex = 0
      self.Lazy = 0
      self.Log = 0
      self.Patch_List = {}
      self.Protection = None
      self.Selection = Programming_Regions[:]
      self.Verbose = 0
      self.Verify = 0
      self.Fuses = 1
      self.Fuses_Value = None
      if Line <> None:
         self.Interpret( Line )
      self.DTR = None
      self.RTS = None
      self.Console = Console 
      self.Speed = Speed_Auto
      self.Last_Clock = None
      self.TProg = 0
      self.Purge = 1
      self.TTY_LogTime = 0
      self.Must_Wait_For_Return = 0
      self.Must_Wait_For_Error_Return = 0
      self.Use_HVP = 1
      self.Use_Short = 1
      
   def Wait_For_Return( self, Error = 0 ):
      import sys
      if ( self.Must_Wait_For_Return ) | ( Error & self.Must_Wait_For_Error_Return ):
         self.Print( "press <enter> to continue" );
         sys.stdin.readline()
      
   def CMD_ZPL( self ):
      import time
      P = ZPL( 
         Console = Dos_Console(),
         Port = 'COM6' )
      P.Test()
      
   def CMD_LVP( self ):
      self.Use_HVP = 0
      if self.Bus_Target != None:
         self.Bus_Target.Use_HVP = 0
      
   def CMD_HVP( self ):
      self.Use_HVP = 1
      if self.Bus_Target != None:
         self.Bus_Target.Use_HVP = 1
      
   def CMD_BEEP( self ):
      import time
      self.Console.Beep()
      time.sleep( 0.2 ) 

   def CMD_BURN( self, Nr = None ):
      if Nr == None:
         Nr = self.Get_Arg()
      raise XWisp_Error( "command not implemented" )

   def CMD_CALIBRATE( self ):
      raise XWisp_Error( "command not implemented" )

   def CMD_CHECK( self ):
      self.Connect_If_Needed()
      self.Identify_If_Needed()
      self.Bus_Target.Verify( 
         self.Patched_Image(), 
         Target = self.Target )
      self.Bus_Target.Reset()

   def CMD_CLOSE( self ):
      self.Close_Bus()

   def CMD_CLEAR( self ):
      self.Image.Clear()

   def CMD_COMPARE( self, File = None ):
      if File == None:
         File = self.Get_Arg( Uppercase = 0 )
      Image2 = Hex_Image()       
      Image2.Read( File )
      self.Bus_Target.Reset()
      Result = self.Image.Compare( Image2 )
      if Result == None:
         pass
      else:
         raise XWisp_Error( 'images differ: ' + Result )
         
   def CMD_CONNECT( self ):
      self.Connect_If_Needed()

   def CMD_DTR( self, Value = None ):
      if Value == None:
         Value = self.Get_Arg()
      self.DTR = self.Is_Switch( Value, "DTR" )
      self.Connect_Port_If_Needed()      
      self.Bus_Target.Bus.Set_DTR( self.DTR )

   def CMD_DUMP( self ):
      # self.Print( self.Image.__str__())   
      self.Print( self.Patched_Image().__str__())

   def CMD_ERASE( self ):
      self.Connect_If_Needed()
      self.Identify_If_Needed()
      self.Bus_Target.Erase()
      self.Bus_Target.Reset()

   def CMD_FLUSH( self ):
      pass

   def CMD_FUSES( self, Value = None ):
      if Value == None:
         Value = self.Get_Arg()
      if Value == 'IGNORE':
         self.Fuses = 0
         self.Fuses_Value = None
      elif Value == 'FILE':
         self.Fuses = 1
         self.Fuses_Value = None
      else:
         self.Fuses_Value = self.Hex_Value( Value )

   def CMD_GET( self ):
      self.Connect_If_Needed()
      self.Identify_If_Needed()
      self.Image = self.Bus_Target.Read( 
         Regions = self.Selection, 
         Ignore  = self.Purge )
      self.Bus_Target.Reset()

   def CMD_GO( self ):
      self.CMD_LOAD()
      self.Connect_If_Needed()
      self.Identify_If_Needed()
      self.Bus_Target.Erase()
      self.Bus_Target.Write_Verify( 
         self.Patched_Image(), 
         Target = self.Target,
         Regions = self.Selection )
      self.Bus_Target.Run()

   def CMD_HEX( self ):
      self.Hex = 1

   def CMD_ID( self, Value = None ):
      if Value == None:
         Value = self.Get_Arg()
      self.ID = self.Hex_Value( Value )

   def CMD_LAZY( self ):
      self.LAZY = 1

   def CMD_LOAD( self, File = None ):
      if File == None:
         File = self.Get_Arg( Uppercase = 0 )
      self.Image.Read( File )

   def CMD_LOG( self ):
      self.LOG = 1

   def CMD_NOPURGE( self ):
      self.Purge = 0

   def CMD_PASS( self, Mode = None ):
      import time
      if Mode == None:
         Mode = self.Get_Arg()
      Message = self.Passthrough_Mode( Mode, "PASS" )
      self.Connect_If_Needed()
      self.Bus_Target.Bus.Send_Slowly( Message )
      self.Bus_Target.Bus.Send_Slowly( 'p' )
      time.sleep( 0.100 ) # wait for sending to complete

   def CMD_PATCH( self, Patch = None ):
      if Patch == None:
         Patch = self.Get_Arg()
      if Patch == 'OFF':
         self.Patch_List = {}
      if Patch == 'CLEAR':
         self.Patch_List = {}
      else:
         Split = Patch.split( ':' )
         if len( Split ) <> 2:
            IOError, "PATCH argument format error"
         self.Patch_List[ self.Hex_Value( Split[ 0 ])] = \
            self.Hex_Value( Split[ 1 ])

   def CMD_PAUSE( self, Message = None ):
      if Message == None:
         Message = self.Get_Arg( Uppercase = 0 )
      self.Print( Message )
      # <return>

   def CMD_PORT( self, Name = None ):
      self.Close_Bus()
      if Name == None:
         Name = self.Get_Arg( Uppercase = 0 )
      if (Name + '   ')[ 0 : 3 ].upper() == 'COM':
         if (int((Name + '   ')[ 3 : ]) > 9):
            self.Port = '\\\\.\\' + Name
         else:
            self.Port = Name
      else:
         try:
            N = self.Int_Value( Name )
            if N > 32:
               self.Active_Baudrate = N
            else:
               self.Port = N
         except:
            self.Port = Name

   def CMD_PROTECT( self, String = None ):
      if String == None:
         String = self.Get_Arg()
      if String == 'ON':
         self.Protection = 1
      elif String == 'OFF':
         self.Protection = 0
      elif String == 'FILE':
         self.Protection = None
      else:
         raise XWisp_Error( "invalid PROTECT argument '%s'" % String )

   def CMD_PUT( self ):
      self.Connect_If_Needed()
      self.Identify_If_Needed()
      self.Bus_Target.Write( 
         self.Patched_Image(), 
         self.Selection, 
         Target = self.Target )
      self.Bus_Target.Reset()

   def CMD_READ( self, File = None ):
      if File == None:
         File = self.Get_Arg( Uppercase = 0 )
      self.CMD_GET()
      self.Bus_Target.Reset()
      self.CMD_SAVE( File )
      
   def CMD_RESET( self ):
      self.Connect_If_Needed()      
      self.Bus_Target.Reset( Must = 1 )

   def CMD_RTS( self, Value = None ):
      if Value == None:
         Value = self.Get_Arg()
      self.RTS = self.Is_Switch( Value, "RTS" )
      self.Connect_Port_If_Needed()      
      self.Bus_Target.Bus.Set_RTS( self.RTS )

   def CMD_RUN( self ):
      self.Connect_If_Needed()
      self.Bus_Target.Run()

   def CMD_SAVE( self, File = None ):
      if File == None:
         File = self.Get_Arg( Uppercase = 0 )
      self.Patched_Image().Write( File )

   def CMD_SELECT( self, Selection = None ):
      if Selection == None:
         Selection = self.Get_Arg()
      Add = 1
      #print "hello", Programming_Regions, self.Selection
      for Char in Selection:
         if Char == '+':
            Add = 1
         elif Char == '-':
            Add = 0
         elif Char == 'A':
            self.Select( Add, Programming_Regions )
         elif Char == 'C':
            self.Select( Add, [ Region_Code ])
         elif Char == 'D':
            self.Select( Add, [ Region_Data ])
         elif Char == 'I':
            self.Select( Add, [ Region_ID ])
         elif Char == 'F':
            self.Select( Add, [ Region_Fuses ])
         else:
            raise XWisp_Error( "invalid SELECT argument char '%s'" % Char )
      #print "hello", self.Selection
      
   def CMD_SHORT( self, ARG = None ):
      if ARG == None:
         ARG = self.Get_Arg()
      if ARG == 'OFF':
         self.Use_Short = 0
      elif ARG == 'AUTO':
         self.Use_Short = 1
      elif ARG == 'ON':
         self.Use_Short = 2
      else:
         raise XWisp_Error( "invalid SHORT argument '%s'" % ARG )
      if self.Bus_Target != None:
         self.Bus_Target.Use_Short = self.Use_Short
  
   def CMD_SPEED( self, Selection = None ):
      if Selection == None:
         Selection = self.Get_Arg()
      if Selection == 'FAST':
         self.Speed = Speed_Fast
      elif Selection == 'SLOW':
         self.Speed = Speed_Slow
      elif Selection == 'AUTO':
         self.Speed = Speed_Auto
      else:
         raise XWisp_Error( "invalid SPEED argument '%s'" % Selection )
      self.Update_Speed()
         
   def CMD_TALK( self ):
      self.Connect_If_Needed()
      self.Emulate_TTY()

   def CMD_TARGET( self, Target = None ):
      if Target == None:
         Target = self.Get_Arg()
      if Target == 'AUTO':
         self.Target = None
      else:
         self.Target = PIC_Type_From_Name( Target, None )
         if self.Target == None:
            raise XWisp_Error( "invalid TARGET argument '%s'" % Target )
      if self.Target != None:
         self.Image.Stride = self.Target.Stride

   def CMD_TERM( self, Baudrate = None ):
      if Baudrate == None:
         Baudrate = self.Get_Arg()
      Rate = self.Baudrate_Value( Baudrate, "TERM" )
      self.Connect_Port( Rate )
      self.Emulate_TTY( Text = "TERMinal at raw port, %d baud" % Rate )
      self.Close_Bus()

   def CMD_TEST( self ):
      raise XWisp_Error( "command not implemented" )

   def CMD_TIME( self ):
      import time
      Message = ( time.asctime() )
      Now = time.clock()
      if self.Last_Clock <> None:
         Message = Message + ( " [%3.3f]" % ( Now - self.Last_Clock ))
      self.Last_Clock = Now
      self.Print( Message )

   def CMD_TPROG( self, TProg = None ):
      if TProg == None:
         TProg = self.Get_Arg()
      self.TProg = int( TProg )
      if self.Bus_Target <> None:
         self.Bus_Target.TProg = self.TProg

   def CMD_TTY( self, Mode = None, Baudrate = None ):
      import time
      if Mode == None:
         Mode = self.Get_Arg()
      if Baudrate <> None:
         Message = self.Passthrough_Mode( Mode, "PASS" )
      else:
         try:
            Message = self.Passthrough_Mode( Mode, "PASS" )
         except:
            Message = '0000'
            Baudrate = Mode
      if Baudrate == None:
         Baudrate = self.Get_Arg()
      Rate = self.Baudrate_Value( Baudrate, "TTY" )
      self.Connect_If_Needed()
      self.Bus_Target.Bus.Send_Expect( Message )
      self.Bus_Target.Bus.Send_Slowly( 'p' )
      time.sleep( 0.100 ) # wait for sending to complete
      self.Bus_Target.Bus.Port.setBaudrate( Rate )
      self.Emulate_TTY( Text = "TTY to target, %d baud" % Rate )
            
   def CMD_TTY_TIME( self ):
      self.TTY_LogTime = 1

   def CMD_USE( self, Extension = None ):
      if Extension == None:
         Extension = self.Get_Arg()
      exec( 'from xwisp_' + Extension.lower() + ' import *' )
      exec( 'Extension = ' + Extension.lower() + '()' )
      Extension.Init( self, self.Console, self.Port )
      while 1:
         Command = self.Get_Arg( Empty_Allowed = 1 )
         if Command == '':
            Extension.Close()
            return
         exec( 'Extension.CMD_' + Command.upper() + '()' )                  

   def CMD_VCC( self ):
      raise XWisp_Error( "command not implemented" )

   def CMD_VERBOSE( self ):
      self.Verbose = 1

   def CMD_VERIFY( self ):
      self.CMD_LOAD()
      self.Connect_If_Needed()
      self.Identify_If_Needed()
      self.Bus_Target.Verify( 
         self.Patched_Image(), 
         Regions = self.Selection,
         Target = self.Target )
      self.Bus_Target.Reset()

   def CMD_WAIT( self, Time = None ):
      import time
      if Time == None:
         Time = self.Get_Arg()
      if Time.upper().startswith( 'ERR' ):
         self.Must_Wait_For_Error_Return = 1
      elif Time.upper().startswith( 'END' ):
         self.Must_Wait_For_Return = 1
      else:   
         try:
            n = int( Time )
         except ValueError:
            raise XWisp_Error( "WAIT argument '%s' is not a valid number" % Time )
         time.sleep( 0.001 * n )
      
   def CMD_CLOSE_WINDOW( self ):
      self.Console.Close()

   def CMD_WRITE( self, File = None ):
      if File == None:
         File = self.Get_Arg( Uppercase = 0 )
      self.CMD_LOAD( File )
      self.CMD_PUT()
      self.Bus_Target.Reset()
      
   def CMD_SAMPLE( self, N = None ):
      if N == None:
         N = self.Get_Arg()
      try:
         N = int( N )
      except:
         raise XWisp_Error( "SAMPLE argument must be an integer" )
      self.Connect_If_Needed()
      self.Data = self.Bus_Target.Sample( N )
      for i in range( 0, len( self.Data )):
         print "%3d : %02X  %s" %  ( i, ord( self.Data[ i ] ), binary( ord( self.Data[ i ]), 8, ' *', ' .' ))

   def CMD_INFO( self, Name = None ):
      if Name == None:
         Name = self.Get_Arg()
      if Name == 'ALL':
         print "\nChip name   Vdd range     Vpp range      Status"
         for X in _PIC_Types_List:
            Chip = _PIC_Types_By_Name[ X ]
            Name = Chip.Name.upper()
            print ( "%-10s %5.2f - %5.2f  %5.2f - %5.2f  %s" %
               ( Name, Chip.Vdd[0], Chip.Vdd[1], Chip.Vpp[0], Chip.Vpp[1], Chip.Tested.Short()))
      else:
         Chip = PIC_Type_From_Name( Name, None )
         if Chip == None:
            raise XWisp_Error( "invalid CHIP argument '%s'" % Name )
         self.Print( "" )
         self.Print( "Name        : %s" % Chip.Name.upper() )
         if Chip.ID_Value == -1:
            self.Print( "ID value    : none" )      
         else:
            self.Print( "ID value    : %04X" % Chip.ID_Value )
         self.Print( "Prog specs  : %s" % Chip.Progspec )         
         self.Print( "Code memory : %d instructions" % ( Chip.Region[ Region_Code ].Size / Chip.IPA ))
         self.Print( "Data memory : %d bytes" % Chip.Region[ Region_Data ].Size  )
         self.Print( "Vdd range   : %5.2f - %5.2f" % Chip.Vdd )
         self.Print( "Vpp range   : %5.2f - %5.2f" % Chip.Vpp )
         self.Print( "Test status : %s" % Chip.Tested.Text() )
         self.Print( "" )

   def CMD_CHIPS( self, Export = 0 ):
      if not Export:
         self.Print( "Supported chips (might require the most recent Wisp648 firmware):" )
      else:
         self.Print( "<P>" )
      Before = ""
      After = ""    
      if Export:
         Before = "<!-- BULLET --><TABLE><TR><TD>&nbsp</TD><TD valign=top>" \
                  + '<IMG BORDER="0" + Align + SRC="./pics/redball.gif" ' \
                  + 'WIDTH="11" HEIGHT="11" > </TD><TD>\n'
         After = "\n<!-- /BULLET --></TD></TR></TABLE>"
      N = 0
      Last = '---'
      Line = None
      Prefix = "   "
      for X in _PIC_Types_List:
         P = _PIC_Types_By_Name[ X ]
         Name = X.upper()
         if not P.Tested.Tested:
            Name = Name + "@"
         elif P.Tested.Comment <> "":
            Name = Name + "#"
         N = N + 1
         if Last[ 0 : 3 ] <> X[ 0 : 3 ]:
            if Line <> None:
               self.Print( Before + Line + After )
            if Export:
               self.Print( "&nbsp;<BR>" )
            else:
               self.Print( "" )
            Separator = ""
            Line = Prefix
         if len( Line + Separator + Name ) > 78:
            self.Print( Before + Line + After )
            Separator = ""
            Line = Prefix
         Line += Separator + Name
         Separator = ", "
         Last = X
      self.Print( Before + Line + After )
      self.Print( "" )
      if Export: 
         self.Print( "</P>" )
      else:
         self.Print( "@ : according to specs, but not tested with a real chip" )
         self.Print( "# : check chip info" )
         self.Print( "Use 'xwisp info <chip>' to get info about a specific chip." )
         self.Print( "%d chips total" % N )      
 
   def CMD_EXPORT( self ):
      self.CMD_CHIPS( 1 )
      
   def CMD_HELP( self ):
      Text = (
         'BEEP      : beep at end               ',
#         'BURN n    : set device id             ',
         'CLEAR     : clear image               ',
         'CLOSE     : close serial connection   ',
         'CHECK     : buffer against target     ',
         'CHIPS     : list supported chips      ',
         'CONNECT   : connect to programmer     ',
         'DTR x     : set DTR line              ',
         'DUMP      : dump image                ',
         'ERASE     : erase targets             ',
         'FLUSH     : flush logging             ',
         'FUSES x   : x=IGNORE, FILE or value   ',
         'GET       : target to buffer          ',
         'GO f      : erase, write f, check, run',
         'HELP      : show this text            ',
         'HEX       : hex values (TALK,TERM,TTY)',
         'HVP       : use HVP (default)         ',
         'INFO n|ALL: print info for chip n     ',
#         'ID n      : use device with ID n      ',
         'LAZY      : use lazy programming      ',
         'LOAD f    : file f to buffer          ',
         'LOG f     : log to file f             ',
         'LVP       ; use LVP (default is HVP)  ',
         'PASS m    : enable passthrough        ',
         '            m=B6T, B6I, AUXT, AUXI    ',
         'PATCH OFF : clear patch list          ',
         'PATCH a:v : patch address a, value v  ',
         'PAUSE m   : print m, wait for return  ',
         'PORT P    : use serial port p         ',
         'PORT b    : use active baudrate b     ',
         'PROTECT x : x=ON, OFF or FILE         ',
         'PUT       : buffer to target          ',
         'READ f    : get, save f               ',
         'RESET     : put target in reset       ',
         'RTS x     : set RTS line              ',
         'RUN       : put target in run mode    ',
         'SAVE f    : buffer to file            ',
         'SELECT x  : x[i] from +-CDIFA         ',
         'SHORT x   : x = ON,OFF,AUTO (default) ', 
         'SPEED     : tbw                       ',
         'TALK      : talk to wisp              ',
         'TARGET x  : specify target chip       ',
         'TERM b    : TTY @ line, baudrate b    ',
         'TIME      : show current time         ',
         'TProg X   : specify TProg, in 100 us  ',
         'TTY b     : TTY to target, baudrate b ',
         'TTY [m] b : idem, for m see PASS      ',
         'VCC l h   : set verify voltages       ',
         'VERBOSE   : enable screen logging     ',
         'VERIFY f  : load f, check             ',
         'WAIT n    : wait (at least) N ms      ',
         'WAIT END  : wait for return at end    ',
         'WAIT ERR  : wait for return when an   ',
         '            error occurred            ',
         'WRITE f   : load f, put               ',
         '                                      ')
      for Index in range( 0, len( Text ) / 2 ):
         self.Print(
            Text[ Index ] +
            ' ' +
            Text[ Index + len( Text ) / 2 ] )

   def Error( self, String ):
      raise XWisp_Error( String )

   def Select( self, Add, Selection ):
      #print "sel", Selection
      for Item in Selection:
         #print "sel", Selection
         #print "add", Add, Item
         if Item in self.Selection:
            if not Add:
               self.Selection.remove( Item )
         else:
            if Add:
               self.Selection.append( Item )
         #print "   result", self.Selection

   def Hex_Value( self, String ):
      return int( String, 16 )

   def Int_Value( self, String ):
      return int( String )

   def Close_Bus( self ):
      if self.Bus_Target != None:
         self.Bus_Target.Close()
         self.Bus_Target = None

   def Connect_Port( self, Baudrate = None ):
      if Baudrate == None:
         Baudrate = self.Default_Baudrate
      self.Close_Bus()
      self.WBus = WBus(
         Port = self.Port,
         Console = self.Console,
         ID = self.ID,
         Baudrate = Baudrate,
         DTR = self.DTR,
         RTS = self.RTS )
      self.Bus_Target = Bus_Target(
         Bus = self.WBus,
         Console = self.Console,
         TProg = self.TProg )
      self.Bus_Target.Use_HVP = self.Use_HVP
      self.Bus_Target.Use_Short = self.Use_Short
      if self.Verbose:
         self.Bus_Target.Debug = 1
         self.Bus_Target.Bus.Debug = 1
         
   def Connect_Port_If_Needed( self ):
      if self.Bus_Target == None:
         self.Connect_Port()

   def Connect_If_Needed( self ):
      import time
      if self.Bus_Target == None:
         self.Connect_Port()
      if not self.Bus_Target.Connected:
         self.Bus_Target.Connect()

      if self.Active_Baudrate <> self.Default_Baudrate:
         if (( self.Bus_Target.Bus.Type == 'Wisp628' ) or ( self.Bus_Target.Bus.Type == 'Wisp648' )) and \
            ( float( self.Bus_Target.Bus.Version ) > 1.02 ):
            if self.Active_Baudrate == 9600:
               self.Bus_Target.Bus.Send_Expect( '0004' )
            elif self.Active_Baudrate == 19200:
               self.Bus_Target.Bus.Send_Expect( '0014' )
            elif self.Active_Baudrate == 38400:
               self.Bus_Target.Bus.Send_Expect( '0024' )
            elif self.Active_Baudrate == 57600:
               self.Bus_Target.Bus.Send_Expect( '0034' )
            elif self.Active_Baudrate == 115200:
               self.Bus_Target.Bus.Send_Expect( '0044' )
            else:
               self.Error( "bus rate %d not supported" \
                  % self.Active_Baudrate )
            if ( float( self.Bus_Target.Bus.Version ) < 1.08 ):
               self.Bus_Target.Bus.Send_Char( 'p' )
               time.sleep( 0.4 )
            else:
               self.Bus_Target.Bus.Send_Expect( 'p' )
            self.Bus_Target.Bus.Port.setBaudrate( self.Active_Baudrate )
            self.Bus_Target.Bus.Clear()
            time.sleep( 0.1 )
            self.Bus_Target.Bus.Send_Expect( 'tv' )
         else:
            self.Print( 'bus speed setting not supported' )
            
      self.Update_Speed()
      Speed = ''
      if self.Bus_Target.Bus.Fast:
         Speed = '(fast)'
      Note = ''
      if ( self.Bus_Target.Bus.Type == 'Wisp628' ) and ( self.Bus_Target.Bus.Version >= "1.23" ):
         Note = "(wisp648 firmware)"
      self.Print(
         'hardware: %s %s %s %s' % (
         self.Bus_Target.Bus.Type,
         self.Bus_Target.Bus.Version,
         Speed,
         Note ))

   def Identify_If_Needed( self ):
      if self.Target == None:
         self.Bus_Target.Identify()
         if self.Bus_Target.Type == None:
            self.Error(
               ( 'device word %04X or %04X, can not identify this target: ' +
               'defect, unsupported, or 16x84' ) %
               ( self.Bus_Target.Device_Code_16,
               self.Bus_Target.Device_Code_18 ))
         else:
            self.Print(
               'target: %s, device code %04X revision bits %02X'% (
               self.Bus_Target.Type.Name,
               self.Bus_Target.Device_ID,
               self.Bus_Target.Device_Revision ))
      else:
         self.Bus_Target.Identify( self.Target.Name )
         if self.Bus_Target.Type.Unconfirmed:
            # print "***", self.Bus_Target.Type
            if not self.Bus_Target.Type.ID_Value == -1:
               self.Print(
                  'target can not be verified (ID reads %04X or %04X), %s assumed'
                  % ( self.Bus_Target.Device_Code_16,
                     self.Bus_Target.Device_Code_18,
                     self.Target.Name ))
            self.Bus_Target.Type = self.Target
         else:
            if self.Bus_Target.Type.Name == self.Target.Name:
               self.Print(
                  'target confirmed: %s, revision bits %02X' % (
                  self.Bus_Target.Type.Name,
                  self.Bus_Target.Device_Revision  ))
            else:
               self.Error(
                  'target specified as %s but appears to be a %s'
                  % (  self.Target.Name, self.Bus_Target.Type.Name ))
      self.Image.Stride = self.Bus_Target.Type.Stride
      self.Target = self.Bus_Target.Type

   def Update_Speed( self ):
      if self.Bus_Target <> None:
         if self.Speed == Speed_Fast:
            self.Bus_Target.Bus.Fast = 1
         elif self.Speed == Speed_Slow:
            self.Bus_Target.Bus.Fast = 0
         else:
            self.Bus_Target.Bus.Fast = 0
            if ( self.Bus_Target.Bus.Type == 'Wisp628' ) or (( self.Bus_Target.Bus.Type == 'Wisp648' )):
               if float( self.Bus_Target.Bus.Version ) > 0.9:
                  self.Bus_Target.Bus.Fast = 1

   def Print( self, String ):
      self.Console.Print( String )

   def Log( self, String ):
      self.Print( String )

   def Patched_Image( self ):
      Image = self.Image.Clone()
      if 0:
         print "raw"
         print Image.__str__()
      
      # precious information
      try:
         self.Bus_Target.Type.Preserved.Patch( Image )
      except: pass
      if 0:
         print "precious"
         print Image.__str__()
      
      # removed: fixes should be applied lateron
      # set what is fixed by the target chip
      # if self.Target != None:
      #    Image.Fixed = self.Target.Fixed
      if 0:
         print "fixed"
         print Image.__str__()         
         
      # patch
      for Address in self.Patch_List.keys():
         Image.Set( Address, self.Patch_List[ Address ])
         
      # fuses
      if self.Fuses_Value != None:
         Image.Set( self.Target.Fuses_Address, self.Fuses_Value )
      if not self.Fuses:
         Image.Erase( self.Target.Fuses_Address )
         
      # protection: could be done here, but much too complex
      
      return Image
      
   def Fixed_Image( self ):
      Image = self.Patched_Image()
      if self.Target != None:
         Image.Fixed = self.Target.Fixed
      return Image

   def Is_Switch( self, Value, Command ):
      if Value == '+':
         return 1
      if Value == '-':
         return 0
      IOError, "%s argument error (%s)" % ( Command, Value )

   def Passthrough_Mode( self, Mode, Command ):
      if Mode == 'B6T':
         return '0000'
      elif Mode == 'B6I':
         return '0001'
      elif Mode == 'AUXT':
         return '0002'
      elif Mode == 'AUXI':
         return '0003'
      raise XWisp_Error( "%s mode argument error (%s)" % ( Command, Mode ))

   def Baudrate_Value( self, Baudrate, Command ):
      try:
         return int( Baudrate )
      except:
         List = Baudrate.upper().split( "K" )
         if len( List ) == 2:
            if List[ 0 ] == "":
               List[ 0 ] = "0"
            if List[ 1 ] == "":
               List[ 1 ] = "0"
            try:
               Rate = int( List[ 1 ] )
               while ( Rate <> 0 ) and ( Rate < 100 ):
                  Rate = 10 * Rate
               return 1000 * int( List[ 0 ] ) + Rate
            except:
                pass
      raise XWisp_Error( "%s baudrate argument error (%s)" % ( Command, Baudrate ))

   def Receive_Char( self ):
      if self.Bus_Target.Bus.Port.inWaiting() == 0:
         return ''
      return self.Bus_Target.Bus.Port.read( 1 )

   def Emulate_TTY( self, Text = 'TTY mode' ):
      import sys, time
      Escapes = 0
      self.Console.Set_Raw()
      self.Console.Print( '%s (ESC ESC to exit)' % Text )
      try:
         f = open( "tty.log", "w" )
      except:
         f = None
      while Escapes < 2:
         Char = self.Console.Get_Key()
         if Char <> '':
            self.Bus_Target.Bus.Port.write( Char )
            if f != None:
               f.write( Char )
            if Char == chr( 27 ):
               Escapes = Escapes + 1
            else:
               Escapes = 0
         else:
            Received = self.Receive_Char()
            if Received <> '':
               if f != None:
                  f.write( Received )
               if self.Hex:
                  self.Console.Print_String( "[%02X]" % ord( Received ))
               self.Console.Print_String( Received )
               if self.Hex and (Received == chr( 13 )):
                  self.Console.Print_String( "\n" )
               if Received == chr(10):
                  if self.TTY_LogTime:
                     self.Console.Print_String( str( "[%04.3f] " % time.clock()))
            else:
               time.sleep( 0.010 )
      self.Console.Print( '' )
      self.Console.Print( 'TTY mode end' )
      self.Console.Print( '' )
      self.Console.Set_Cooked()
      if f != None: 
         f.close()

   def Get_Arg( self, Uppercase = 1, Empty_Allowed = 0 ):
      Result = ''
      while Result == '':
         if len( self.Args ) == 0:
            if Empty_Allowed:
               return ''
            else:
               raise XWisp_Error( "missing argument(s) for last command" )
         Result = self.Args.pop( 0 ).strip()
      if Uppercase:
         Result = Result.upper()
      return Result

   def Execute( self, Command ):
      if Command.startswith( 'COM' ) and Command <> 'COMPARE':
         exec( 'self.CMD_PORT("' + Command + '")' )
      else:
         try:
            dummy = self.__class__.__dict__[ 'CMD_' + Command.upper() ]
         except:
            # print self.__class__.__bases__
            try:
               dummy = self.__class__.__bases__[ 0 ].__dict__[ 'CMD_' + Command.upper() ]
            except:
               raise XWisp_Error( 
                  "unknown command '%s'" % Command ,
                  "The command\n"
                  "   xwisp help\n"
                  "will show the list of available commands."
               )
         exec( 'self.CMD_' + Command.upper() + '()' )

   def Interpret( self, Line = None, Line_Mode = 1, Show_Version = 1 ):
      import sys, traceback, StringIO
      if Line == None:
         Line = sys.argv[1:]
      Line = Line[:]
      if Show_Version:
         if Line_Mode:
            self.Print( 'XWisp ' + Version +', command line mode' )
         else:
            self.Print( 'XWisp ' + Version  )      
      NL = ''
      if Line_Mode:
         NL = '\n'
      if len( Line ) == 0:
         self.CMD_HELP()
      else:
         self.Args = Line
         while len( self.Args ) > 0:
            Command = self.Get_Arg()
            try:
               self.Execute( Command )
            except XWisp_Error, ( e ):
               self.Print( str( e ))
               self.Print( 'ERROR' )
               self.Wait_For_Return( Error = 1 )
               return
            except Hex_Image.Hex_Image_Error, e:
               self.Print( NL + "The specified hex file is not valid:\n   %s" % str( e ))
               self.Print( 'ERROR' )
               self.Wait_For_Return( Error = 1 )
               return            
            except:
               self.Print( 
                 NL + "An exception ocurred which was not explicitly handled by the XWisp application. "
                 "The traceback below might give some information about the exception.\n"
               )
               s = StringIO.StringIO()
               traceback.print_exc( file = s )
               self.Print( s.getvalue())
               s.close()
               self.Print( 'ERROR' )
               self.Wait_For_Return( Error = 1 )
               return
         self.Print( '%-32s' % 'OK' )
         self.Wait_For_Return( Error = 0 )


#############################################################################
#
# GUI 1
#
# 'sea of buttons' style 
#
#############################################################################

class Command:
   def __init__( self, func, *args, **kw ):
      self.func = func
      self.args = args
      self.kw = kw
   def __call__( self, *args, **kw ):
      args = self.args + args
      kw.update( self.kw )
      apply( self.func, args, kw )

class Text_Window:

   def __init__( self, Parent ):
      import Tkinter
      self.Parent = Parent
      self.Root = Tkinter.Toplevel( Parent )
      self.Root.bind( '<Destroy>', Command( self.Destroy ))
      self.Text = Tkinter.Text( self.Root, height=26, width=80, font='Courier 8' )
      self.Scroll = Tkinter.Scrollbar( self.Root, command=self.Text.yview )
      self.Text.configure( yscrollcommand=self.Scroll.set )
      self.Text.pack( side=Tkinter.LEFT )
      self.Scroll.pack( side=Tkinter.RIGHT, fill=Tkinter.Y )
      self.Last_Line = None
      self.Text.focus_force()
      self.Text.bind( '<KeyPress>', Command( self.Key_Press ))
      self.Key = ''
      self.Destroyed = 0
      self.Closed = 0
      self.Set_Cooked()

   def Beep( self ):
      if self.Closed:
         return
      try:
         import winsound
         winsound.Beep( 440, 400 )
      except:
         self.Print( "sorry, could not beep" )

   def Destroy( self, Event ):
      #print "destroy"
      self.Destroyed = 1
      
   def Close( self ):
      if self.Closed:
         return
      self.Root.destroy()
      self.Closed = 1

   def Key_Press( self, Event ):
      #print "[%s]" % Event.keysym
      if Event.keysym == 'BackSpace':
         self.Key = chr( 8 )
      elif Event.keysym == 'Tab':
         self.Key = chr( 9 )
      elif Event.keysym == 'LineFeed':
         self.Key = chr( 10 )
      elif Event.keysym == 'Return':
         self.Key = chr( 13 )
      elif Event.keysym == 'Escape':
         self.Key = chr( 27 )
      elif Event.keysym == 'Delete':
         self.Key = chr( 127 )
      elif Event.keysym == 'Cancel':
         self.Key = chr( 27 )
      elif Event.keysym == 'space':
         self.Key = ' '
      elif len( Event.keysym ) == 1:
         self.Key = Event.keysym
      else:
         return None
      return "break"

   def Print( self, String, Progress = 0 ):
      import Tkinter
      if self.Closed:
         return
      if self.Last_Line <> None:
         self.Text.delete( self.Last_Line, Tkinter.END)
         self.Last_Line = None
      if Progress:
         self.Last_Line = self.Text.index( Tkinter.END )
      self.Text.insert( Tkinter.END, '\n' + String, 'last' )
      self.Text.see( Tkinter.END )
      self.Text.update()
      self.Parent.update()

   def Print_String( self, String ):
      import Tkinter
      if self.Closed:
         return
      self.Text.insert( Tkinter.END, String )
      self.Text.see( Tkinter.END )
      self.Text.update()
      self.Parent.update()

   def Set_Raw( self ):
      if self.Closed:
         return
      self.Text.configure( insertontime = 600 )

   def Set_Cooked( self ):
      if self.Closed:
         return
      self.Text.configure( insertontime = 0 )

   def Get_Key( self ):
      if self.Destroyed:
         print "Esc"
         return chr( 27 )
      self.Parent.update()
      Key = self.Key
      self.Key = ''
      return Key

   def Title( self, Text ):
      if self.Closed:
         return
      self.Root.title( Text)

class Wisp_Window_Interpreter( Wisp_Line ):

   def __init__( self, Parent, Console ):
      self.Parent = Parent
      Wisp_Line.__init__( self, Console = Console )

   def Run( self, Command ):
      Wisp_Line.Interpret( self, Command, Line_Mode = 0 )


class Wisp_Button:

   def __init__( self, Parent, Console, At, Text, Command ):
      import Tkinter
      self.Parent = Parent
      self.Console = Console
      self.Command = Command
      self.Text = Text
      self.Button = Tkinter.Button(
         Parent.Root,
         text = Text,
         command = self.Pressed )
      if At == '':
         self.Button.grid()
      else:
         self.Button.grid( row = At[ 0 ], column = At[ 1 ], \
            padx = 3, pady = 3,
            sticky = 'EW' )

   def Pressed( self ):
      import Tkinter
      Out = self.Console
      if self.Console == None:
         Out = Text_Window( self.Parent.Root )
         Out.Title( self.Text + '  (' + \
            reduce( lambda x,y: x + ' ' + y, self.Command ) + ')' )
      Interpreter = Wisp_Window_Interpreter( self.Parent.Root, Out )
      Interpreter.Run( self.Command )
      if self.Console == None:
         Out.Title( '(inactive)' )

class Wisp_Window:
   "Wisp GUI"

   def __init__( self ):
      self.Root = None
      self.Row = 0
      self.Column = -1
      self.Macros = { 'xwisp_defaults' : []}

   def Make_Root( self ):
      import Tkinter
      if self.Root == None:
         self.Root = Tkinter.Tk()
         self.Root.title( 'XWisp' )

   def Mainloop( self ):
      if self.Root <> None:
         self.Root.mainloop()

   def Run_File( self, File_Name ):
      File = open( File_Name, 'r' )
      for Line in File.readlines():
         if Line.endswith( '\n' ):
            Line = Line[:-1]
         # print 'interpret', Line
         self.Interpret( Line )
      File.close()

   def Run_File_If_Exists( self, File_Name ):
      try:
         File = open( File_Name, 'r' )
         File.close()
         self.Run_File( File_Name )
      except:
         return

   def Get_Arg( self, Uppercase = 1 ):
      Result = ''
      while Result == '':
         if len( self.Args ) == 0:
            return ''
         Result = self.Args.pop( 0 ).strip()
      if Uppercase:
         Result = Result.upper()
      return Result

   def Expand( self, List, N = 0 ):
      if N > 100:
         IOError, "macro expansion nesting exceeds 100"
      Result = []
      for Element in List:
         if self.Macros.has_key( Element):
            Result.extend( self.Expand( \
               self.Macros[ Element ], N + 1 ))
         else:
            if Element <> '':
               Result.append( Element )
      return Result

   def Interpret( self, Line = '' ):
      self.Args = Split_Quoted( Line )
      # print self.Args
      if len( self.Args ) > 0:
         if self.Args[ 0 ].upper() != 'MACRO':
            self.Args = self.Expand( self.Args )
      # print 'line', Line
      # print 'args', self.Args
      Command = self.Get_Arg()
      if ( Command + '#' )[ 0 ]<> '#':
         #try:
            exec( 'self.CMD_' + Command.upper() + '()' )
         #except AttributeError:
         #   raise IOError, "unknown command '%s' in line '%s'" % ( Command, Line )

   def Make_At( self, String ):
      Row = None
      Column = None
      if String <> None:
         for Char in String:
            if Char.isalpha():
               Row = ord( Char ) - ord( 'A' )
            if Char.isdigit():
               if Column == None:
                  Column = 0
               Column = 10 * Column + int( Char )
      if Row == None:
         Row = self.Row
      if Column == None:
         Column = self.Column + 1
      self.Row = Row
      self.Column = Column
      return ( Row, Column )

   def CMD_BUTTON( self ):
      Arg = self.Get_Arg()

      if Arg == 'AT':
         At = self.Get_Arg()
         Arg = self.Get_Arg()
      else:
         At = None
      At = self.Make_At( At )

      if Arg == 'TEXT':
         Text = self.Get_Arg( Uppercase = 0 ).replace( '_', ' ' )
         Arg = self.Get_Arg()
      else:
         Text = '<button>'

      if Arg == 'XWISP':
         Arg = ''
         Xwisp_Command = self.Expand( self.Macros[ 'xwisp_defaults' ][:])
         Xwisp_Command.extend( self.Expand( self.Args ))
         self.Args = []
         # print 'macros', self.Macros
         # print 'xwisp_command is', Xwisp_Command
      else:
         XWisp_Command = []

      if Arg <> '':
         raise XWisp_Error( "unknown command '%s'" % Arg )

      self.Make_Root()
      Button = Wisp_Button( self, None, At, Text, Xwisp_Command )

   def CMD_LABEL( self ):
      import Tkinter
      Arg = self.Get_Arg()

      if Arg == 'AT':
         At = self.Get_Arg()
         Arg = self.Get_Arg()
      else:
         At = None
      At = self.Make_At( At )

      if Arg == 'TEXT':
         Text = self.Get_Arg( Uppercase = 0 ).replace( '_', ' ' )
         Arg = self.Get_Arg()
      else:
         Text = '<label>'

      self.Make_Root()
      Label = Tkinter.Label(
         self.Root,
         text = Text )
      if At == '':
         Label.grid()
      else:
         Label.grid( row = At[ 0 ], column = At[ 1 ], sticky = 'E' )

   def CMD_MACRO( self ):
      Name = self.Get_Arg( Uppercase = 0 )
      self.Macros[ Name ] = self.Args[:]     
      self.Args = []
      # print 'Name=', Name
      # print 'Macros=', self.Macros

   def CMD_NEXTROW( self ):
      self.Row = self.Row + 1
      self.Column = -1

   def CMD_NAME( self ):
      Name = self.Get_Arg( Uppercase = 0 )
      self.Make_Root()
      self.Root.title( Name.replace( '_', ' ' ))


#############################################################################
#
# Logic Analyser GUI
#
#############################################################################

# vertical marker lines
# 'show all' button
# set samples N
# set 'samples before trigger'
# select trigger
# show trigger moment in display
# interpreter: asynch, I2C
# multi-channel
# high-speed
# origin and span not preserved?
# time axis
# triggering
# sample == capture!
# view window RAISED problem
# enter numerical start, span
# show irregularitief (strange frequency) in red
# hide error line
# start with more span than 10!
# error in triggering

from Tkinter import *
import Tkinter
import tkFileDialog
##import app_util
import os
import pickle

# used?
def frame( root, side ):
   w = Frame( root )
   w.pack( side = side, expand = YES, fill = BOTH )
   return w
   
# used?   
def button( root, side, etxt, command = None ):
   w = Button( root, text = text, command = command )
   w.pack( side = side, expand = YES, fill = BOTH )
   return w
   
class Empty_Class:
   pass   
   
def Bin_From_Hex( X ):    
   S = ''
   if len( X ) == 1:
      if X.upper() >= 'A':
         N = ord( X.upper() ) - ord( 'A' )
      else:
         N = ord( X ) - ord( '0' )
      for i in range( 4 ):
         S = (( N % 2 ) and '1' or '0' ) + S
         N = N / 2
   else:
      for C in X:
         S = S + Bin_From_Hex( C )
   return S
   
def Hex_From_Bin( X ):
   if len( X ) <= 4:
      N = 0
      for C in X:
         N = 2 * N
         if C == '1':
            N = N + 1
      if N < 10:
         return chr( N + ord( '0' ))
      else:
         return chr( ( N - 10 ) + ord( 'A' ) )
   else:
      return Hex_From_Bin( X[ : -4] ) + Hex_From_Bin( X[ -4 : ] )
      
def Hex_From_List( X ):
   S = ""
   for C in X:
      S = chr( C + ord( '0' )) + S
   return Hex_From_Bin( S ) 
   
class Empty_Trigger:

   def __init__( self ):
      self.Stop_Flag = 0

   def Trigger( self, D ):
      return 1
      
   def Stop_Requested( self ):
      return self.Stop_Flag
      
   def Request_Stop( self ):
      self.Stop_Flag = 1
         
class Line_Trigger( Empty_Trigger ):

   def __init__( self, Immediate, Line, Event ):
      Empty_Trigger.__init__( self )
      
      self.Immediate = Immediate
      self.Mask = 1 << Line
      self.Invert = 0
      self.First = 0
      self.Must_Change = 0
      
      if not Immediate:
         if Event == 0:
            self.Immediate = 1
            self.Must_Change = 1
         elif Event == 1:
            self.Must_Change = 1
         elif Event == 2:
            self.Must_Change = 1
            self.Invert = 0xFF
         elif Event == 3:
            pass
         elif Event == 4:
            self.Invert = 0xFF
         
      self.First = self.Must_Change
      
      print "trigger Imm=%d Line=%d Ev=%d : imm=%d mask=%02X inv=%02X mch=%d" % \
         ( Immediate, Line, Event, self.Immediate, self.Mask, self.Invert, self.Must_Change )
      
   def Trigger( self, D ):
      
      # keep only the interesting bit, make it positive
      D = ( D ^ self.Invert ) & self.Mask
      
      # save the first sample
      if self.First:
         self.Last = D
         self.First = 0
         return 0
         
      # if change require: return when no change
      if self.Must_Change:
         if self.Last == D:
            return 0
            
      if self.Immediate:
         return 1
         
      self.Last = D
      if D:
         return 1
      else:
         return 0
         
         

icon='''R0lGODdhFQAVAPMAAAQ2PESapISCBASCBMTCxPxmNCQiJJya/ISChGRmzPz+/PxmzDQyZDQy
ZDQyZDQyZCwAAAAAFQAVAAAElJDISau9Vh2WMD0gqHHelJwnsXVloqDd2hrMm8pYYiSHYfMMRm53ULlQ
HGFFx1MZCciUiVOsPmEkKNVp3UBhJ4Ohy1UxerSgJGZMMBbcBACQlVhRiHvaUsXHgywTdycLdxyB
gm1vcTyIZW4MeU6NgQEBXEGRcQcIlwQIAwEHoioCAgWmCZ0Iq5+hA6wIpqislgGhthEAOw==
'''   

icon1 = ('''#define im_width 26
#define im_height 25
static char im_bits[] = {
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00, 0x70,0x00,0x00,0x00,0x7e,
0x00,0x00,0xe0,0x7f,0x00,0x00,0xff,0x63,0x00,0x00, 0x3f,0x70,0x00,0x00,0x03,
0x7e,0x00,0x00,0xe3,0x7f,0x00,0x00,0xff,0x63,0x00, 0x00,0x3f,0x60,0x00,0x00,
0x03,0x60,0x00,0x00,0x03,0x60,0x00,0x00,0x03,0x78, 0x00,0x00,0x03,0x7c,0x00,
0x00,0x03,0x7e,0x00,0xc0,0x03,0x7e,0x00,0xe0,0x03, 0x3c,0x00,0xf0,0x03,0x18,
0x00,0xf0,0x03,0x00,0x00,0xe0,0x01,0x00,0x00,0xc0, 0x00,0x00,0x00,0x00,0x00,
0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00 };''')

class Empty():
   pass

class Track:
   def __init__( self, Name ):
      self.Name = Name
      self.X_Margin   = 2
      self.Y_Margin   = 2
      self.X_Name     = 40
      self.Fill_Color = 'YELLOW'
      pass
   
class Digital_Track( Track ):

   def __init__( self, Data, Name, Color ):
      Track.__init__( self, Name )
      self.Data = Data
      self.Color = Color
      
   def Draw( self, Canvas, X, Y, L, H, S, N ):
      Canvas.create_rectangle( 
         X, Y, X + L, Y - H, 
         fill = self.Fill_Color, outline = '' )
      Y = Y - self.Y_Margin
      H = H - 2 * self.Y_Margin
      X = X + self.X_Margin
      Canvas.create_text( X, Y - ( H / 2 ), text = self.Name, anchor = W )
      X = X + self.X_Name
      L = L - ( 2 * self.X_Margin + self.X_Name )
      Last = None
      Count = 0
      Old_X = X
      for Offset in range( N ):
        if S + Offset < len( self.Data ):
         D = self.Data[ S + Offset ]
         if Last <> None and Last <> D:
            Canvas.create_line( Old_X, Y, Old_X, Y - H )
         Last = D
         AY = Y
         if D: 
            AY = AY - H
         New_X = X + (( L * ( Offset + 1 )) / N )
         Canvas.create_line( Old_X, AY, New_X, AY )
         Old_X = New_X
         
def Scale_Up( N ):  
   # return N, N  # for debugging only
   M = 1
   while 1:
      for Minor, Major in ( ( 1, 1 ),  ( 1, 5 ), ( 2, 10 ), ( 5, 25 ) ):
         if N <= M * Major:
            return ( M * Minor, M * Major  )
      M = M * 10         
         
class Counter_Track( Track ):

   def __init__( self, Name ):
      Track.__init__( self, Name )         
      self.Y1 = 0     # Y pixels top of track to top of marker
      self.Y2 = 4     # Y big marker pixels above and below line
      self.Y3 = 2     # Y small marker pixels above and below line
      self.X1 = 50    # X pixels between markers
      self.Marker_Font = 'Verdana 6 bold'
            
   def Steps( self, L, S, N, Sel ):
      X = ( self.X1 * N ) / L
      N_per_Marker = Scale_Up( X )[ Sel ]
      First = 0
      while First < S: 
         First = First + N_per_Marker
      return range( First - S, N, N_per_Marker )
      
   def Format_Marker( self, X ):
      return str( X )
      
   def Draw( self, Canvas, X, Y, L, H, S, N ):
      Canvas.create_rectangle( 
         X, Y, X + L, Y - H, 
         fill = self.Fill_Color, outline = '' )
      Y = Y - self.Y_Margin
      H = H - 2 * self.Y_Margin
      X = X + self.X_Margin
      L = L - ( 2 * self.X_Margin + self.X_Name )
      MY = Y - ( H / 2 )
      Canvas.create_text( X, MY, text = self.Name, anchor = W )
      X = X + self.X_Name
      LY = ( Y - H ) + ( self.Y1 + self.Y2 )
      for Offset in self.Steps( L, S, N, 0 ):
         Index = S + Offset
         MX = X + (( L * Offset ) / N )
         Canvas.create_line( MX, LY + self.Y3, MX, LY - self.Y3 )
      Canvas.create_line( X, LY, X + L, LY  )
      for Offset in self.Steps( L, S, N, 1 ):
         Index = S + Offset
         MX = X + (( L * Offset ) / N )
         Canvas.create_line( MX, LY + self.Y2, MX, LY - self.Y2 )
         Canvas.create_text( 
            MX, LY + self.Y2, text = self.Format_Marker( Index ), 
            anchor = Tkinter.N, font = self.Marker_Font )
         
class Time_Track( Counter_Track ):

   # 115k2 => 11.52 ks/s => 86.8 us / sample 
   def __init__( self, 
      Name, 
      Tick_Duration = 0.08680556, 
      Duration_Units = ( 'us', 'ms', 's' ) 
   ):
      Counter_Track.__init__( self, Name )
      self.Tick_Duration = Tick_Duration
      self.Duration_Units = Duration_Units                 
      
class Marker_Track( Track ):

   def __init__( self, Position, Color ):
      Track.__init__( self, None )
      self.Position = Position
      self.Color = Color
      
   def Draw( self, Canvas, X, Y, L, H, S, N ):
      X = X + self.X_Margin + self.X_Name
      L = L - ( self.X_Margin + self.X_Name )
      H = H + self.X_Margin
      if 0 : # debug only
         Canvas.create_rectangle( 
            X, Y, X + L, Y + H, 
            outline = self.Color )
      if self.Position >= S and self.Position <= S + N :
         X = X + ( ( self.Position - S ) * L ) / N
         Canvas.create_line( 
            X, Y, X, Y + H, fill = self.Color )
     

def Checkbutton_Set( Checkbutton, State ):
   if State:
      Checkbutton.select()
   else:
      Checkbutton.deselect()      
      
def SetIcon( window ):
   try:
      window.iconbitmap( 'd:/wouter/xwisp/wesp1.ico' )
   except:
      pass            
      
class Analyser():

   def __init__( self, Parent ):
      self.Parent = Parent
      self.Window = Toplevel( self.Parent )
      self.Window.title( 'XWisp - logic analyser' )
      self.Window.iconname( 'Analyser' )
      SetIcon( self.Window )
      
      self.Preserved = Empty()
      self.Preserved.Data = None
      self.Preserved.N_Samples = 0
      self.Preserved.Origin = 0
      self.Preserved.Span = 100
      self.Preserved.Scale_Value_BG = 'YELLOW'
      self.Preserved.Tick_Pixels = 30
      self.Preserved.Data = []
      self.Preserved.Trigger_N = None

      self.Preserved.Canvas_BG = 'BROWN'
      self.Preserved.Canvas_Border = 10
      self.Preserved.Canvas_Border_Effect = RAISED
      self.Preserved.Canvas_Width = 1000
      self.Preserved.Canvas_X_Border_Margin =  5
      self.Preserved.Canvas_Y_Border_Margin =  5
      self.Preserved.Canvas_Track_Height    = 20
      self.Preserved.Canvas_Y_Track_Margin  =  5
      
      self.Preserved.Trigger_Immediately = 1
      self.Preserved.Trigger_Line = 0
      self.Preserved.Trigger_Event = 0
      self.Preserved.Trigger_Before = 100
      self.Preserved.Trigger_After = 300

      self.FileName = None
      self.Tracks = []
      self.GUI_Items = []       
      self.Track_Info = (
         ( 'CLCK',  'GREEN', 'PGC (programming clock) line, GREEN wire' ), 
         ( 'DATA',  'BLUE',  'PGD (programming data) line, BLUE wire'  ),
         ( 'PLD',   'WHITE', 'PGM (LPV enable) line, WHITE wire' ), 
         ( 'AUX1',   None,   'AUX1 line' ),
         ( 'AUX2',   None,   'AUX2 line' ),
         ( 'ERR',    None,   'sample errors' ),
         ( 'Sample', None,   'sample number track' ),
         ( 'Time',   None,   'time track' ))
      self.N_Data_Lines = 6
      self.Preserved.Visible_Tracks = [ 1, 1, 1, 1, 1, 1, 1, 1 ]
      
      mBar = Frame( self.Window, relief = RAISED, borderwidth = 2 )
      mBar.pack( fill = X )
            
      File = Menubutton( mBar, text = 'File', underline = 0 )
      File.pack( side = LEFT, padx = "2m" )
      File.menu = Menu( File )
      File.menu.add_command( label = "Load", underline = 0, 
         command = self.LOAD  )
      File.menu.add_command( label = "Save", underline = 0, 
         command = self.SAVE  )
      File.menu.add_command( label = "Save As", underline = 5, 
         command = self.SAVE_AS  )
      File.menu.add_separator()
      File.menu.add_command( label = "Close", underline = 0, 
         command = self.CLOSE )
      File[ 'menu' ] = File.menu
      
      View = Menubutton( mBar, text = 'View', underline = 0 )
      View.pack( side = LEFT, padx = "2m" )
      View.menu = Menu( View )
      self.Track_Visible = []
      for Index in range( 0, len( self.Track_Info )):
         Name, Color, Text = self.Track_Info[ Index ]
         V = IntVar()         
         View.menu.add_checkbutton( label = Name + ' - ' + Text, 
            command = self.Tracks_Change, variable = V  )
         self.Track_Visible.append( V )
         V.set( self.Preserved.Visible_Tracks[ Index ] )
      View.menu.add_separator()
      View[ 'menu' ] = View.menu
      
      Sampler = Menubutton( mBar, text = 'Sampler', underline = 0 )
      Sampler.pack( side = LEFT, padx = "2m" )
      Sampler.menu = Menu( Sampler )
      Sampler.menu.add_command( label = "Configure", underline = 0, 
         command = self.SAMPLER_CONFIGURE )
      Sampler[ 'menu' ] = Sampler.menu

      self.Process_Data()
      self.Redraw()
      
   def LOAD( self ):
      Answer = tkFileDialog.askopenfilename( 
         defaultextension = '.xwa', 
         filetypes = ( 
            ('XWisp logic Analyser files', '*.xwa'), 
            ('all files', '*' ) 
         ),
         initialfile = self.FileName )
      if Answer != '':
         self.FileName = Answer
         # print "load %s" % self.FileName
         try:
            f = open( self.FileName, 'r' )
            try:
               self.Preserved = pickle.load( f )
               f.close()
            except:
               f.close()
               raise
         except:
            N = 0
            # pass
         self.Process_Data()
         self.Redraw()
      
   def SAVE( self ):
      if self.FileName == None:
         self.FileName = tkFileDialog.asksaveasfilename( 
            defaultextension = '.xwa', 
            filetypes = ( 
               ('XWisp logic Analyser files', '*.xwa'), 
               ('all files', '*' ) 
            ),
            initialfile = self.FileName )
      if self.FileName != None:
         self.Get_Settings_From_GUI()
         try:
            f = open( self.FileName, 'w' )
            try:
               pickle.dump( self.Preserved, f )
               f.close()
            except:
               f.close()
               raise
         except:
            pass
         
   def SAVE_AS( self ):
      Answer = tkFileDialog.asksaveasfilename( 
         defaultextension = '.xwa', 
         filetypes = ( 
            ('XWisp logic Analyser files', '*.xwa'), 
            ('all files', '*' ) 
         ),
         initialfile = self.FileName )
      if Answer != '':
         self.FileName = Answer
         self.SAVE()
      
   def CLOSE( self ):
      self.Window.destroy()
      
   def Sampler_Cancel( self ):
      self.Trigger.Request_Stop()
      print "trigger stop requested"
      
   def Sampler_Busy( self ):
      self.Parent.update_idletasks()
      self.Busy_Value = self.Busy_Value + 1
      if self.Busy_Value > 10:
         self.Parent.update()
         self.Busy_Value = 0
         if self.Busy_Label_Var.get() <> 'X':
            self.Busy_Label_Var.set( 'X' )
         else:
            self.Busy_Label_Var.set( 'o' )
      
   def SAMPLE( self ):
      if 0:
         self.Busy_Window = Window = Toplevel( self.Window )
         Window.title( 'XWisp - Sampling' )
         Window.iconname( 'Sampling' )
         SetIcon( Window )

         self.Busy_Value = 0
         self.Busy_Label_Var = StringVar()
         Button( Window, 
            text="Cancel", 
            command=lambda: self.Sampler_Cancel()
         ).pack()   
         Label( Window, textvariable = self.Busy_Label_Var ).pack()
         self.Parent.update()
      
      self.Trigger = Line_Trigger( 
         self.Preserved.Trigger_Immediately,
         self.Preserved.Trigger_Line,
         self.Preserved.Trigger_Event )
      Before = self.Preserved.Trigger_Before
      if self.Preserved.Trigger_Immediately:
         Before = 0         
   
      self.Parent.Connect_If_Needed()
      print "sample start"
      self.Preserved.Data = self.Parent.Bus_Target.Sample( 
         Before = self.Preserved.Trigger_Before,
         After  = self.Preserved.Trigger_After, 
         Trigger = self.Trigger,
         Idle = None )
         # Idle = self.Sampler_Busy )
      print "sample end"   
      # self.Busy_Window.destroy()
         
      self.Preserved.N_Samples = len( self.Preserved.Data )
      self.Preserved.Trigger_N = Before
      if 0: # for debugging
         for i in range( 0, len( self.Data )):
           print "%3d : %02X  %s" % ( 
              i, 
              ord( self.Data[ i ] ), 
              binary( ord( self.Data[ i ]), 8, ' *', ' .' ))
      self.Process_Data()
      self.Redraw()
      
   def unused_Config_Port_Update( self, Window, Var, Update ):
      if Update:
         self.PortName = Var.get()
         self.CMD_PORT( self.PortName )
         self.GuiLog( 'now using serial port [%s]' % self.PortName, Indent = 0 )
      Window.destroy()
      
   def Sampler_Configure_Leave( self, Update ):
      if Update:
         self.Preserved.Trigger_Immediately = self.Trigger_Immediately.get()
         self.Preserved.Trigger_Line = self.Trigger_Line.get()
         self.Preserved.Trigger_Event = self.Trigger_Event.get()
         try:
            self.Preserved.Trigger_Before = int( self.Samples_Before.get() )
         except:
            pass
         try:
            self.Preserved.Trigger_After = int( self.Samples_After.get() )
         except:
            pass
         
      self.Sampler_Window.destroy()
         
   def Sampler_Configure_Update( self ):
      for Button in self.Lines_Buttons:
         if self.Trigger_Immediately.get():
            Button.configure( state = DISABLED )
         else:
            Button.configure( state = NORMAL )         
      if self.Trigger_Immediately.get():
         self.Before_Entry.configure( state = DISABLED )
      else:
         self.Before_Entry.configure( state = NORMAL )         
               
   def SAMPLER_CONFIGURE( self ):
      self.Sampler_Window = Window = Toplevel( self.Window )
      Window.title( 'XWisp - Logic Analyser - Configure Sampler' )
      Window.iconname( 'Sampler' )
      SetIcon( Window )
      
      self.Trigger_Immediately = IntVar( 
         value = self.Preserved.Trigger_Immediately )
      self.Trigger_Line = IntVar( 
         value = self.Preserved.Trigger_Line )
      self.Trigger_Event = IntVar( 
         value = self.Preserved.Trigger_Event )

      Trigger_Frame = Frame( Window, borderwidth = 5, relief = SUNKEN )
      Trigger_Frame.pack( side = TOP, fill = Tkinter.BOTH, expand = YES )
      
      Label( Trigger_Frame, text = "Trigger " ).pack( side = LEFT )
      
      Immediate_Frame = Frame( Trigger_Frame )
      Immediate_Frame.pack( side = LEFT )
      
      Radiobutton( Immediate_Frame, 
         text = "immediately",     
         variable = self.Trigger_Immediately,
         value = 1,
         command=lambda: self.Sampler_Configure_Update()
      ).pack( side = TOP, anchor = Tkinter.W )
      Radiobutton( Immediate_Frame, 
         text = "when line ",     
         variable = self.Trigger_Immediately,
         value = 0,
         command=lambda: self.Sampler_Configure_Update()
      ).pack( side = TOP, anchor = Tkinter.W )
      
      self.Lines_Buttons = []
      
      Line_Frame = Frame( Trigger_Frame )
      Line_Frame.pack( side = LEFT )
      
      for Index in range( 0, self.N_Data_Lines ):
         Name, Color, Text = self.Track_Info[ Index ]
         B = Radiobutton( Line_Frame, 
            text = Name,     
            variable = self.Trigger_Line,
            value = Index,
            command=lambda: self.Sampler_Configure_Update())
         B.pack( side = TOP, anchor = Tkinter.W )
         self.Lines_Buttons.append( B )

      Event_Frame = Frame( Trigger_Frame )
      Event_Frame.pack( side = LEFT )
      for Index, Name in (
         ( 0, 'changes' ),
         ( 1, 'rises (from 0 to 1)' ),
         ( 2, 'falls (from 1 to 0)' ),
         ( 3, 'is high (1)' ),
         ( 4, 'is low (0)' ),
      ):
         B = Radiobutton( Event_Frame, 
            text = Name,     
            variable = self.Trigger_Event,
            value = Index,
            command=lambda: self.Sampler_Configure_Update())
         B.pack( side = TOP, anchor = Tkinter.W )
         self.Lines_Buttons.append( B )  
         
      Store_Frame = Frame( Window, borderwidth = 4, relief = SUNKEN )          
      Store_Frame.pack( side = TOP, fill = Tkinter.BOTH, expand = YES )

      Label( Store_Frame, text = "Store " ).pack( side = LEFT )
       
      Before_Frame = Frame( Store_Frame )          
      Before_Frame.pack( side = TOP, anchor = Tkinter.NW )
      After_Frame = Frame( Store_Frame )          
      After_Frame.pack( side = TOP, anchor = Tkinter.NW )
      
      self.Samples_Before = StringVar( 
         value = str( self.Preserved.Trigger_Before ))
      self.Samples_After = StringVar( 
         value = str( self.Preserved.Trigger_After ))
      
      self.Before_Entry = Entry( 
         Before_Frame, 
         textvariable = self.Samples_Before,
         width = 8
      )
      self.Before_Entry.pack( side = LEFT )     
      Label( 
         Before_Frame, text = "samples before the trigger moment" 
      ).pack( side = LEFT )
      Tkinter.Entry( 
         After_Frame, 
         textvariable = self.Samples_After,
         width = 8
      ).pack( side = LEFT )
      Label( 
         After_Frame, text = "samples after the trigger moment" 
      ).pack( side = LEFT )
     
      Actions_Frame = Frame( Window )          
      Actions_Frame.pack( side = BOTTOM )
      
      Button( Actions_Frame, 
         text="OK",     
         command=lambda: self.Sampler_Configure_Leave( 1 )
      ).pack( side = LEFT )
      Button( Actions_Frame, 
         text="Cancel", 
         command=lambda: self.Sampler_Configure_Leave( 0 )
      ).pack( side = RIGHT )   
            
      self.Sampler_Configure_Update()
      
   def Get_Settings_From_GUI( self ):
      try:
         self.Preserved.Origin = self.Origin_Scale.get()
         self.Preserved.Span = self.Span_Scale.get()
      except:
         pass
         
   def Tracks_Change( self ):
      # print "visible tracks change"
      for Index in range( 0, len( self.Track_Visible )):
         self.Preserved.Visible_Tracks[ Index ] = \
            self.Track_Visible[ Index ].get()
      self.Redraw()
      
   def Process_Data( self ):
      Y = [ [], [], [], [], [], [] ]
      for X in self.Preserved.Data:
         Y[ 0 ].append( ( ord( X ) >> 0 ) & 1 )
         Y[ 1 ].append( ( ord( X ) >> 1 ) & 1 )
         Y[ 2 ].append( ( ord( X ) >> 2 ) & 1 )
         Y[ 3 ].append( ( ord( X ) >> 3 ) & 1 )
         Y[ 4 ].append( ( ord( X ) >> 4 ) & 1 )
         Y[ 5 ].append( ( ord( X ) >> 7 ) & 1 )
      self.Tracks = []
      for Index in range( 0, 6 ):
         Name, Color, Text = self.Track_Info[ Index ]
         self.Tracks.append( Digital_Track( Y[ Index ], Name, Color ))        
      Name, Color, Text = self.Track_Info[ 6 ]         
      self.Tracks.append( Counter_Track( Name ))       
      Name, Color, Text = self.Track_Info[ 7 ]
      self.Tracks.append( Time_Track( Name ))          
      
   def Redraw( self, Dummy = None ):
      self.Get_Settings_From_GUI()
   
      for Item in self.GUI_Items:
         Item.destroy()
         
      Buttons_Frame = Frame( self.Window )
      Canvas_Frame = Frame( self.Window )
      Origin_Scale_Frame = Frame( self.Window )
      Span_Scale_Frame = Frame( self.Window )
      Origin_Labels_Frame = Frame( Origin_Scale_Frame )
      Span_Labels_Frame = Frame( Span_Scale_Frame )
      self.GUI_Items = [ 
         Buttons_Frame, Canvas_Frame,
         Origin_Scale_Frame, Span_Scale_Frame, 
         Origin_Labels_Frame, Span_Labels_Frame 
      ]
      
      Span_Scale_Frame.pack( side = BOTTOM, anchor = Tkinter.SE )
      Origin_Scale_Frame.pack( side = BOTTOM, anchor = Tkinter.SE )
      Buttons_Frame.pack( side = LEFT, anchor = Tkinter.NW )
      Canvas_Frame.pack( side = RIGHT, anchor = Tkinter.NE )
      Origin_Labels_Frame.pack( side = LEFT, anchor = Tkinter.E )
      Span_Labels_Frame.pack( side = LEFT, anchor = Tkinter.E )
      
      self.SampleButton = Button( 
         Buttons_Frame, text = "SAMPLE", command = self.SAMPLE )
      self.GUI_Items.append( self.SampleButton )
      self.SampleButton.pack( side = LEFT )      
      
      Y = ( 2 * self.Preserved.Canvas_Y_Border_Margin +
         self.Preserved.Canvas_Border )
      Extra = 0
      for Index in range( 0, len( self.Preserved.Visible_Tracks )):
         if self.Preserved.Visible_Tracks[ Index ]:
            Y = Y + self.Preserved.Canvas_Track_Height + Extra
            Extra = self.Preserved.Canvas_Y_Track_Margin
      self.Canvas_Height = Y
      
      self.Canvas = Canvas( 
         Canvas_Frame, 
         width = self.Preserved.Canvas_Width, 
         height = self.Canvas_Height,
         borderwidth = self.Preserved.Canvas_Border,
         relief = self.Preserved.Canvas_Border_Effect 
      )
      self.Canvas.pack( side = RIGHT )
      self.Canvas.Width = self.Preserved.Canvas_Width   
      self.Canvas.Height = self.Canvas_Height  
      self.GUI_Items.append( self.Canvas )
      
      Samples_Per_Tick = (( self.Preserved.N_Samples * 
         self.Preserved.Tick_Pixels ) 
         / self.Preserved.Canvas_Width )
      Dummy, Ti = Scale_Up( Samples_Per_Tick )
      
      self.Origin_Scale_Var = StringVar()
      self.Origin_Scale = Scale( 
         Origin_Scale_Frame, 
         orient = HORIZONTAL, 
         length = self.Preserved.Canvas_Width, 
         from_ = 0, 
         to = self.Preserved.N_Samples, 
         tickinterval = Ti, 
         showvalue = 0,
         variable = self.Origin_Scale_Var,
         command = self.Redraw_Canvas )
      self.GUI_Items.append( self.Origin_Scale )
      self.Origin_Name_Label = Label( 
         Origin_Labels_Frame, text = 'X Origin' )
      self.GUI_Items.append( self.Origin_Name_Label )
      self.Origin_Value_Label = Label( 
         Origin_Labels_Frame, 
         width = 4,
         bg = self.Preserved.Scale_Value_BG, 
         textvariable = self.Origin_Scale_Var )
      self.GUI_Items.append( self.Origin_Value_Label )

      self.Origin_Value_Label.pack( side = TOP )
      self.Origin_Name_Label.pack( side = TOP )
      self.Origin_Scale.pack( side = RIGHT )
      
      self.Span_Scale_Var = StringVar()
      self.Span_Scale = Scale( 
         Span_Scale_Frame, 
         orient = HORIZONTAL, 
         length = self.Preserved.Canvas_Width, 
         from_ = 10, 
         to = self.Preserved.N_Samples, 
         tickinterval = Ti, 
         showvalue = 0,
         variable = self.Span_Scale_Var,
         command = self.Redraw_Canvas )
      self.GUI_Items.append( self.Span_Scale )
      self.Span_Name_Label = Label( Span_Labels_Frame, text = 'X Span' )
      self.GUI_Items.append( self.Span_Name_Label )
      self.Span_Value_Label = Label( 
         Span_Labels_Frame, 
         width = 4,
         bg = self.Preserved.Scale_Value_BG, 
         textvariable = self.Span_Scale_Var )
      self.GUI_Items.append( self.Span_Value_Label )
            
      self.Span_Value_Label.pack( side = TOP )
      self.Span_Name_Label.pack( side = TOP )
      self.Span_Scale.pack( side = RIGHT )
        
      self.Origin_Scale.set( self.Preserved.Origin )
      self.Span_Scale.set( self.Preserved.Span )
            
      self.Redraw_Canvas()
      
   def Redraw_Canvas( self, Dummy = None ):
      C = self.Canvas
      C.delete( ALL )
      C.create_rectangle( 
         self.Preserved.Canvas_Border, self.Preserved.Canvas_Border, 
         C.Width, C.Height, 
         fill = self.Preserved.Canvas_BG, 
         outline = '' )
         
      #self.Origin_Value_Label.set( str( Origin_Scale_Var.get()))
      #self.Span_Value_Label.set( str( Span_Scale_Var.get() ) )

      Low_Y = ( self.Preserved.Canvas_Y_Border_Margin + 
         self.Preserved.Canvas_Border )
      Y = ( self.Preserved.Canvas_Y_Border_Margin + 
         self.Preserved.Canvas_Track_Height +
         self.Preserved.Canvas_Border ) 
      X = self.Preserved.Canvas_X_Border_Margin + \
                  self.Preserved.Canvas_Border
      XW = C.Width - ( 2 * self.Preserved.Canvas_X_Border_Margin )
      Index = 0
      for T in self.Tracks:
         if self.Preserved.Visible_Tracks[ Index ]: 
            T.Draw( 
               self.Canvas, 
               X,
               Y, 
               XW, 
               self.Preserved.Canvas_Track_Height, 
               self.Origin_Scale.get(), self.Span_Scale.get() ) 
            YW = Y - Low_Y
            Y = Y + self.Preserved.Canvas_Track_Height + \
               self.Preserved.Canvas_Y_Track_Margin
         Index = Index + 1
         
      if self.Preserved.Trigger_N <> None:
         self.Trigger_Track = \
            Marker_Track( self.Preserved.Trigger_N, 'GREEN' )
         self.Trigger_Track.Draw( 
            self.Canvas, 
            X, Low_Y, XW, YW, 
            self.Origin_Scale.get(), self.Span_Scale.get() )
                  
   
#############################################################################
#
# GUI 2
#
# classic GUI
#
#############################################################################

# --- ToDo ---
# GUI should use startup files?
# truncate long text in log
# use message io text?
# arrange
# erase reads??
# target select
# target identify
# get should clear image file name?
# failed read should clear image file name?
# start terminal
# config: auto terminal, baudrate, mode
# set/clear RTS/DTS
# remember target flag is not remembered?
# target is now always remembered?
# exception: communication
# local config file (doubleclick!)
# save log file
# build-in blink and other test files (recompile? assembly on the fly? - won't work on Linux :()
# serial monitor!

class XWisp_GUI( Wisp_Line, Frame ):
   def __init__( self, StartFile = None, Line = None ):
         
      #TempName = 'd:/wouter/xwisp/xwisptemp.ico'
      #self.iconImage=Tkinter.PhotoImage(master=self, data=icon)
      #self.iconImage.write( TempName )
      #tk = Tk()
      # tk.iconbitmap(default=TempName)
      # tk.iconbitmap(default=None)
      # tk.iconbitmap(default=self.iconImage)
      # tk.iconbitmap(default='d:/wouter/xwisp/wesp1.ico')
      
      Wisp_Line.__init__( self, Console = self)      
      Frame.__init__( self )
      self.pack( expand = YES, fill = BOTH )
      self.master.title( 'XWisp ' + Version )
      self.master.iconname( 'XWisp' )
      SetIcon( self.master )

      # self.master.iconbitmap( bitmap = None )
      # self.master.iconbitmap( bitmap = self.iconImage)
      
      mBar = Frame( self, relief = RAISED, borderwidth = 2 )
      mBar.pack( fill = X )
      
      File = Menubutton( mBar, text = 'File', underline = 0 )
      File.pack( side = LEFT, padx = "2m" )
      File.menu = Menu( File )
      File.menu.add_command( label = "Load", underline = 0, command = self.Load  )
      File.menu.add_command( label = "Save", underline = 0, command = self.Save  )
      File.menu.add_command( label = "Save As", underline = 5, command = self.SaveAs  )
      File.menu.add_separator()
      File.menu.add_command( label = "Quit", underline = 0, command = File.quit )
      File[ 'menu' ] = File.menu
      
      Config = Menubutton( mBar, text = 'Configure', underline = 0 )
      Config.pack( side = LEFT, padx = "2m" )
      Config.menu = Menu( Config )
      Config.menu.add_command( label = "Serial Port", underline = 7, command = self.Config_Port  )
      Config.menu.add_command( label = "Target PIC", underline = 0, command = self.Config_Target  )
      Config.menu.add_separator()
      self.RememberTargetVar = StringVar()
      Config.menu.add_checkbutton( label = "Remember target", variable = self.RememberTargetVar  )
      Config[ 'menu' ] = Config.menu
      
      Target = Menubutton( mBar, text = 'Action', underline = 0 )
      Target.pack( side = LEFT, padx = "2m" )
      Target.menu = Menu( Target )
      Target.menu.add_command( label = "Go", underline = 0, command = self.GO )
      Target.menu.add_separator()
      Target.menu.add_command( label = "Erase", underline = -1, command = self.ERASE  )
      Target.menu.add_command( label = "Dump", underline = -1, command = self.DUMP  )
      Target.menu.add_command( label = "Get", underline = -1, command = self.GET )
      Target.menu.add_command( label = "Put", underline = -1, command = self.PUT  )
      Target.menu.add_command( label = "Reset", underline = -1, command = self.RESET  )
      Target.menu.add_command( label = "Run", underline = -1, command = self.RUN  )
      Target.menu.add_command( label = "Verify", underline = -1, command = self.VERIFY  )
      # enable logica analyser
      if 1:
         Target.menu.add_separator()
         Target.menu.add_command( label = "Logic Analyser", underline = 6, command = self.Create_Analyser )
      Target.menu.add_separator()
      Target.menu.add_command( label = "Pins", underline = 0, command = self.Manipulate_Pins )
      Target[ 'menu' ] = Target.menu
      
      Help = Menubutton( mBar, text = 'Help', underline = 0 )
      Help.pack( side = LEFT, padx = "2m" )
      Help.menu = Menu( Help )
      # Help.menu.add_command( label = "Help", underline = 0, command = self.HELP )
      Help.menu.add_command( label = "About", underline = 0, command = self.ABOUT )
      Help[ 'menu' ] = Help.menu
      
      self.FileNameVar = StringVar()
      self.FileNameLabel = Label( self  )
      self.SetFileName( '' )     
       
      self.LoadButton = Button( self, text = "Load File", comman = self.Load )
      self.GetButton = Button( self, text = "Get", comman = self.GET )
      self.PutButton = Button( self, text = "Put", comman = self.PUT )
      self.EraseButton = Button( self, text = "Erase", comman = self.ERASE )
      self.VerifyButton = Button( self, text = "Verify", comman = self.VERIFY )
      self.DumpButton = Button( self, text = "Verify", comman = self.DUMP )
      self.GoButton = Button( self, text = "Reset", comman = self.RESET )
      self.GoButton = Button( self, text = "Run", comman = self.RUN )
      self.GoButton = Button( self, text = "Go", comman = self.GO )
      self.ReadButton = Button( self, text = "Load", comman = self.RELOAD )
      self.WriteButton = Button( self, text = "ReSave", comman = self.RESAVE )
      
      self.FileNameLabel.pack()
      self.LoadButton.pack( side = LEFT )
      self.GoButton.pack( side = LEFT )
      
      self.LogWindow = Text( self, height = 20, width = 80, font=( "courier", 8 ) )
      self.LogScroll = Scrollbar( self, command = self.LogWindow.yview )
      self.LogWindow.pack( side = LEFT )
      self.LogScroll.pack( side = RIGHT, fill = Y )      
      
      mBar.tk_menuBar( File, Config, Target )
      
      self.FileName = None
      self.Last_Line = None
      self.LastIndent = 0
      self.FirstLine = 1
      self.StartFile = StartFile
      self.LogLine = 0
      
      self.Interpret(Line[:-1], Line_Mode = 0)
                        
   def Main( self ):
      # get config file location
      ###self.ConfigFile = app_util.user_data_dir( 'XWisp', 'VOTI' )
      
      # try to read config file
      try:
         f = open( self.ConfigFile, 'r' )
         try:
            self.Config = pickle.load( f )
         except:
            f.close()
            raise
         f.close()
         self.GuiLog( 'read configuration from\n   [%s]' % self.ConfigFile, Indent = 0 )
         
      except:
      
         # error while reading: empty config file
         self.Config = Empty_Class()
         
         # maybe the directory did not exist: try to create it
         try:
            os.makedirs( os.path.dirname( self.ConfigFile ))
         except: pass
         
      # update create GUI variables from config
      try:
         self.RememberTargetVar.put( self.Config.RememberTarget )
      except: pass
      self.PortName = ''
      try:
         self.PortName = self.Config.PortName
      except: pass
      self.Target_Name = None
      try:
         self.Target_Name = self.Config.Target_Name
      except: pass      
         
      # startup
      if self.PortName != '':
         self.GuiLog( 'using serial port [%s]' % self.PortName, Indent = 0 )
         self.CMD_PORT( self.PortName )
         
      if self.StartFile != None:
         self.SetFileName( self.StartFile )
         self.GuiLog( 'LOAD ' + self.FileName, 0 )
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'LOAD', self.FileName ])
         
      self.Update_Target( self.Target_Name )
         
      # main loop of the GUI
      self.mainloop()
      
      # update configuration from GUI variables
      self.Config.RememberTarget = self.RememberTargetVar.get()
      self.Config.Target_Name = None
      if self.Config.RememberTarget:
         self.Config.Target_Name = self.Target_Name
      self.Config.PortName = self.PortName      
      
#      # try to save the configuration
#      f = open( self.ConfigFile, 'w' )
#      try:
#         pickle.dump( self.Config, f )
#      except:
#         f.close()
#         raise
#      f.close()      
      
   def SetFileName( self, T ):
      S = 'file : ' + T
      if T == '':
         S = 'file : <not yet specified>'
      self.FileNameLabel.config( text = S )
      self.FileName = T
      
   def GuiLog( self, Text, Indent, Newline = 1 ):
      self.LastIndent = Indent
      
      T = Text.split( '\n' )
      for Line in T:
         if Newline and not self.FirstLine :
            self.LogWindow.insert( END, '\n' )            
         self.FirstLine = 0
         self.LogLine = self.LogLine + 1
         self.LogWindow.insert( END, ( "%03d " % self.LogLine ))
         if Indent:
            self.LogWindow.insert( END, Repeat( ' ', 3 * Indent ))
         self.LogWindow.insert( END, Line )
      self.LogWindow.see( END )
      self.update_idletasks()
      
   def Log( self, Text ):
      self.GuiLog( Text, '   ' )      
      
   def Create_Analyser( self ):
      A = Analyser( self )
         
   def Print( self, S, Progress = 0 ):
      if self.Last_Line <> None:
         self.LogWindow.delete( self.Last_Line, END)
         self.Last_Line = None
      if Progress:
         self.Last_Line = self.LogWindow.index( END )
      T = ( '\n' + S ).replace( '\n', '\n' + Repeat( ' ', 3 * ( 1 + self.LastIndent )))
      self.LogWindow.insert( END, T, 'last' )
      self.LogWindow.see( END )
      self.update_idletasks()
      
   def Update_Target( self, Target ):
      self.Target_Name = Target
      if self.Target_Name == None:
         self.GuiLog( 'target PIC chip will be autodetected', Indent = 0 )      
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'TARGET', 'AUTO' ])
      else:   
         self.GuiLog( 'target PIC chip is %s' % self.Target_Name, Indent = 0 )      
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'TARGET', self.Target_Name ])
      
   def Config_Target_Update( self, Window, List, Update ):      
      if Update == 1:
         X = List.curselection()
         if len( X ) > 0:
            self.Update_Target( _PIC_Types_List[ int( X[ 0 ] ) ] )
      if Update == 2:
         self.Update_Target( None )
      Window.destroy()
         
   def Config_Target( self, Indent = 0 ):
      W = get_window = Toplevel( self )
      W.title( 'select target PIC' )
      L = Listbox( W, height = 20, width = 20  )
      S = Scrollbar( W, command= L.yview )
      L.pack( side = LEFT )
      S.pack( side = RIGHT, fill = Y )
      for P in _PIC_Types_List:
         L.insert( END, P )   
      Button( W, text="Autodetect",  command=lambda: self.Config_Target_Update( W, L, 2)).pack()
      Button( W, text="OK",          command=lambda: self.Config_Target_Update( W, L, 1)).pack()
      Button( W, text="Cancel",      command=lambda: self.Config_Target_Update( W, L, 0)).pack()      
      
   def Load( self, Indent = 0 ):
      Answer = tkFileDialog.askopenfilename( 
         defaultextension = '.hex', 
         filetypes = ( ('hex files', '*.hex'), ('all files', '*' ) ),
         initialfile = self.FileName )
      if Answer != '':
         self.SetFileName( Answer )
         self.GuiLog( 'LOAD ' + self.FileName, Indent )
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'LOAD', self.FileName ])
         
   def Save( self, Indent = 0 ):
      if self.FileName == None:
         Answer = tkFileDialog.asksaveasfilename( 
            defaultextension = '.hex', 
            filetypes = ( ('hex files', '*.hex'), ('all files', '*' ) ),
            initialfile = self.FileName )
         if Answer != '':
            self.SetFileName( Answer )
         else:
            return
      if self.FileName != None:
         self.GuiLog( 'SAVE ' + self.FileName, Indent )
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'SAVE', self.FileName ])
         
   def SaveAs( self, Indent = 0 ):
      Answer = tkFileDialog.asksaveasfilename( 
         defaultextension = '.hex', 
         filetypes = ( ('hex files', '*.hex'), ('all files', '*' ) ),
         initialfile = self.FileName )
      if Answer != '':
         self.GuiLog( 'SAVE AS ' + Answer, Indent ) 
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'SAVE', Answer ])
         
   def Config_Port_Update( self, Window, Var, Update ):
      if Update:
         self.PortName = Var.get()
         self.CMD_PORT( self.PortName )
         self.GuiLog( 'now using serial port [%s]' % self.PortName, Indent = 0 )
      Window.destroy()
         
   def Config_Port( self, Indent = 0 ):
      W = get_window = Toplevel( self )
      W.title( '' )
      P = StringVar()
      P.set( self.PortName )
      Label( W, text = 'Port:' ).pack()
      Entry( W, width=20, textvariable = P ).pack()
      Button( W, text="OK",     command=lambda: self.Config_Port_Update( W, P, 1 )).pack()
      Button( W, text="Cancel", command=lambda: self.Config_Port_Update( W, P, 0 )).pack()
      
   def Manipulate_Pins_Send_Receive( self, M, N = 0 ):
      # print "send [%s]" % M
      self.Bus_Target.Bus.Send_Expect( M )
      return self.Bus_Target.Bus.Get( N )
            
   def Manipulate_Pins_Timer( self, Window ):
      Window.State += 1
      if Window.State > 5:
         Window.State = 0
         if Window.Blink_State:
            Window.Blinker.config( text = 'X' )
            Window.Blink_State = 0
         else:
            Window.Blinker.config( text = 'O' )
            Window.Blink_State = 1     
            
      if Window.State == 1:
         self.Manipulate_Pins_Send_Receive( Hex_From_List( Window.Values[ 0 ] ) + '5P' )
      if Window.State == 2:
         self.Manipulate_Pins_Send_Receive( Hex_From_List( Window.Values[ 1 ] ) + '6P' )
      if Window.State == 3:
         self.Manipulate_Pins_Send_Receive( Hex_From_List( Window.Values[ 2 ] ) + '7P' )
      if Window.State == 4:   
         Response = self.Manipulate_Pins_Send_Receive( "0005P", 3 )
         Binary = Bin_From_Hex( Response )
         for C, Indicator in map( None, Binary, Window.Indicators ):
            Indicator.config( text = ( ( C == '0' ) and ' 0 ' or ' 1 ' ))
            
      Window.after( 50, lambda: self.Manipulate_Pins_Timer( Window ))
           
   def Manipulate_Pins_Update( self, Window, Name, Index, Command ):
      # print Name, Index, Command
      if Command < 3 : 
         for x in [ 0, 1, 2 ]:
            Window.Values[ x ][ Index ] = 0
         Window.Values[ Command ][ Index ] = 1
      else:
         Window.destroy()
         
   def Add_Button_Row( self, W, N, Index, Name ):
      Label( W, text = Name, font='Courier 8' ).grid( row = N, column = 0 )
      W.ButtonVar.append( IntVar( 0 ))
      Radiobutton( W, 
         text      = "Input", 
         variable  = W.ButtonVar[ N ], 
         value     = 0, 
         indicatoron = 0,
         command   = lambda: self.Manipulate_Pins_Update( W, Name, Index, 0 )
      ).grid( row = N, column = 1 )
      Radiobutton( W, 
         text      = " 1 ",  
         variable  = W.ButtonVar[ N ], 
         value     = 1, 
         indicatoron = 0,
         command   = lambda: self.Manipulate_Pins_Update( W, Name, Index, 1 )
      ).grid( row = N, column = 2 )
      Radiobutton( W, 
         text      = " 0 ",   
         variable  = W.ButtonVar[ N ], 
         value     = 2, 
         indicatoron = 0,
         command   = lambda: self.Manipulate_Pins_Update( W, Name, Index, 2 )
      ).grid( row = N, column = 3 )
      Indicator = IntVar()
      Indicator = Label( W, text = ' ? ', font='Courier 8' )       
      Indicator.grid( row = N, column = 4 )
      Label( W, text = '  ', font='Courier 8' ).grid( row = N, column = 5 )  
      W.Values[ 0 ].append( 1 ) 
      W.Values[ 1 ].append( 0 ) 
      W.Values[ 2 ].append( 0 )
      W.Indicators.append( Indicator )

   def Manipulate_Pins( self ):
      W = Toplevel( self )
      W.title( 'XWisp - direct pin access' )
      W.Values = [ [], [], [] ]
      W.ButtonVar = []      
      W.Indicators = []
      N = 0
      for Index, Name in (
         (  0, 'RA0 : clock pin (green)    ' ),
         (  1, 'RA1 : reset pin            ' ),
         (  2, 'RA2 : pump feed pin        ' ),
         (  3, 'RA3 : power short pin      ' ),
         (  4, 'RA4 : led pin              ' ),
         (  5, 'RA5 : dummy pin            ' ),
         (  6, 'RB0 : pump 1 pin           ' ),
         (  7, 'RB3 : pump 2 pin           ' ),
         (  8, 'RB4 : aux 2 pin            ' ),
         (  9, 'RB5 : data pin (blue)      ' ),
         ( 10, 'RB6 : aux 1 pin            ' ),
         ( 11, 'RB7 : pulldown pin (white) ' ),
      ): 
         self.Add_Button_Row( W, N,Index, Name )
         N += 1
      W.Indicators.reverse()
      Button( W, text="-- Exit --", command=lambda: self.Manipulate_Pins_Update( W, Name, 0, 3 )).grid( row = N, column = 0 )
      W.Blinker = Label( W, text = 'O' )
      W.Blinker.grid( row = N, column = 2 )
      W.Blink_State = 0
      W.State = 0
      self.Connect_If_Needed()
      W.after( 1, lambda: self.Manipulate_Pins_Timer( W ))  
         
   def ABOUT( self ):
      W = get_window = Toplevel( self )
      W.title( 'about XWisp' )
      Label( W, text = \
         "XWisp " + Version + '\n\n'
         "PC software for the Wisp648 PIC programmer.\n\n"
         "http://www.voti.nl/xwisp\n"
         "http://www.voti.nl/wisp648\n"
      ).pack()
      Button( W, text="OK",     command=lambda: self.Close_Window( W ) ).pack()

   def DUMP( self, Indent = 0 ):
      self.GuiLog( 'DUMP ', Indent ) 
      self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'DUMP' ])
               
   def ERASE( self, Indent = 0 ):          
      self.GuiLog( 'ERASE ', Indent ) 
      self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'ERASE' ])
         
   def GET( self, Indent = 0 ):          
      self.GuiLog( 'GET ', Indent ) 
      self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'GET' ])
   
   def GO( self, Indent = 0 ):
      self.GuiLog( 'GO ', Indent ) 
      if self.FileName == None:
         self.Load( Indent = 1 )
         self.LastIndent = Indent
      if self.FileName != None:
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'GO', self.FileName ])
         
   def HELP( self ):
      pass
      
   def PUT( self, Indent = 0 ):          
      self.GuiLog( 'PUT ', Indent ) 
      self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'PUT' ])
         
   def RELOAD( self, Indent = 0 ):
      if self.FileName == None:
         pass
      else:
         self.GuiLog( 'RELOAD ' + self.FileName, Indent )
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'RELOAD', self.FileName ])
         
   def RESAVE( self, Indent = 0 ):
      if self.FileName == None:
         pass
      else:
         self.GuiLog( 'RESAVE ' + Answer, Indent ) 
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'SAVE', self.FileName ])      
         
   def RESET( self, Indent = 0 ):
      self.GuiLog( 'RSET ', Indent ) 
      self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'RESET' ])
               
   def RUN( self, Indent = 0 ):
      self.GuiLog( 'RUN ', Indent ) 
      self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'RUN' ])
               
   def VERIFY( self, Indent = 0 ):          
      if self.FileName == None:
         self.Load( Indent = 1 )
      if self.FileName != None:
         self.GuiLog( 'VERIFY ', Indent ) 
         self.Interpret( Show_Version = 0, Line_Mode = 0, Line = [ 'VERIFY', self.FileName ])
         
   def Close_Window( self, Window ):
      Window.destroy()         
      
   def unused_Config_Port_Update( self, Window, Var, Update ):
      if Update:
         self.PortName = Var.get()
         self.CMD_PORT( self.PortName )
         self.GuiLog( 'now using serial port [%s]' % self.PortName, Indent = 0 )
      Window.destroy()         
                        
if 0:   
   XWisp_GUI().mainloop()   
   print "exit"
   exit()

#############################################################################
#
# main
#
#############################################################################

def Global_Config_File_Name():
   import sys, os
   return os.path.join( 
      os.path.abspath( os.path.dirname( sys.argv[ 0 ])),
      'XWisp.ini' )
   
def Local_Config_File_Name():
   return 'XWisp.ini'   

def XWisp_Main():
   import sys, os
   # print ">>>", os.path.expanduser('~')
   Line = sys.argv[1:]
   if sys.argv[0].find( "xwisp_gui" ) > 0:
      if len( Line ) > 0:
         File = Line[ 0 ]
         Wisp = XWisp_GUI( StartFile = File ).Main()
      else:
         Wisp = XWisp_GUI().Main()   
   elif len( Line ) == 0:
      Wisp_Line().Interpret()
   else:
      File = Line[ -1 ]
      Dummy, Extension = os.path.splitext( File.upper())
      # print File.upper(), Dummy, Extension
      if Dummy == 'BUTTON':
         File = Line[ 1 ]
         Dummy, Extension = os.path.splitext( File.upper())
         Wisp = Wisp_Window()
         Wisp.Run_File_If_Exists( Global_Config_File_Name() )
         Wisp.Run_File_If_Exists( Local_Config_File_Name() )
         File.replace( ' ', '_' )
         Wisp.Interpret( 
            'button text go_' + File.replace( ' ', '_' ) + \
            ' xwisp go "' + File + '"' )
         Wisp.Mainloop()
      elif ( Dummy == 'GUI' ):
         Wisp = XWisp_GUI().Main()
      elif ( Extension == '.HEX' ):
         Wisp = XWisp_GUI( StartFile = File, Line = Line ).Main()
      elif Extension == '.XWISP':
         Wisp = Wisp_Window()
         Wisp.Run_File_If_Exists( Global_Config_File_Name() )
         Wisp.Run_File_If_Exists( Local_Config_File_Name() )
         Wisp.Run_File( File )
         Wisp.Mainloop()
      else:
         Wisp_Line().Interpret()
         
if __name__ == '__main__':
   XWisp_Main()

