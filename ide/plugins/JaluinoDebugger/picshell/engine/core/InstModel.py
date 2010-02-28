class InstModel:
    TYPE_BYTE = 1
    TYPE_BIT = 2
    TYPE_LITERAL = 3
    TYPE_A_BYTE = 4
    TYPE_DA_BYTE = 5
    TYPE_A_BIT = 6
    TYPE_LITERAL_20 = 7
    TYPE_LITERAL_S_20 = 8
    TYPE_LITERAL_FF_12 = 9
    
    def __init__ (self,  code, mnemonic, type, hasData=True):
        self.code = code;
        self.mnemonic = mnemonic;
        self.type = type;
        self.hasData = hasData;
        
    