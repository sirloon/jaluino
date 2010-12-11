# -*- coding: utf-8 -*-
###############################################################################
# Name: jpk2cmd.py                                                            #
# Purpose: Jaluino PK2cmd Plugin main program                                 #
# Author: Carlo Dormeletti <carlo.dormeletti@email.it>                        #
# with consistent help of Sebastien Lelong <sebastien.lelong@gmail.com>       #
# Copyright: (c) 2010 Carlo Dormeletti <carlo.dormeletti@email.it>            #
# License: wxWindows License                                                  #
###############################################################################

"""PK2cmd JaluinoIDE jpk2cmd"""

__author__ = "Carlo Dormeletti"

#-----------------------------------------------------------------------------#
# Imports
import os, sys
import wx

#Editra imports
from ed_menu import EdMenuBar,EdMenu


# Globals
_ = wx.GetTranslation

#-----------------------------------------------------------------------------# 

ID_PK2PTARGET  = wx.NewId()
ID_PK2IDENTIFY = wx.NewId()
ID_PK2UPDATEFW = wx.NewId()
ID_PK2INFO = wx.NewId()
ID_PK2VER = wx.NewId()
ID_PK2SETTING  = wx.NewId()
ID_PK2PLUGINFO = wx.NewId()

def GetMenu(self):
    submenu = EdMenu()
    submenu.Append(ID_PK2PTARGET, _("Power the target"),
                   _("Power the target board attached to PicKit2"))
    submenu.Append(ID_PK2IDENTIFY, _("Identify"),
                   _("Identify the PIC attached to PicKit2"))
    submenu.AppendSeparator()  
    submenu.Append(ID_PK2VER, _("PK2cmd/PicKit2 Software Versions"),
                   _("View the software versions of PK2cmd,PicKit2 and PK2Dev "))  
    submenu.Append(ID_PK2INFO, _("Usage"),
                   _("View the usage help from pk2cmd commandline"))
    submenu.Append(ID_PK2UPDATEFW, _("Update Firmware"),
                   _("Updating the PicKit2 Firmware"))
    submenu.AppendSeparator()
    submenu.Append(ID_PK2SETTING, _("Settings"),
                   _("Configure Plugin"))
    submenu.AppendSeparator()
    submenu.Append(ID_PK2PLUGINFO, _("About"),
                   _("Get Information About Plugin"))                       
    return submenu
