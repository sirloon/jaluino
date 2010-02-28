def isSet( val,bitToTest):
    bitWeight = 1;
    bitWeight = bitWeight << bitToTest;
    return ((val&bitWeight)>0);
def isClear(val,bit):
    return not isSet(val,bit);
    