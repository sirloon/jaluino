from wx.lib import ogl
import wx
class MarkWindow(ogl.ShapeCanvas):
    def __init__(self, parent):
        ogl.ShapeCanvas.__init__(self, parent)
        #self.SetBackgroundColour("SILVER") #wx.WHITE)
        self.diagram = ogl.Diagram()
        self.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self)
        self.SetClientSizeWH(10,10)
        
        
        
        
        
        