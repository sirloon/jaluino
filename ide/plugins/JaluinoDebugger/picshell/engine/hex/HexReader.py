from picshell.engine.hex.HexLine import HexLine
#
# 14/16 bit Hex Reader
#

class HexReader:

    def __init__(self, maxCodeSize ):
       self.maxCodeSize = maxCodeSize
       
    def readData(self,filename, code):
        codeIndex = 0
        lastAddress = 0

        
        #
        # Init flash code
        #
        for i in range (len(code)):
            code[i]="11111111"+"11111111";
        
        #
        # fill  flash code with hex file content 
        #
        fin = None
        try:                            # file IO is "dangerous"
            fin = open(filename,"r")    # open input.txt, mode as in c fopen
            base_offset = 0x00
            for line in fin:            # implements iterator interface (readline loop)
                hexLine = self._adapt(line)
                #print line
                
                # AF add base offset for 18F support
                codeIndex =int(hexLine.loadAdress,16)/2 + base_offset # loadAdress is in hex

                #print "%02X " % hexLine.recordType + " addr %06X " % ( int(hexLine.loadAdress,16)/2  ) + " LEN %d \n" % ( len(hexLine.data) / 4 )
                #print hexLine.recordsLength
                #print hexLine.recordType
                #print hexLine.loadAdress
                #print hexLine.data

                # check if within code area in order to exclude config & location IDs
                if codeIndex < len(code): 
                    if hexLine.recordType == "00" :
                        for i in range( 0, len(hexLine.data), 4 ) :
                            part1 = hexLine.data[i:i+2]
                            part2 = hexLine.data[i+2:i+4]
                            # print '>'+part1+' '+part2+" %d" %codeIndex
                            b1 = HexReader.bin(int(part1,16))
                            b2 = HexReader.bin(int(part2,16))
                            
                            if ( codeIndex < self.maxCodeSize ): 
                                code[codeIndex] =  b2 + b1  #TODO : convert to bin
                            
                                # print "maxCodeSize %04X" % self.maxCodeSize 
                                if ( lastAddress < 0x1FFFF ):
                                   lastAddress = codeIndex
                                   #print "LAST ADDRESS %d" % lastAddress
                                codeIndex = codeIndex + 1
                    if hexLine.recordType == "04" :
								part1 = hexLine.data[0:2]
								part2 = hexLine.data[2:4]
								base_offset = ( int(part1,16) << 24 ) + ( int(part2,16) << 16 ) / 2
								
								#print '04 RECORD>'+part1+' '+part2 + ' ' + '%08X' % base_offset
                            
        except IOError, e:                # catch IOErrors, e is the instance
            print "Error in file IO: ", e # print exception info if thrown
        if fin: fin.close()               # cleanup, close fin only if open (not None)
        return lastAddress
    
    def _adapt (self,line):
        line = line.strip()
        hexLine = HexLine()
        hexLine.recordsLength = line[1:3]
        hexLine.loadAdress = line[3:7]
        hexLine.recordType = line[7:9]
        hexLine.checkSum = line[len(line)-2:]
        hexLine.data = line[9:len(line)-2]
        return hexLine
    @staticmethod
    def bin(n):
        res = ''
        while n != 0: n, res = n >> 1, `n & 1` + res
        bin = res
        # pad with leading 0
        for j in range (8,len(res),-1):
            bin = "0" + bin
        return bin
    @staticmethod
    def binf(n):
        res = HexReader.bin(n)
       
        return res[0:4] +"_"+res[4:]