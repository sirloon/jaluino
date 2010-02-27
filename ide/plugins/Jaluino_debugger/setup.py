# -*- coding: utf-8 -*-
# Setup script to build the hello plugin. To build the plugin
# just run 'python setup.py bdist_egg'

""" The hello plugin is a very simple plugin implimenting the well
known hello world program for Editra. It does so by adding the
words "Hello World" to the View Menu. Which in turn opens a dialog
that says hello world again.

"""
__author__ = "Albert Faber"

import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None


if setup != None:
    setup(
            name='Jaluino_debugger',
            version='0.1',
            description=__doc__,
            author=__author__,
            author_email="jaluino@jaluino.org",
            license="wxWindows",
            url="http://editra.org",
            platforms=["Linux", "OS X", "Windows"],
            package_data = {'':['*.py']},
            #packages=['jaluino_debugger'],
            packages = find_packages(),
            
			#package_data = {'jaluino_debugger': ['jaluino_debugger/pichsell/*.py', 'pichsell/icons/*.*', 'jaluino_debugger/pichsell/engine/*.py', 'pichsell/engine/core/*.py', 'pichsell/engine/hex/*.py', 'pichsell/engine/util/*.py', 'pichsell/monitors/*.py', 'pichsell/parser/*.py', 'pichsell/ui/*.py', 'pichsell/ui/browser/*.py', 'pichsell/ui/config/*.py', 'pichsell/ui/debug/*.py', 'pichsell/ui/debug/comp/*.py', 'pichsell/ui/debug/plug/*.py', 'pichsell/ui/icons/*.*', 'pichsell/ui/edit/*.py', 'pichsell/ui/search/*.py', 'pichsell/ui/virtual/*.py']},
			# package_data = {'jaluino_debugger': ['pichsell/ui/*.py']},
			#{"script":"picshell/ui/PicShell.py","icon_resources": [(0, "icon.ico")]}],data_files=[("virtual",glob.glob("picshell\\ui\\virtual\\*.*")),("",glob.glob("*.txt")), ("icons",glob.glob("picshell\\ui\\icons\\*.*")), ("doc",glob.glob("..\\doc\\*.*")), ("doc\\img",glob.glob("..\\doc\\img\\*.*")), ("doc\\img\\dev",glob.glob("..\\doc\\img\\dev\\*.*")), ("doc\\img\\annotation",glob.glob("..\\doc\\img\\annotation\\*.*")), ("examples",glob.glob(".\\picshell\\examples\\*.jal")),("",glob.glob("picshell\\ui\\*.txt_no"))],options={"py2exe": {"packages":["picshell.ui.Context"]}})
            
            entry_points='''
            [Editra.plugins]
            Jaluino_debugger = jaluino_debugger:Jaluino_debugger
            '''
        )
