#
# State.globalWriteMonitors
#
class RegisterUpdater:
    def __init__(self,watchedReg):
        self.watchedReg = watchedReg
        
    def execute(self,address,value,state):
        #
        # Update registers shown in reg watch list
        #
        self.watchedReg.add(address)
       
       