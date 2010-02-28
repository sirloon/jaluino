# -*- coding: utf-8 -*-
# Setup script to build the hello plugin. To build the plugin
# just run 'python setup.py bdist_egg'

""" The plugin is a JALUINO debugger plugin, based on the 
picshell implementation
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
            name='JaluinoDebugger',
            version='0.16',
            description=__doc__,
            author=__author__,
            author_email="jaluino@jaluino.org",
            license="wxWindows",
            url="http://editra.org",
            platforms=["Linux", "OS X", "Windows"],
            package_data = {'':['*.py']},

            packages = find_packages(),
            
            entry_points='''
            [Editra.plugins]
            JaluinoDebugger = JaluinoDebugger:Jaluino_debugger
            '''
        )
