from picshell.ui.debug.comp.Dual7Seg import Dual7Seg
from picshell.ui.debug.comp.Counter import UpDownCounter
from picshell.ui.debug.comp.uart import MidiSender
from picshell.ui.debug.comp.uart import UARTReceiver
from picshell.ui.debug.comp.uart import ASCIIReceiver
from picshell.ui.debug.comp.uart import ASCIISender
from picshell.ui.debug.comp.uart import ByteSender
from picshell.ui.debug.comp.LED import LED
from picshell.ui.debug.comp.StaticText import StaticText
from picshell.engine.util.Format import Format
from picshell.ui.debug.comp.CLED import CLED
from picshell.ui.debug.comp.Watch import Watch
from picshell.ui.debug.comp.LCD import LCD
from picshell.ui.debug.comp.Potmeter import Potmeter
from picshell.ui.debug.comp.PermanentSwitch import PermanentSwitch
from picshell.ui.debug.comp.MomentarySwitch import MomentarySwitch

import re

        
class AnnotationParser:
    
   
    @staticmethod
    def findAnnotations(content):
        an = [];
        for lg in content.split("\n"):
            lg2 = re.sub(';\s*@', '--@', lg)
            if "--@" in lg2:
                an.append(lg.strip());
        return an
                
        
    @staticmethod
    def parse(content):
        noDebug = []
        debug=[]
        inputs = []
        outputs =[]
        devices = []
        varfilter =""
        regfilter =""
        options=[]
        
        for lg in content.split("\n"):
            lg = re.sub(';\s*@', '--@', lg)
            if "--@" in lg:
                lg = lg.strip()
                parts = lg.split("--@")
                start = parts[0]
                cmd = parts[1]
                parts = cmd.split(" ")
                if parts[0] == "use_virtual_delay":
                    options.append("virtual_delay") 
                    
                elif parts[0] == "no_debug":
                    noDebug.append(lg.split(" ")[1].upper()) # add to debug ignore list
                elif parts[0] == "debug":
                    debug.append(lg.split(" ")[1].upper()) # add to debug ignore list
                elif parts[0] == "no_debug_all":
                    noDebug.append("*");
                elif parts[0] == "var_filter":
                    varfilter=cmd.replace("var_filter ","")
                elif parts[0] == "reg_filter":
                    regfilter=cmd.replace("reg_filter ","")
                elif parts[0] == "mpu":
                    cmdParts = cmd.split(" ")
                    pin =""
                    if "pin_" in start:
                        start = start.strip()
                        startParts = start.split(" ");
                        pin = startParts[len(startParts)-1]
                        name = cmdParts[1]
                        type =cmdParts[0]

                    elif "mpu" == cmdParts[0]:
                        pin = cmdParts[2]
                        name = cmdParts[1] 
                        type =cmdParts[0]

                    
                    if (pin != "") :
                        bInfo = MomentarySwitch(name,pin,type)
                        inputs.append(bInfo)
                                
                elif parts[0] == "mpd":
                    cmdParts = cmd.split(" ")
                    pin =""
                    if "pin_" in start:
                        start = start.strip()
                        startParts = start.split(" ");
                        pin = startParts[len(startParts)-1]
                        name = cmdParts[1]
                        type =cmdParts[0]
                    
                    elif "mpd" == cmdParts[0]:
                        pin = cmdParts[2]
                        name = cmdParts[1] 
                        type =cmdParts[0]
                    
                    if (pin != "") :
                        bInfo = MomentarySwitch(name,pin,type)
                        inputs.append(bInfo)                
                            
                elif parts[0] == "ppu":
                    cmdParts = cmd.split(" ")
                    pin =""
                    if "pin_" in start:
                        start = start.strip()
                        startParts = start.split(" ");
                        pin = startParts[len(startParts)-1]
                        name = cmdParts[1]
                        type =cmdParts[0]
                    
                    elif "ppu" == cmdParts[0]:
                        pin = cmdParts[2]
                        name = cmdParts[1] 
                        type =cmdParts[0]
                    
                    if (pin != "") :
                        bInfo = PermanentSwitch(name,pin,type)
                        inputs.append(bInfo)
                
                elif parts[0] == "ppd":
                    cmdParts = cmd.split(" ")
                    pin =""
                    if "pin_" in start:
                        start = start.strip()
                        startParts = start.split(" ");
                        pin = startParts[len(startParts)-1]
                        name = cmdParts[1]
                        type =cmdParts[0]
                    
                    elif "ppd" == cmdParts[0]:
                        pin = cmdParts[2]
                        name = cmdParts[1] 
                        type =cmdParts[0]
                    
                    if (pin != "") :
                        bInfo = PermanentSwitch(name,pin,type)
                        inputs.append(bInfo)
                        
                elif parts[0] == "pot":
                    cmdParts = cmd.split(" ")
                    pin =""
                    if "pin_" in start:
                        start = start.strip()
                        startParts = start.split(" ");
                        pin = startParts[len(startParts)-1]
                        name = cmdParts[0]
                    
                    elif "pot" == cmdParts[0]:
                        name = cmdParts[1]
                        pin = cmdParts[2]
                         
                    if (pin != "") :
                        bInfo = Potmeter( name, pin )
                        inputs.append(bInfo)
                        
                
                           
                elif parts[0] == "watch_bin":
                    cmdParts = cmd.split(" ")
                    name=""
                    if len(cmdParts) == 3:
                        name = cmdParts[2]
                    adr = cmdParts[1]
                    watch = Watch( adr,"bin", name, None)
                    
                    outputs.append(watch)
                elif parts[0] == "watch_hex":
                    cmdParts = cmd.split(" ")
                    name=""
                    if len(cmdParts) == 3:
                        name = cmdParts[2]
                    adr = cmdParts[1]
                    watch = Watch( adr,"hex", name, None)
                    outputs.append(watch)
                elif parts[0] == "watch":
                    cmdParts = cmd.split(" ")
                    name=""
                    if len(cmdParts) == 3:
                        name = cmdParts[2]
                    adr = cmdParts[1]
                    watch = Watch( adr,"dec", name, None)
                    outputs.append(watch)
                elif parts[0] == "lcd4bit":
                    cmdParts = cmd.split(" ")
                    name=""
                    par = cmdParts[1].split(",")
                    adr = par[0]
                    nbChar=16;
                    if len(par) == 2 :
                        nbChar = int(par[1])
                    watch = LCD(name,adr,nbChar )
                    outputs.append(watch)
                elif parts[0] == "labelOut":
                    cmdParts = cmd.split(" ")
                    text =""
                    if len(cmdParts) > 1 :
                        for t in cmdParts[1:]:
                            text += t+" "
                    label = StaticText("labelOut", text)
                    outputs.append(label)
                elif parts[0] == "labelIn":
                    cmdParts = cmd.split(" ")
                    text =""
                    if len(cmdParts) > 1 :
                        for t in cmdParts[1:]:
                            text += t+" "
                    label = StaticText("labelIn", text )
                    inputs.append(label)
                    
                elif parts[0] == "dual7seg":
                    cmdParts = cmd.split(" ")
                    args = cmdParts[1].split(",")
                    name =""
                    if len(cmdParts) == 3:
                        name = cmdParts[2]
                    seg = Dual7Seg(None,args[0],int(args[1]),int(args[2]),int(args[3]),name)
                    outputs.append(seg)
                    
                elif parts[0] == "led" or parts[0].startswith("led_"):
                    ok = True
                    cmdParts = cmd.split(" ")
                    name=""
                    if len(cmdParts) == 3:
                        name = cmdParts[2]
                    adr = cmdParts[1]
                    # adr:bit
                    # pin_xy
                    if ":" in adr :
                        p = adr.split(":")
                        adr = p[0]
                        bit = int(p[1])
                        bit = pow(2,bit)
                        
                    elif "_" in adr :
                        adr = adr.upper()
                        port = ord(adr[4])-60 
                        bit = pow(2,(ord(adr[5])-48))
                        adr = "PORT" + adr[4]
                       
                    else :
                        print "Invalide syntax in line :"+lg
                        ok = False
                    if ok :
                        if parts[0] == "led" :    
                            led = LED(None,adr,bit,name)
                        elif parts[0] == "led_red" :
                            led = CLED(None,None,None,adr,bit,name,"red")
                        elif parts[0] == "led_blue" :
                            led = CLED(None,None,None,adr,bit,name,"blue")
                        elif parts[0] == "led_green" :
                            led = CLED(None,None,None,adr,bit,name,"green")
                        elif parts[0] == "led_orange" :
                            led = CLED(None,None,None,adr,bit,name,"orange")
                        elif parts[0] == "led_yellow" :
                            led = CLED(None,None,None,adr,bit,name,"yellow")

                        outputs.append(led)
                elif parts[0] == "upDownCounter":
                    cmdParts = cmd.split(" ")
                    args = cmdParts[1].split(",")
                    name =""
                    csBar=False
                    if len(cmdParts) >= 3:
                        name = cmdParts[2]
                    
                    if len(cmdParts) == 4 and cmdParts[3]=="*":
                        csBar = True # counter will be actif on chip select = low
                        
                    cpt = UpDownCounter(None,args[0],int(args[1]),int(args[2]),int(args[3]),int(args[4]),name,csBar)
                    outputs.append(cpt)
                    
                elif parts[0] == "midiSender":
                    inputs.append(MidiSender())
                elif parts[0] == "asciiSender":
                    inputs.append(ASCIISender())
                elif parts[0] == "byteSender":
                    inputs.append(ByteSender())
                elif parts[0] == "uartReciever":
                    outputs.append(UARTReceiver())
                elif parts[0] == "uartReceiver":
                    outputs.append(UARTReceiver())
                elif parts[0] == "asciiReceiver":
                    outputs.append(ASCIIReceiver())
                elif parts[0] == "device":
                    devices.append(cmd)
                
                    
                
        return {"noDebug":noDebug,
                "debug":debug,
                "inputs":inputs,
                "outputs":outputs,
                "devices":devices,
                "varfilter":varfilter,
                "regfilter":regfilter,
                "options":options}

    
    
    
    