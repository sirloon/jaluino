import re
import os
class DebugStruct:
    address =0;
    line ="";
#
# Parse the asm file to find jal code in comment
#
class JalV2AsmParser:
    
    JAL = 1
    ASM = 2
    mode = JAL # can return JAL Code or ASM Code
    
    def __init__(self):
        self.varAdrMapping = {}
        self.adrVarMapping = {}
        
        # we need both relation as the same address can be mapped to several lines
        # i.e. "end if" hsn't it's own address
       
        self.lineToAdr = [0]*(128*1024)
        self.adrToLine = [0]*(128*1024)
        self.adr =[]       # private int[] adr = null;
        self.adressSet =[] # private Set adressSet = new HashSet();
        self.picName = None        
        for i in range(0,len( self.lineToAdr )):
            self.lineToAdr[i] = None
            self.adrToLine[i] = None
         
    def parseAsmFile(self,filename,noDebugList,debugList=()):
       
        self.varAdrMapping = {}
        self.adrVarMapping = {}
        self.addressMethodMapping = {}
        adresse = 0
        list = []
        meth = ""
        
        line = ""
        lineIndex= 0;
        orgFound = False
        file =""
        libFile =None
        fin = None
        prevLine =""
        pic18f = False
        try:                           
            fin = open(filename,"r")   
            libFile = os.path.basename(file).replace(".jal","")
            
            for line in fin:   
                #if adresse < 400:
                #    print ">> %06X " %  (adresse * 2 ) + " " + line.strip()
                    
                if line.strip().upper() == "END" :
                    #
                    # With jal2.4 the last ;sal comment in asm file *may* not correspond to an asm instruction...
                    # example : 
                    #;   30 end loop
                    #           end
                    # so when we reach "end", we should look if previous line starts with ";" if it does,
                    # set decrease adress for prevLine
                    if (prevLine.strip().startswith(";")) :
                        #Need correction
                        
                        tmp = list[-1]
                        self.adrToLine[tmp.address-1] = self.adrToLine[tmp.address];
                       
                        tmp.address -=1 
                        list[-1] = tmp
                        self.lineToAdr[lineIndex-1] = self.lineToAdr[lineIndex-1]-1
                        #print " lineToAdr[lineIndex-1] %06X " % ( lineIndex - 1 ) + " set to %d " % ( self.lineToAdr[lineIndex-1]-1 )
                         
                        
                    break
                # var mapping part
                if ( "list p=18" in line ):
                   pic18f = True

                   p0 = line.find( "list p=" )                   
                   if ( p0 >= 0 ):
                       self.picName = line[p0+7:]

                       p0 = self.picName.find( "," )
                       if ( p0 >= 0 ):
                           self.picName = self.picName[:p0]


                if ( ( "list p=18" in line ) or ( "list p=16" in line ) or ( "list p=14" in line ) or ( "list p=12" in line ) or ( "list p=10" in line )):                
                   p0 = line.find( "list p=" )                   
                   if ( p0 >= 0 ):
                       self.picName = line[p0+7:]

                       p0 = self.picName.find( "," )
                       if ( p0 >= 0 ):
                           self.picName = self.picName[:p0]

                   
                if ("EQU" in line):
                    tmp = line.strip()
                    parts = re.split(r'\W+',tmp)
                    if (parts[2].startswith("0x")):
                        dec = int(parts[2],16)
                        # one addr can used by many var
                        if self.adrVarMapping.has_key(dec):
                            self.adrVarMapping[dec] = self.adrVarMapping[dec]+", "+parts[0]
                        else:
                            self.adrVarMapping[dec] = parts[0]
                        #one var belong in one adr (or at least starts at one address...)
                        self.varAdrMapping[parts[0]] = dec
                        
                # end var mapping
                
                   
                if (line.startswith(";")):
                    try :
                        
                        int(line[1:6].strip()); # to raise an execption for line that didn't start with an adress
                        # JAL code
                        if (self.mode == JalV2AsmParser.JAL):
                            line = line.strip()
                            st = DebugStruct()
                            st.address = adresse
                            st.line = line[7:]
                            
                            #print str(st.address)+" "+ st.line
                            
                            if st.line.upper().startswith("PROCEDURE ") or st.line.upper().startswith("FUNCTION "):
                                meth = re.split(r"\W+", st.line)[1]
                            if st.line.upper().startswith("END PROCEDURE") or st.line.upper().startswith("END FUNCTION"):
                                self.addressMethodMapping[st.address] = meth 
                                meth = ""
                            if meth != "":
                               self.addressMethodMapping[st.address] = meth   
                            
                            
                            if (file != ""): # show file that contains the code
                                
                                libFile = os.path.basename(file).replace(".jal","")
                                st2 = DebugStruct()
                                st2.address = " "
                                st2.line = "-- "+file[2:]
                                
                                if ((libFile != None) and (libFile.upper() in noDebugList)) or (
                                    ("*" in noDebugList) 
                                    and libFile != os.path.basename(filename).replace(".asm","") 
                                    and "~"+libFile != os.path.basename(filename).replace(".asm","") 
                                    and libFile.upper() not in debugList):
                                        st2.line+=" [ignored]"
                                
                                list.append(st2)
                                #print str(lineIndex) +" 1> "+line

                                file =""
                                lineIndex += 1
                                
                            if ((libFile != None) and (libFile.upper() not in noDebugList)) :
                                if (
                                    ("*" not in noDebugList) 
                                    or libFile == os.path.basename(filename).replace(".asm","")
                                    or "~"+libFile == os.path.basename(filename).replace(".asm","")
                                    or libFile.upper() in debugList):
                                    
                                    if (not line[7:].startswith("include")):
                                        list.append(st)
                                        #print str(lineIndex) +" 2> "+line,
                                        self.lineToAdr[lineIndex] = adresse # used to place breakpoint for a line
                                        # print " self.lineToAdr[%d] " % lineIndex + " = %06X"  % adresse # used to place breakpoint for a line
                                        
                                        
                                        if self.adrToLine[adresse] == None:
                                            self.adrToLine[adresse] = lineIndex # used to find the line to highligh when debuging
                                        lineIndex += 1
                       
                    except :
                        #print "e:"+line,
                        file = line.strip() # file module
                        if ("command line:" in file):
                            file =""
                        
                # ASM code
                # with the -d option of jalv2, some line starting with space
                # may juste content comment and not asm code...
                parts = line.split(";")
                if (parts[0].startswith(" ")) and parts[0].strip()!="":
                    if (orgFound):
                        if (self.mode == JalV2AsmParser.ASM):
                            line = line.rstrip()
                            st = DebugStruct()
                            st.address = adresse
                            st.line = line[7:]
                            list.append(st)
                            
                            self.lineToAdr[lineIndex] = adresse # used to place breakpoint for a line
                            # print " self.lineToAdr[%d] " % lineIndex + " = %06X"  % adresse # used to place breakpoint for a line
                            self.adrToLine[adresse] = lineIndex # used to find the line to highligh when debuging
                            
                            lineIndex = lineIndex + 1
                        
                        # TODO : macro can contains more then one line...
                        if not (line.strip().startswith("org ")): # org is a directive...
                             if not ( "   db   " in line ) :
                                if ( pic18f ):
                                   # AF FIXME TODO complete 2 word instructions (Extended instr set)
                                   if ( "goto " in line ) :
                                      adresse = adresse + 1
                                   if ( "call " in line ) :
                                      adresse = adresse + 1
                                   if ( "movff " in line ) :
                                      adresse = adresse + 1
                                   if ( "lfsr " in line ) :
                                      adresse = adresse + 1
                                adresse = adresse + 1
                             else:   
                                  # count number of 0X
                                  nullXcount = line.count( "0x" )
                                  adresse = adresse + nullXcount / 2
                                  # print "DB %d" % nullXcount + " new addr %04x"%adresse
                        else :
                            if pic18f:
                               adresse = int(line.strip("org "))/2
                            else:
                               adresse = int(line.strip("org "))
                            
                           
                    else:
                        if (line.strip().startswith("org ")):
                            orgFound = True
                
                #if adresse < 0x200:
                #   print "JAL: %d "%adresse + line
                prevLine = line;
                
        except IOError, e:               
            print "Error in file IO: ", e 
        if fin: fin.close()              
        return list;
    @staticmethod
    def BuildVarTypeDict(lines, jalFileName):
        array = {}
        arrayCpt = {}
         
        incfiles = list()
        incfiles.append( jalFileName )
        
        # get all include files (once) from asm file			
        for st in lines:
            # st is a DebugStruct
            lg = st.line
            #print lg
            if lg.upper().strip().find(".JAL") > 0 :
               filename = lg[ 3:]
               incfiles.append( filename )
      
        # loop through all JAL files
        for incfile in incfiles:
            try:
	            # print incfile     
	            fin = open(incfile,"r")   
	   
	            for lg in fin:
	                if lg.upper().strip().startswith("VAR "):
	                    parts = re.split(r'\s+',lg.strip())
	                      
	                    type = parts[1]
	                    name = parts[2]
	                     
	                    if type.upper() == "VOLATILE":
	                        type = parts[2]
	                        name = parts[3]
	                    if arrayCpt.has_key(name):
	                        arrayCpt[name] += 1
	                        name = "__"+name+"_%d" % arrayCpt[name]
	                    else:
	                        arrayCpt[name] = 1
	                              
	                    name = name.lower()    
	                    array[name] = type
	            if fin: 
	            	fin.close()              
            except :
            	# print "could not open file: " + incfile
            	incfile = incfile
        return array