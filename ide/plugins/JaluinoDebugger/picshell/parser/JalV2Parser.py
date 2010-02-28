import re
class Var:
    def __init__(self,name,type):
        self.name=name
        self.type=type

class JalV2Parser:
    #
    # Check if code is a method call (ie test() or call(89) ...)
    #
    @staticmethod
    def mustStepOver(code):
        
        lines = code.split("/");
        for code in lines :
            code = code.upper()
            code = code.strip()
            if (not code.startswith("PROCEDURE ") and 
                not code.startswith("FUNCTION ") and
                not  code.startswith("END ") and
                not  code.startswith("IF ") and
                not  code.startswith("ELSIF ") and
                not  code.startswith("END ") and
                
                "(" in code and ")" in code) : 
                return True
        
        return False
        
    
    #
    # Parse a jal file and return a tuple (func,proc,var)
    # lines : content of the jal file as an array of lines
    @staticmethod
    def parse(lines):
        funcs = {} # key is func name, value is an array of Var
        procs = {} # key is proc name, value is an array of Var
        globalVars = [] # array oy Var
        curVars = [] # array oy Var
        
        
        currentMethod = None
        for line in lines:
            line = line.strip()
            orig = line
            line = line.upper()
            if (line.startswith("VAR")):
                names = JalV2Parser.extractVarNames(orig)
                type = JalV2Parser.extractVarType(orig)
                for name in names:
                    var = Var(name,type)
                    if currentMethod == None:
                        globalVars.append(var)
                    else:
                        curVars.append(var)
            elif (line.startswith("FUNCTION")):
                currentMethod = JalV2Parser.extractMethodeName(orig)
               
            elif (line.startswith("PROCEDURE")):
                currentMethod = JalV2Parser.extractMethodeName(orig)
               
            elif (line.startswith("END FUNCTION")):
                funcs[currentMethod] = curVars
                currentMethod = None
                curVars =[]
            elif (line.startswith("END PROCEDURE")):
                procs[currentMethod] = curVars
                currentMethod = None
                curVars =[]
        return(funcs,procs,globalVars)
     
    @staticmethod
    def extractMethodeName(line):
        parts = re.split(r'\W+',line)
        return parts[1]
    @staticmethod
    def extractVarNames(line):
        line = line.replace(" volatile "," ")
        [var, type, varNames] = re.split(r'\s+',line,2)
        varNames = re.split(r'\s*,\s*',varNames)
        return varNames
    @staticmethod
    def extractVarType(line):
        line = line.replace(" volatile "," ")
        parts = re.split(r'\s+',line)
        return parts[1]
    
    
    @staticmethod
    def findLocalVar(textToCurs):  
        localv = []
        scoopCodeText = JalV2Parser.findMethodTextToCursor(textToCurs)
        for lg in scoopCodeText.split("\n"):
                    lg = lg.strip()
                    if lg.upper().startswith("VAR "):
                        parts = re.split(r"\s+",lg)
                        localv.append(parts[2])
        return localv
    
    @staticmethod
    def findConst(textToCurs):  
        const = []
        for lg in textToCurs.split("\n"):
                    lg = lg.strip()
                    if lg.upper().startswith("CONST "):
                        parts = re.split(r"\s+",lg)
                        const.append(parts[1])
        return const
    
    #
    # used to find visible variables at some scope
    #
    @staticmethod    
    def findMethodTextToCursor(text):
        lines = text.split("\n")
        l = len(lines)-1
        text = "";
        thresold = 0;
        level = 0
        hasElse = False;
        for i in range(l,-1,-1):
            lg = lines[i].strip().upper()
            
            if lg.startswith("END PROCEDURE") or lg.startswith("END FUNCTION"): 
                return "" # global scoop
            elif ("END " in lg) :
                level +=1 
            elif lg==("ELSE") or lg.startswith("ELSE ") :
                hasElse = True
                level +=1 
            elif lg.startswith("IF ") :
                level -=1 
                if hasElse:
                    level -=1 
                    hasElse = False
            elif lg.startswith("BLOCK ") or ("WHILE " in lg) or lg.startswith("FOR ") or lg.startswith("FOREACH ") :
                level -=1 
                
            if lg.startswith("PROCEDURE ") or lg.startswith("FUNCTION "):
                return text
            if thresold>=level:
                thresold = level
                text =lines[i].strip()+"\n"+text
        return text
    
    
    
