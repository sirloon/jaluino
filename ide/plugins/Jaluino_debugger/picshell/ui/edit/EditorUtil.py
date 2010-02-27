import os
import re
from picshell.util.FileUtil import FileUtil
#
# Utility class for Jal editor
#
class EditorUtil:
    
    #pathes must be separted with ;
    @staticmethod
    def findInFile(filename,pathes,what,num) :
        res = set()
        allpathes = pathes.split(";")
        for path in allpathes:
            
            if os.path.exists(path+os.sep+filename):
                file = open(path+os.sep+filename)
                for lg in file:
                    if what in lg:
                        if (not lg.strip().startswith(";")) and (not  lg.strip().startswith("--")):
                            res.add(EditorUtil.extractName(lg,num))
                            
                file.close()
                break # lib as been found
            
        
        return res
    
    #pathes must be separted with ;
    @staticmethod
    def findInFileStartswith(filename,pathes,what,num) :
        res = set()
        allpathes = pathes.split(";")
        for path in allpathes:
            if os.path.exists(path+os.sep+filename):
                file = open(path+os.sep+filename)
                for lg in file:
                    if lg.startswith(what):
                        res.add(EditorUtil.extractName(lg,num))
                file.close()
                break # lib as been found
            
        
        return res
    
    @staticmethod
    def findInFileNoPath(filename,what,num) :
        res = set()
        if os.path.exists(filename):
            file = open(filename)
            for lg in file:
                if what.upper() in lg.upper():
                    if (not lg.strip().startswith(";")) and (not  lg.strip().startswith("--")):
                        res.add(EditorUtil.extractName(lg,num))
            file.close()
        return res
    
    @staticmethod
    def findInString(str,what, num) :
        res = set()
        tab = str.split("\n");
        for lg in tab:
            lg = lg.strip()
            if what.upper() in str.upper():
                if (not lg.startswith(";")) and (not  lg.startswith("--")):
                    res.add(EditorUtil.extractName(lg,num))
       
        return res
    
    
    @staticmethod
    def findInStringStartswith(str,what, num) :
        res = set()
        tab = str.split("\n");
        for lg in tab:
            lg = lg.strip()
            if lg.upper().startswith(what.upper()):
                res.add(EditorUtil.extractName(lg,num))
       
        return res
    
    @staticmethod
    def extractName(lg,num):
        lg = lg.strip()
        l = re.split(r'\W+',lg)
        if num < len(l):
            return l[num].strip()
        else:
            return ""
    
    @staticmethod
    def findAllLibs(libpathes):
        res = []
        libpathes = FileUtil.expand_paths( libpathes )         
        allPathes = libpathes.split(";")
        try :
            for libpath in allPathes:
                fnames = os.listdir(libpath)
                for name in fnames:
                    if name.endswith(".jal"):
                        name = name.replace(".jal","")
                        res.append(name)
        except : pass
        return res
    
    @staticmethod
    def findAllLibsWithPath(libpathes):
        res = []
        libpathes = FileUtil.expand_paths( libpathes )         
        allPathes = libpathes.split(";")
        try :
            for libpath in allPathes:
                fnames = os.listdir(libpath)
                for name in fnames:
                    if name.endswith(".jal"):
                        
                        res.append(libpath+os.sep+name)
        except : pass
        return res
    
    @staticmethod
    def findAllIncludes(text,libpath):
        found = set()
        libpath = FileUtil.expand_paths( libpath )         
        includes = EditorUtil.findInStringStartswith(text,"include", 1)
        for inc in includes:
            if (inc not in found):
                found.add(inc)
                text =""
                for path in libpath.split(";"):
                    if os.path.exists(path+os.sep+inc+".jal"):
                        file = open (path+os.sep+inc+".jal")
                        for lg in file:
                            text += lg
                        file.close()
                        found = found.union(EditorUtil.findAllIncludes(text,libpath))
                        break
                
        return found
    
    @staticmethod
    def findAllIncludesWithPath(text,libpath,path=""):
        found = set()
        libpath = FileUtil.expand_paths( libpath )         
        includes = EditorUtil.findInStringStartswith(text,"include", 1)
        for inc in includes:
            text =""
            for path in libpath.split(";"):
                if os.path.exists(path+os.sep+inc+".jal"):
                    if (inc not in found):
                        found.add(path+os.sep+inc+".jal")
                    
                    file = open (path+os.sep+inc+".jal")
                    for lg in file:
                        text += lg
                    file.close()
                    found = found.union(EditorUtil.findAllIncludesWithPath(text,libpath,path))
                    break
        return found
    
    @staticmethod
    def searchInAllIncludes(what,text,libpath):
        found = set()
        resFile = None
        resLine = None
        libpath = FileUtil.expand_paths( libpath )         
        includes = EditorUtil.findInStringStartswith(text,"include", 1)
        for inc in includes:
            if (inc not in found):
                found.add(inc)
                text =""
                for path in libpath.split(";"):
                    if os.path.exists(path+os.sep+inc+".jal"):
                        
                        file = open (path+os.sep+inc+".jal")
                        line = 0
                        for lg in file:
                            text += lg
                            tmp = lg.strip()
                            
                            met = tmp.split(";")[0]
                            met = tmp.split("--")[0]
                            met = tmp.strip()
                            
                            if (EditorUtil.isMethodDeclaration(met,what) ):
                                resFile= path+os.sep+inc+".jal"
                                resLine = line
                            
                                return [set(),resFile,resLine]
                                
                            line +=1
                        file.close()
                        
                        res = EditorUtil.searchInAllIncludes(what,text,libpath)
                        resFile = res[1]
                        resLine = res[2]
                        found = found.union(res[0])
                        break
                
        return [found,resFile,resLine]
    
    @staticmethod
    def isMethodDeclaration(tmp,what):
        what = what.strip()
        return tmp.upper().startswith("FUNCTION "+what.upper()+" ") or\
             tmp.upper().startswith("PROCEDURE "+what.upper()+" ") or\
             tmp.upper().startswith("FUNCTION "+what.upper()+"(") or\
             tmp.upper().startswith("PROCEDURE "+what.upper()+"(") or\
             tmp.upper().startswith("FUNCTION "+what.upper()+"'") or\
             tmp.upper().startswith("PROCEDURE "+what.upper()+"'") or\
             tmp.upper() == "FUNCTION "+what.upper() or\
             tmp.upper() == "PROCEDURE "+what.upper()
             
       
    
    @staticmethod
    def searchCommentInAllIncludes(what,text,libpath):
        found = set()
        libpath = FileUtil.expand_paths( libpath )         
        includes = EditorUtil.findInStringStartswith(text,"include", 1)
        comment = ""
        for inc in includes:
            if (inc not in found):
                found.add(inc)
                text =""
                for path in libpath.split(";"):
                    if os.path.exists(path+os.sep+inc+".jal"):
                        file = open (path+os.sep+inc+".jal")
                        line = 0
                        comment = ""
                        full = file.readlines()
                        for lg in full:
                            text += lg
                            tmp = lg.strip()
                            
                            met = tmp.split(";")[0]
                            met = tmp.split("--")[0]
                            met = tmp.strip()
                            
                            if EditorUtil.isMethodDeclaration(met,what) or \
                                 ((what.upper() in met.upper()) and  met.upper().startswith("VAR ")) :
                                
                                resFile= path+os.sep+inc+".jal"
                                resLine = line
                                try :
                                    cpt = 0
                                    if not met.upper().startswith("VAR ") :
                                        while not met.upper().endswith("IS"):
                                            cpt += 1
                                            met += full[line+cpt].strip()
                                            if cpt == 20:
                                                break
                                except : pass
                                
                                return [set(),path+os.sep+inc+".jal"+"\n"+met+"\n"+comment]
                            
                            elif tmp.startswith("--") or tmp.startswith(";"):
                                comment += tmp+"\n"
                               
                            elif tmp != "":
                                comment =""
                                
                            line +=1
                        file.close()
                        res = EditorUtil.searchCommentInAllIncludes(what,text,libpath)
                        found = found.union(res[0])
                        comment = res[1]
                        break
                
        return [found,comment]
    
    
    @staticmethod
    def findAllIncludedFiles(text,pathes):
        found = set()
        pathes = FileUtil.expand_paths( pathes )         
        includes = EditorUtil.findInStringStartswith(text,"include", 1)
        for inc in includes:
            if (inc not in found):
                text =""
                for path in pathes.split(";"):
                    if os.path.exists(path+os.sep+inc+".jal"):
                        found.add(path+os.sep+inc+".jal")
                        file = open (path+os.sep+inc+".jal")
                        for lg in file:
                            text += lg
                        file.close()
                        found = found.union(EditorUtil.findAllIncludedFiles(text,pathes))
                        break
        return found
    
    @staticmethod
    def findLineForVar(str,var,inMethod=""):
        line = 0;
        tab = str.split("\n");
        var_name =  re.split(r'\s+',var,2)[1]
        methodFound = False
        for lg in tab:
            lg = lg.strip()
            if lg.upper().startswith("PROCEDURE "+inMethod.upper()) \
                or lg.upper().startswith("FUNCTION "+inMethod.upper()): 
                methodFound = True
            
            if lg.upper().startswith("VAR") and EditorUtil.testWithSep(var_name,lg):
                if inMethod=="" or methodFound:
                    return line
            line += 1
        return -1

    @staticmethod
    def findLineForFunc(str,func):
        line = 0;
        tab = str.split("\n");
        for lg in tab:
            lg = lg.strip()
            if lg.upper().startswith("FUNCTION") and EditorUtil.testWithSep(func,lg):
                return line
            line += 1
        return -1
    
    @staticmethod
    def findLineForAnnotation(str,func):
        line = 0;
        tab = str.split("\n");
        for lg in tab:
            lg = lg.strip()
            if lg.strip() == func.strip():
                return line
            line += 1
        return -1
    
    @staticmethod
    def findLineForMethod(str,method):
        line = 0;
        tab = str.split("\n");
        for lg in tab:
            lg = lg.strip()
            if (lg.upper().startswith("FUNCTION") or lg.upper().startswith("PROCEDURE")) and EditorUtil.testWithSep(method,lg):
                return line
            line += 1
        return -1
    @staticmethod
    def findLineForProc(str,proc):
        line = 0;
        tab = str.split("\n");
        for lg in tab:
            lg = lg.strip()
            if lg.upper().startswith("PROCEDURE") and EditorUtil.testWithSep(proc,lg):
                return line
            line += 1
        return -1
    @staticmethod
    def findLineForForever(str):
        line = 0;
        tab = str.split("\n");
        for lg in tab:
            lg = lg.strip()
            if lg.upper().startswith("FOREVER") :
                return line
            line += 1
        return -1
    
    @staticmethod
    def testWithSep(str,lg):    
        if re.search(r'[\s+,]' + str + r'([\s\(\[\',]|$)',lg,re.I):
            return True
        else:
            return False
    
    @staticmethod
    def findInFileStartswithNoPath(filename,what,num) :
        res = set()
        lineMapping = {}
        if os.path.exists(filename):
            file = open(filename)
            curLine = 0;
            for lg in file:
                if lg.startswith(what):
                    func = EditorUtil.extractName(lg,num)
                    res.add(func)
                    lineMapping[func] = curLine
                curLine += 1
            file.close()
        resList = list(res)
        resList.sort()
        return (resList,lineMapping) 
    
    @staticmethod
    def findMethod(text,methodName):
        line = 0
        found = False
        for lg in text.split("\n") :
            if lg.strip().upper().startswith("PROCEDURE "+methodName.upper()) or \
                lg.strip().upper().startswith("FUNCTION "+methodName.upper()):
                found = True
                break
            
            line += 1

        if found :
            return line
        else:
            return None
       
       
    @staticmethod
    def findMethodComment(text,methodName):
        
        line = 0
        found = False
        comment =""
        full = text.split("\n")
        
        for lg in full :
            slg = lg.strip()
           
            if slg.upper().startswith("PROCEDURE "+methodName.upper()) or \
                slg.upper().startswith("FUNCTION "+methodName.upper()) or \
                slg.upper().startswith("VAR VOLATILE "+methodName.upper()):
              
                if not slg.upper().startswith("VAR "):
                    cpt = 0
                    while not slg.upper().endswith(" IS"):
                        slg += full[line+1]
                        cpt += 1
                        if cpt == 20:
                            break
                    
                found = True
                comment = slg+"\n"+comment
                break
            elif slg.startswith("--") or slg.startswith(";"):
                comment += slg+"\n"
            elif slg != "" :
                comment =""
            line += 1
        if found :
            return comment
        else:
            return None
    

