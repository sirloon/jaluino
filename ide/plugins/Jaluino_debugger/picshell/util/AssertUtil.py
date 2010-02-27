from picshell.engine.util.Format import Format
class AssertUtil :
    
    @staticmethod
    def parse(lineCode, assertTag ):
        label=""
        var =""
        ref = ""

        # remove double spaces in order to increase parser rubustness
        while ( lineCode.find( "  " ) >= 0 ) :
            lineCode = lineCode.replace( "  ", " " ) 
        
        parts = lineCode.strip().split(assertTag)
        # print "PARTS"
        # print parts
        assertParts = parts[1].split(" ")
        ref = Format.toNumber(assertParts[1])
        label = assertParts[2]
        firstPart = parts[0].split("(")[1]
        var = firstPart.split(")")[0]

        label = label.strip()
        var = var.strip()

        # print "label " + label
        # print "var " + var
        # print "ref %02X" % ref
        
        
        return {"label":label,"var":var,"ref":ref}
        
    @staticmethod
    def GetAssertTag( lineCode ):
        assertTag = None

        if ( "@assertEquals" in lineCode ):
            assertTag = "@assertEquals"
        if ( "@assertLess" in lineCode ):
            assertTag = "@assertLess"
        if ( "@assertGreater" in lineCode ):
            assertTag = "@assertGreater"
        if ( "@assertNotEqual" in lineCode ):
            assertTag = "@assertNotEqual"
        return assertTag
      
    @staticmethod
    def Assert( assertTag, val, ref ):
         assertRes = False
         cmpStr = "??"
         
         if assertTag == "@assertEquals":
             assertRes = (ref == val)
             if assertRes:
                cmpStr = "=="
             else:
                cmpStr = "!="                                  
         if assertTag == "@assertLess":
             assertRes = (val < ref)
             if assertRes:
                cmpStr = "<"
             else:
                cmpStr = ">="                                  
         if assertTag == "@assertGreater":
             assertRes = (val > ref)
             if assertRes:
                cmpStr = ">"
             else:
                cmpStr = "<="                                  
         if assertTag == "@assertNotEqual":
             assertRes = (ref != val)
             if assertRes:
                cmpStr = "!="
             else:
                cmpStr = "=="                                  
         return [assertRes, cmpStr ]
        