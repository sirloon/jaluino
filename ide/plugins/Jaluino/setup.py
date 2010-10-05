# -*- coding: utf-8 -*-
# Setup script to build the Jaluino plugin. To build the plugin
# just run 'python setup.py bdist_egg' and an egg will be built and put into 
# the dist directory of this folder.
"""Jaluino IDE"""
__author__ = "Sebastien Lelong"

import sys
try:
    from setuptools import setup
except ImportError:
    print "You must have setup tools installed in order to build this plugin"
    setup = None

if setup != None:
    setup(
        name='Jaluino',
        version='0.2.2',
        description=__doc__,
        author=__author__,
        author_email="sebastien.lelong@gmail.com",
        license="wxWindows",
        url="http://jaluino.org",
        platforms=["Linux", "OS X", "Windows"],
        packages=['jaluino'],
        entry_points='''
        [Editra.plugins]
        Jaluino = jaluino:Jaluino
        '''
        )

