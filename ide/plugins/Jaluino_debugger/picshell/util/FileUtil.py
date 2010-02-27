from picshell.ui.Context import Context
from wx.stc import STC_EOL_LF
from wx.stc import STC_EOL_CR
from wx.stc import STC_EOL_CRLF
import wx
import os
class FileUtil:
    #
    # read a lang file and return an array of lines
    #
    @staticmethod
    def open(fileExt="*.jal"):
        if Context.sourcepath == "":
            Context.sourcepath = os.getcwd()
        
        dlg = wx.FileDialog(Context.top,"Choose a file", Context.sourcepath, "", fileExt, wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            file = dlg.GetPath()
            dlg.Destroy()
            return file
        else:
            return ""

    @staticmethod
    def save(filename,content):
        if filename == "":
            dlg = wx.FileDialog(Context.top, "Choose a file", Context.sourcepath, "", "*.jal", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
            dlg.Destroy()
        if filename != "":  
            fileHandler = open(filename,"w")
            fileHandler.write(content)
            fileHandler.close()
        return filename
    
    @staticmethod
    def saveEditor(filename,editor):
        if filename == "":
            dlg = wx.FileDialog(Context.top, "Choose a file", Context.sourcepath, "", "*.jal", wx.SAVE)
            if dlg.ShowModal() == wx.ID_OK:
                filename = dlg.GetPath()
            dlg.Destroy()
        if filename != "":  
            editor.ConvertEOLs(STC_EOL_CRLF)
            editor.SaveFile(filename)
        return filename
    
    @staticmethod
    def getContentAsText(filename):
        file = open(filename)
        text = file.read()
        file.close()
        return text
    
        
    @staticmethod
    def expand_paths(libpath):
        """Expand paths """
        libpaths = libpath.split(";")
        libpath = None
        for lib in libpaths:
            lib_expanded = os.path.expandvars( os.path.expanduser( lib ) )
            if libpath != None:
                libpath = libpath + ";" + lib_expanded 
            else:
                libpath = lib_expanded
        return libpath
                
    @staticmethod
    def opj(path):
        """Convert paths to the platform-specific separator"""
        str = apply(os.path.join, tuple(path.split('/')))
        # HACK: on Linux, a leading / gets lost...
        if path.startswith('/'):
            str = '/' + str
        return str 