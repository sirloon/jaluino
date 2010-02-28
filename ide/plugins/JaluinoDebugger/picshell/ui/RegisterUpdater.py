#
# Global monitor
#
class RegisterUpdater:
    def __init__(self,watchedReg):
        self.watchedReg = watchedReg
        
    def execute(self,address,value,state):
        self.watchedReg.add(address)
     
    