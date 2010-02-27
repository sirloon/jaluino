import sys
import os

class Context:
    app = None
    frame = None 
    uiManager = None
    MAX_RECENT_FILE = 9
    FONTSIZE = 10
    TABSIZE = 4
    USETABS = 0
    APP_SIZE_X = 0
    APP_SIZE_Y = 0
    APP_POS_X = 0
    APP_POS_Y = 0
    
    BROWSER_SASH_POSITION=0
    
    
    TOOL_RUN = 801
    TOOL_COMPILE = 806
    TOOL_STOP = 802
    TOOL_SHOW_OUTLINE = 808
   
    TOOL_NEW = 810
    TOOL_SAVE = 811
    TOOL_OPEN = 812
    TOOL_PROGRAM= 813
    TOOL_RUN_UNIT_TEST = 814
    
    
    # main app tabs
    TAB_DEBUG = 0
    TAB_EDIT = 1
    TAB_BROWSER = 2
    TAB_TERMINAL = 3
    
    #compile tab
    COMPILE_ERROR_TAB = 0
    COMPILE_RESULT_TAB = 1
    
    #debugger list columns
    COL_ADR = 0
    COL_RUN = 1
    COL_BP = 2
    COL_CODE = 3
    COL_COM = 4
    
    #shared static config
    sourcepath=""
    devicesPath=""

    libpath="C:\PICjal\JAL\Libraries"
    compiler="C:\PICjal\JAL\Compiler\jalv2.exe"
    # -Wno-all -long-start -d -clear
    compilerOptions =""
    
    libpath2=""
    compiler2=""
    compiler2Options=""
    
    programmer =""
    programmerOptions =""
    
    top = None
    
    lastOpenedFiles = []
    
    completeStructure = "true"
    
    #configView = None
    
    #
    # Need a better parser here, but work for now... ;-)
    #
    @staticmethod
    def load(configFilename="config.txt"):
        Context.lastOpenedFiles = []
        if os.path.exists(configFilename):
            file = open(configFilename)
            lines = file.readlines()
            for line in lines :
                line = line.strip()
                parts = line.split("=")
                if (parts[0].upper() == "COMPILER") :
                    Context.compiler = parts[1]
                elif (parts[0].upper() == "COMPILER_OPTIONS") :
                    Context.compilerOptions = parts[1]
                elif (parts[0].upper() == "LIBPATH") :
                    Context.libpath = parts[1]
                elif (parts[0].upper() == "DEFAULT_OPEN_DIR") :
                    Context.sourcepath = parts[1]  
                   
                elif (parts[0].upper() == "DEVICES_PATH") :
                    Context.devicesPath = parts[1]  
                elif (parts[0].upper() == "COMPILER2") :
                    Context.compiler2 = parts[1]
                elif (parts[0].upper() == "COMPILER2_OPTIONS") :
                    Context.compiler2Options = parts[1] 
                elif (parts[0].upper() == "LIBPATH2") :
                    Context.libpath2 = parts[1]
                elif (parts[0].upper() == "PROGRAMMER") :
                    Context.programmer = parts[1]
                elif (parts[0].upper() == "PROGRAMMER_OPTIONS") :
                    Context.programmerOptions = parts[1]
                elif (parts[0].upper() == "OPENED_FILE") :
                    Context.lastOpenedFiles.append(parts[1])
                elif (parts[0].upper() == "MAX_RECENT_FILES") :
                    Context.MAX_RECENT_FILE = int (parts[1])
                elif (parts[0].upper() == "COMPLETE_STRUCTURE") :
                    Context.completeStructure=parts[1]
                elif (parts[0].upper() == "FONTSIZE") :
                    Context.FONTSIZE = int (parts[1])
                elif (parts[0].upper() == "TABSIZE") :
                    Context.TABSIZE = int (parts[1])
                elif (parts[0].upper() == "USETABS") :
                    Context.USETABS = int (parts[1])
                elif (parts[0].upper() == "APP_SIZE_X") :
                    Context.APP_SIZE_X = int (parts[1])
                elif (parts[0].upper() == "APP_SIZE_Y") :
                    Context.APP_SIZE_Y = int (parts[1])
                elif (parts[0].upper() == "APP_POS_X") :
                    Context.APP_POS_X = int (parts[1])
                elif (parts[0].upper() == "APP_POS_Y") :
                    Context.APP_POS_Y = int (parts[1])                    
                elif (parts[0].upper() == "BROWSER_SASH_POSITION") :
                    Context.BROWSER_SASH_POSITION = int (parts[1])                    
                    
            
            file.close() 
            try :
                sys.path.remove(Context.devicesPath)
            except : pass
            sys.path.append(Context.devicesPath)
           
    @staticmethod
    def stackOpenedFile(filename):
        last = Context.lastOpenedFiles
        if filename in last:
            last.remove(filename)
        last.insert(0,filename)
        last = last[:Context.MAX_RECENT_FILE]
        Context.save()

    
    @staticmethod
    def save(configFilename="config.txt"):
        f=open(configFilename, 'w')
        f.write("compiler="+Context.compiler+"\n")
        f.write("libpath="+Context.libpath+"\n")
        f.write("compiler_options="+Context.compilerOptions+"\n")
        f.write("default_open_dir="+Context.sourcepath+"\n")
        f.write("devices_path="+Context.devicesPath+"\n")
        f.write("compiler2="+Context.compiler2+"\n")
        f.write("libpath2="+Context.libpath2+"\n")
        f.write("compiler2_options="+Context.compiler2Options+"\n")
        f.write("programmer="+Context.programmer+"\n")
        f.write("programmer_options="+Context.programmerOptions+"\n")
        f.write("COMPLETE_STRUCTURE="+Context.completeStructure+"\n")
        f.write("FONTSIZE="+str(Context.FONTSIZE)+"\n")
        f.write("TABSIZE="+str(Context.TABSIZE)+"\n")
        f.write("USETABS="+str(Context.USETABS)+"\n")
        f.write("APP_SIZE_X="+str(Context.APP_SIZE_X)+"\n")
        f.write("APP_SIZE_Y="+str(Context.APP_SIZE_Y)+"\n")
        f.write("APP_POS_X="+str(Context.APP_POS_X)+"\n")
        f.write("APP_POS_Y="+str(Context.APP_POS_Y)+"\n")
        f.write("BROWSER_SASH_POSITION="+str(Context.BROWSER_SASH_POSITION)+"\n")

        for file in Context.lastOpenedFiles[:Context.MAX_RECENT_FILE]:
            f.write("OPENED_FILE="+file+"\n");
        f.close()
        try :
            sys.path.remove(Context.devicesPath)
        except : pass
        sys.path.append(Context.devicesPath)
        
       
        
        
        
        
                
