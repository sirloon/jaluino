#
# Global monitor
#
# from JALsPy_globals import V_Node

# import JALsPy_globals



# State.globalWriteMonitors
# Update device state regarding to the Pic State
# only called if device is connected to at leat one output pin
#
class DeviceTargetStateMonitor:
    def __init__(self,uiManager):
        self.uiManager = uiManager
        
    def execute(self,address,value,state):
        
        #Update device
        devices = self.uiManager.devicesForAddressWrite[address] 
        if devices != None :
            #Update NetList
            nodesAndBits = self.uiManager.nodesForAddress[address] 
            if nodesAndBits != None :
                 for nodeAndBit in nodesAndBits :
                     node = nodeAndBit[0]
                     bit = nodeAndBit[1]
                     digitalVoltageAtBit = 0
                     if (value & bit)>0 :
                         digitalVoltageAtBit = 5
                     # JALsPy_globals.V_Node[node] = digitalVoltageAtBit
                
                 for device in devices :
                    device.Execute()
                        
# State.globalReadMonitors
# update Pic state regarding to a device
# only called if device is connected to at leat one input pin
#
class DeviceSourceStateMonitor:
    def __init__(self,uiManager):
        self.uiManager = uiManager
        
    def execute(self,address,state,value):
       devices = self.uiManager.devicesForAddressRead[address] 
       
       if devices != None :
           for device in devices :
               device.Execute()
               nodesAndBits = self.uiManager.nodesForAddress[address] 
               for nodeAndBit in nodesAndBits:
                   node = nodeAndBit[0]
                   bit = nodeAndBit[1]
                   nodeValue = device.V[1]
                   #nodeValue = JALsPy_globals.V_Node[node]
                   if (nodeValue == 5) :
                       value = value | bit
                   else: 
                       value = value & (255-bit)
       
       return value
