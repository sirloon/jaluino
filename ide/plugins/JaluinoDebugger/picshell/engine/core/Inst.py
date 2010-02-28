class Inst:
    DEST_W = 0
    DEST_F = 1
    DEST_FSR_0 = 2
    DEST_FSR_1 = 3
    DEST_FSR_2 = 4
    DEST_NONE = 5
    
    ACCESS_RAM = 0
    ACCESS_BSR = 1
    ACCESS_NONE = 2
    def __init__(self):
        self.model = None
        self.value = 0
        self.bit = 0
        self.inv_bit = 255 # see Mnemonic.BCF which must be fast
        self.access = Inst.ACCESS_NONE
        self.dest = Inst.DEST_NONE  
        self.adresse = 0